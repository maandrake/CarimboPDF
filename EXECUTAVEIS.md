# Executável Windows

Instale Python 3.10+ com Tcl/Tk e execute na raiz do repositório:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m PyInstaller --clean --noconfirm CarimboPDF.spec
```

O resultado fica em `dist/CarimboPDF.exe`. O logo é embutido e a aplicação usa
`multiprocessing.freeze_support()` para processar PDFs fora da interface.

O arquivo versionado `dist/CarimboPDF.exe` foi atualizado com a refatoração e a
correção do ícone da janela (código de origem: `bf70cec`, integrado pelo PR #10).
Ele inclui o ícone no cabeçalho da interface e no executável Windows.
Após novas alterações no código, gere novamente o executável antes de distribuir.
Arquivos intermediários de build e logs não são necessários para executar o programa.

O atalho CMD instala o pacote na primeira execução e verifica as dependências antes
de abrir a interface com `pythonw.exe`. Para atualizar um ambiente antigo:

```powershell
.venv\Scripts\python -m pip install --upgrade -e .
```

Consulte o README para uso, proteção e migração das preferências.
