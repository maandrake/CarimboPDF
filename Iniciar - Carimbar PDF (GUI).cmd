@echo off
setlocal
set "ROOT=%~dp0"
set "PYTHONPATH=%ROOT%src"
if exist "%ROOT%.venv\Scripts\pythonw.exe" (
    set "PYBIN=%ROOT%.venv\Scripts\pythonw.exe"
) else if exist "%ROOT%.venv\Scripts\python.exe" (
    set "PYBIN=%ROOT%.venv\Scripts\python.exe"
) else (
    set "PYBIN=pythonw"
)
start "CarimboPDF" "%PYBIN%" "%ROOT%CarimboPDF_GUI.pyw"
exit /b
