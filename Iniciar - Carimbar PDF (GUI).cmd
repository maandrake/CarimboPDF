@echo off
set "PYTHONPATH=%~dp0src"
if exist "%~dp0.venv\Scripts\pythonw.exe" (
  "%~dp0.venv\Scripts\pythonw.exe" "%~dp0CarimboPDF_GUI.pyw"
) else if exist "%~dp0.venv\Scripts\python.exe" (
  "%~dp0.venv\Scripts\python.exe" "%~dp0CarimboPDF_GUI.pyw"
) else (
  pythonw "%~dp0CarimboPDF_GUI.pyw"
)
