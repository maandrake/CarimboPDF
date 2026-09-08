# Executável Windows

Instale Python 3.10+ com Tcl/Tk e execute na raiz do repositório:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m PyInstaller --clean --noconfirm CarimboPDF.spec
```

O resultado fica em `dist/CarimboPDF.exe`. O logo é embutido e a aplicação usa
`multiprocessing.freeze_support()` para processar PDFs fora da interface.

Os binários históricos já presentes no repositório não representam necessariamente
o código atual. Gere novamente antes de distribuir. Novos arquivos de build, logs
e executáveis são ignorados pelo Git; publique versões compiladas em Releases.

O atalho CMD instala o pacote na primeira execução e verifica as dependências antes
de abrir a interface com `pythonw.exe`. Para atualizar um ambiente antigo:

```powershell
.venv\Scripts\python -m pip install --upgrade -e .
```

Consulte o README para uso, proteção e migração das preferências.
