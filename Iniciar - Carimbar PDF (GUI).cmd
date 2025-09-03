@echo off
set "PYTHONPATH=%~dp0src"
if exist "%~dp0.venv\Scripts\python.exe" (
  "%~dp0.venv\Scripts\python.exe" -m data_hora_pdf.cli --gui --in-place
) else (
  python -m data_hora_pdf.cli --gui --in-place
)
