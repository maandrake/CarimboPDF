# Guia Rápido: Limpeza de Pull Requests

## ❓ Pergunta Original
"Tem como excluir pull que foram fechados?"

## ✅ Resposta
**Não é possível excluir PRs no GitHub**, mas você pode limpar os branches associados!

## 🚀 Uso Rápido

### Para Windows:
```cmd
scripts\Limpeza_Branches_PRs.cmd
```

### Para Linux/Mac:
```bash
python scripts/cleanup_closed_pr_branches.py
```

## 🎯 O que o script faz:
- ✅ Identifica branches de PRs fechados (copilot/, feature/, fix/, etc.)
- ✅ Remove branches locais e remotos desnecessários
- ❌ **NÃO remove os PRs** (impossível no GitHub)
- ✅ Mantém histórico completo do projeto

## 📋 Lembrete
PRs fechados continuam visíveis em:
https://github.com/maandrake/CarimboPDF/pulls?q=is:pr+is:closed

**Isso é normal e esperado!** 🎯

Para detalhes completos, veja: [`GERENCIAMENTO_PRS.md`](GERENCIAMENTO_PRS.md)