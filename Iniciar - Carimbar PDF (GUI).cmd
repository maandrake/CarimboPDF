@echo off
setlocal
set "APP_ROOT=%~dp0"
pushd "%APP_ROOT%" || exit /b 1
set "APP_PYTHON=%APP_ROOT%.venv\Scripts\python.exe"
if exist "%APP_PYTHON%" goto check_dependencies

where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m venv "%APP_ROOT%.venv" || goto failed
) else (
    where python >nul 2>nul
    if errorlevel 1 goto missing_python
    python -m venv "%APP_ROOT%.venv" || goto failed
)

:check_dependencies
"%APP_PYTHON%" -c "import sys; assert sys.version_info >= (3,10); import pymupdf, PIL, tkcalendar, data_hora_pdf; from importlib.metadata import version; assert version('carimbopdf') == '3.0.0'" >nul 2>nul
if errorlevel 1 (
    "%APP_PYTHON%" -m pip install -e "%APP_ROOT%." || goto failed
)
if exist "%APP_ROOT%.venv\Scripts\pythonw.exe" (
    start "CarimboPDF" "%APP_ROOT%.venv\Scripts\pythonw.exe" "%APP_ROOT%CarimboPDF_GUI.pyw"
) else (
    "%APP_PYTHON%" "%APP_ROOT%CarimboPDF_GUI.pyw"
)
popd
exit /b 0

:missing_python
echo Python 3.10 ou superior nao encontrado. Instale em https://www.python.org/downloads/
goto failure_exit

:failed
echo Falha ao preparar o CarimboPDF. Verifique o Python e a conexao com a internet.
:failure_exit
pause
popd
exit /b 1
