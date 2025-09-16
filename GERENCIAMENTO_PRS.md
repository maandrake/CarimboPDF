# Gerenciamento de Pull Requests - CarimboPDF

## ❓ Pergunta: "Tem como excluir pull que foram fechados?"

### 📋 Resposta Rápida
**NÃO**, GitHub não permite excluir Pull Requests. Isso é uma limitação/recurso intencional do GitHub para preservar o histórico do projeto e auditoria.

### 🔍 O que você PODE fazer:

## 1. 🧹 Limpar Branches de PRs Fechados

### Para Windows (Fácil):
```cmd
# Execute o arquivo de lote incluído:
scripts\Limpeza_Branches_PRs.cmd
```

### Para qualquer sistema (Manual):
```bash
# Execute o script Python:
python scripts/cleanup_closed_pr_branches.py
```

### ⚠️ O que o script faz:
- ✅ **Deleta branches locais** de PRs fechados
- ✅ **Deleta branches remotos** de PRs fechados  
- ❌ **NÃO deleta os PRs** (impossível no GitHub)
- ✅ **Mantém histórico** dos PRs no GitHub

---

## 2. 📊 Visualizar PRs Fechados

### No GitHub Web:
```
🔗 PRs Fechados: 
https://github.com/maandrake/CarimboPDF/pulls?q=is:pr+is:closed

🔗 PRs Merged: 
https://github.com/maandrake/CarimboPDF/pulls?q=is:pr+is:merged

🔗 Todos os PRs:
https://github.com/maandrake/CarimboPDF/pulls?q=is:pr
```

### Via linha de comando (GitHub CLI):
```bash
# Instalar GitHub CLI primeiro: https://cli.github.com
gh pr list --state closed
gh pr list --state merged
gh pr list --state all
```

---

## 3. 🎯 Estados dos PRs

| Estado | Descrição | Visível no GitHub? | Branch pode ser deletado? |
|--------|-----------|-------------------|---------------------------|
| **Open** | PR aberto/ativo | ✅ Sim | ❌ Não (ainda em uso) |
| **Closed** | PR fechado sem merge | ✅ Sim (sempre) | ✅ Sim |
| **Merged** | PR aceito e merged | ✅ Sim (sempre) | ✅ Sim |

---

## 4. 🔧 Limpeza Manual Avançada

### Listar branches de PRs fechados:
```bash
# Ver branches remotos
git branch -r | grep -E "(copilot/|feature/|fix/|pr/)"

# Ver branches locais  
git branch | grep -E "(copilot/|feature/|fix/|pr/)"
```

### Deletar branch específico:
```bash
# Branch local
git branch -d nome-do-branch

# Branch remoto
git push origin --delete nome-do-branch
```

### Limpeza em lote (cuidado!):
```bash
# Deletar todos os branches copilot/ locais
git branch | grep "copilot/" | xargs git branch -D

# Deletar todos os branches copilot/ remotos
git branch -r | grep "origin/copilot/" | sed 's/origin\///' | xargs -I {} git push origin --delete {}
```

---

## 5. 🛡️ Boas Práticas

### ✅ FAÇA:
- **Mantenha branches organizados** com nomes descritivos
- **Delete branches** após PR ser merged/fechado
- **Use o script de limpeza** regularmente
- **Documente PRs importantes** antes de fechar

### ❌ NÃO FAÇA:
- **Não tente "deletar" PRs** (impossível)
- **Não delete branch main/master** nunca
- **Não delete branches** de PRs ainda abertos
- **Não force push** em branches compartilhados

---

## 6. 💡 Por que GitHub preserva PRs?

### Motivos técnicos:
- **📚 Histórico completo** de mudanças
- **🔍 Auditoria** e compliance
- **🔗 Referências** entre issues/PRs/commits
- **📝 Discussões técnicas** preservadas
- **🔄 Possibilidade de reabrir** PRs fechados

### Benefícios:
- Rastreabilidade completa do código
- Facilita revisões de código futuras
- Mantém contexto de decisões técnicas
- Permite análise de padrões de desenvolvimento

---

## 7. 🚀 Automatização

### Script incluído:
O script `cleanup_closed_pr_branches.py` automatiza:

1. **Identificação** de branches de PR
2. **Verificação** de status (merged/fechado)
3. **Limpeza segura** de branches
4. **Relatório** de ações executadas

### Agendamento automático:
```bash
# Adicionar ao crontab (Linux/Mac) para limpeza semanal:
0 0 * * 0 cd /path/to/CarimboPDF && python scripts/cleanup_closed_pr_branches.py
```

---

## 8. 📞 Suporte

### Se encontrar problemas:
1. **Verifique permissões** no repositório
2. **Confirme conectividade** com GitHub
3. **Execute** `git fetch --prune` primeiro
4. **Tente limpeza manual** se script falhar

### Comandos de diagnóstico:
```bash
# Verificar status do repositório
git status
git remote -v
git branch -a

# Verificar conectividade
git ls-remote origin

# Atualizar referências
git fetch --prune
```

---

## ✨ Resumo

- ❌ **GitHub NÃO permite excluir PRs** (por design)
- ✅ **Você PODE limpar branches** associados a PRs fechados
- 🛠️ **Use o script incluído** para automatizar limpeza
- 📚 **PRs fechados permanecem visíveis** no histórico (isso é bom!)
- 🧹 **Limpeza regular** mantém repositório organizado

> **Dica:** Aceite que PRs fechados ficam visíveis - isso é uma funcionalidade, não um bug! 🎯