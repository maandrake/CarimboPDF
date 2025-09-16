#!/usr/bin/env python3
"""
Teste básico para o script de limpeza de branches.
"""

import sys
import subprocess
from pathlib import Path

def test_script_runs():
    """Testa se o script executa sem erros críticos."""
    script_path = Path(__file__).parent / "cleanup_closed_pr_branches.py"
    
    # Simular entrada "n" para cancelar operação
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input="n\n",
            text=True,
            capture_output=True,
            timeout=30
        )
        
        # Script deve terminar com sucesso (usuário cancelou)
        if result.returncode == 0:
            print("✅ Script executou corretamente")
            return True
        else:
            print(f"❌ Script falhou: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Script demorou muito para executar")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar script: {e}")
        return False

def test_git_repository():
    """Verifica se estamos em um repositório Git válido."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Repositório Git válido")
            return True
        else:
            print("❌ Não é um repositório Git válido")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar Git: {e}")
        return False

def main():
    """Executa os testes."""
    print("🧪 Testando funcionalidade de limpeza de branches")
    print("=" * 50)
    
    tests = [
        ("Verificação do repositório Git", test_git_repository),
        ("Execução do script de limpeza", test_script_runs),
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n🔍 {name}...")
        if test_func():
            passed += 1
    
    print(f"\n📊 Resultados: {passed}/{len(tests)} testes passaram")
    
    if passed == len(tests):
        print("🎉 Todos os testes passaram!")
        return 0
    else:
        print("⚠️  Alguns testes falharam")
        return 1

if __name__ == "__main__":
    sys.exit(main())