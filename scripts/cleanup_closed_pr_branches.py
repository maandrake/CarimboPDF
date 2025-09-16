#!/usr/bin/env python3
"""
Script para limpar branches de Pull Requests que foram fechados ou merged.

GitHub não permite excluir pull requests, mas podemos limpar os branches
associados para manter o repositório organizado.

IMPORTANTE: GitHub preserva o histórico de PRs por motivos de auditoria,
então PRs fechados permanecem visíveis na interface web.
"""

import subprocess
import sys
import json
from typing import List, Dict, Any


def run_command(cmd: str) -> tuple[int, str, str]:
    """Executa um comando e retorna código de saída, stdout e stderr."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Timeout: Comando demorou mais de 30 segundos"
    except Exception as e:
        return 1, "", f"Erro ao executar comando: {e}"


def get_remote_branches() -> List[str]:
    """Obtém lista de branches remotos."""
    code, stdout, stderr = run_command("git branch -r")
    if code != 0:
        print(f"Erro ao obter branches remotos: {stderr}")
        return []
    
    branches = []
    for line in stdout.split('\n'):
        line = line.strip()
        if line and not line.startswith('origin/HEAD'):
            # Remove 'origin/' prefix
            branch = line.replace('origin/', '')
            branches.append(branch)
    
    return branches


def get_local_branches() -> List[str]:
    """Obtém lista de branches locais."""
    code, stdout, stderr = run_command("git branch")
    if code != 0:
        print(f"Erro ao obter branches locais: {stderr}")
        return []
    
    branches = []
    for line in stdout.split('\n'):
        line = line.strip()
        if line and not line.startswith('*'):
            branches.append(line)
        elif line.startswith('* '):
            # Branch atual
            branches.append(line[2:])
    
    return branches


def get_current_branch() -> str:
    """Obtém o branch atual."""
    code, stdout, stderr = run_command("git branch --show-current")
    if code != 0:
        print(f"Erro ao obter branch atual: {stderr}")
        return "main"
    return stdout or "main"


def is_branch_merged(branch: str, target_branch: str = None) -> bool:
    """Verifica se um branch foi merged no branch principal."""
    if target_branch is None:
        # Tentar detectar branch principal automaticamente
        code, stdout, _ = run_command("git symbolic-ref refs/remotes/origin/HEAD")
        if code == 0:
            target_branch = stdout.replace('refs/remotes/origin/', '')
        else:
            target_branch = "main"  # fallback
    
    code, stdout, stderr = run_command(f"git merge-base --is-ancestor {branch} {target_branch}")
    return code == 0


def delete_local_branch(branch: str, force: bool = False) -> bool:
    """Deleta um branch local."""
    flag = "-D" if force else "-d"
    code, stdout, stderr = run_command(f"git branch {flag} {branch}")
    if code == 0:
        print(f"✅ Branch local '{branch}' deletado com sucesso")
        return True
    else:
        print(f"❌ Erro ao deletar branch local '{branch}': {stderr}")
        return False


def delete_remote_branch(branch: str) -> bool:
    """Deleta um branch remoto."""
    code, stdout, stderr = run_command(f"git push origin --delete {branch}")
    if code == 0:
        print(f"✅ Branch remoto '{branch}' deletado com sucesso")
        return True
    else:
        print(f"❌ Erro ao deletar branch remoto '{branch}': {stderr}")
        return False


def identify_pr_branches(branches: List[str]) -> List[str]:
    """Identifica branches que provavelmente são de PRs (copilot/, feature/, fix/, etc.)."""
    pr_patterns = [
        "copilot/",
        "feature/",
        "fix/",
        "bugfix/",
        "hotfix/",
        "develop/",
        "pr/",
        "pull/",
        "merge/"
    ]
    
    pr_branches = []
    for branch in branches:
        if any(branch.startswith(pattern) for pattern in pr_patterns):
            pr_branches.append(branch)
    
    return pr_branches


def main():
    """Função principal do script."""
    print("🧹 Script de Limpeza de Branches de PRs Fechados")
    print("=" * 50)
    
    # Verificar se estamos em um repositório Git
    code, _, _ = run_command("git rev-parse --is-inside-work-tree")
    if code != 0:
        print("❌ Este diretório não é um repositório Git válido")
        sys.exit(1)
    
    # Obter branch atual
    current_branch = get_current_branch()
    print(f"📍 Branch atual: {current_branch}")
    
    # Definir branch principal (main ou master)
    main_branch = "main"
    
    # Verificar se main existe localmente, senão buscar do remoto
    code, _, _ = run_command("git show-ref --verify --quiet refs/heads/main")
    if code != 0:
        print("📥 Branch 'main' não encontrado localmente, buscando do remoto...")
        code, _, stderr = run_command("git fetch origin main:main")
        if code != 0:
            print(f"❌ Erro ao buscar branch 'main': {stderr}")
            print("💡 Verifique se o repositório tem um branch 'main' no remoto")
            # Tentar com master como fallback
            code, _, _ = run_command("git fetch origin master:master")
            if code == 0:
                print("📥 Usando 'master' como branch principal")
                main_branch = "master"
            else:
                print("❌ Não foi possível encontrar branch principal")
                sys.exit(1)
        else:
            main_branch = "main"
    else:
        main_branch = "main"
    
    # Mudar para main se estivermos em um branch de PR
    if current_branch != main_branch and identify_pr_branches([current_branch]):
        print(f"🔄 Mudando para branch '{main_branch}' (estava em '{current_branch}')")
        code, _, stderr = run_command(f"git checkout {main_branch}")
        if code != 0:
            print(f"❌ Erro ao mudar para {main_branch}: {stderr}")
            print(f"💡 Tente executar: git checkout {main_branch}")
            print("⚠️  Continuando sem mudar de branch...")
            main_branch = current_branch
    
    # Atualizar referências remotas
    print("🔄 Atualizando referências remotas...")
    run_command("git fetch --prune")
    
    # Obter branches
    print("📋 Analisando branches...")
    local_branches = get_local_branches()
    remote_branches = get_remote_branches()
    
    # Identificar branches de PR
    local_pr_branches = identify_pr_branches(local_branches)
    remote_pr_branches = identify_pr_branches(remote_branches)
    
    print(f"🔍 Encontrados {len(local_pr_branches)} branches locais de PR")
    print(f"🔍 Encontrados {len(remote_pr_branches)} branches remotos de PR")
    
    if not local_pr_branches and not remote_pr_branches:
        print("✨ Nenhum branch de PR encontrado para limpeza!")
        return
    
    # Mostrar branches encontrados
    if local_pr_branches:
        print("\n📍 Branches locais de PR encontrados:")
        for branch in local_pr_branches:
            print(f"  - {branch}")
    
    if remote_pr_branches:
        print("\n🌐 Branches remotos de PR encontrados:")
        for branch in remote_pr_branches:
            print(f"  - {branch}")
    
    # Confirmar ação
    print("\n⚠️  ATENÇÃO: Esta ação irá deletar os branches listados acima!")
    print("📝 IMPORTANTE: PRs fechados ainda estarão visíveis no GitHub (isso é normal)")
    print("🔒 GitHub preserva o histórico de PRs por motivos de auditoria")
    
    response = input("\n❓ Continuar com a limpeza? [s/N]: ").lower().strip()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("🚫 Operação cancelada pelo usuário")
        return
    
    # Deletar branches locais
    local_deleted = 0
    for branch in local_pr_branches:
        if branch != current_branch:  # Não deletar o branch atual
            if delete_local_branch(branch, force=True):
                local_deleted += 1
    
    # Deletar branches remotos
    remote_deleted = 0
    for branch in remote_pr_branches:
        if branch != main_branch:  # Nunca deletar main/master
            if delete_remote_branch(branch):
                remote_deleted += 1
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DA LIMPEZA:")
    print(f"✅ Branches locais deletados: {local_deleted}/{len(local_pr_branches)}")
    print(f"✅ Branches remotos deletados: {remote_deleted}/{len(remote_pr_branches)}")
    
    if local_deleted > 0 or remote_deleted > 0:
        print("\n🎉 Limpeza concluída com sucesso!")
        print("💡 Lembre-se: PRs fechados ainda são visíveis no GitHub")
        print("🔗 Acesse: https://github.com/maandrake/CarimboPDF/pulls?q=is%3Apr+is%3Aclosed")
    else:
        print("\n⚠️  Nenhum branch foi deletado. Verifique permissões ou conectividade")


if __name__ == "__main__":
    main()