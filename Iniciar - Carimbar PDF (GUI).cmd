@echo off
setlocal
set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"
set "PYTHONW=%VENV%\Scripts\pythonw.exe"
set "PYTHON=%VENV%\Scripts\python.exe"

rem --- 1) já existe venv? então usa ---
if exist "%PYTHONW%" goto run_gui
if exist "%PYTHON%"  goto run_gui_py

rem --- 2) procurar um Python no sistema ---
call :find_python
if not defined SYS_PYTHON goto need_python

rem --- 3) criar venv se não existir ---
if not exist "%VENV%" (
    for %%# in ("%SYS_PYTHON%") do (
        if /i "%%~nx#"=="py.exe" (
            py -3 -m venv "%VENV%" || goto venv_failed
        ) else (
            "%%~f#" -m venv "%VENV%" || goto venv_failed
        )
    )
)

rem --- 4) garantir dependências ---
"%PYTHON%" -m pip install -r "%ROOT%requirements.txt" || goto pip_failed

:run_gui
rem --- procurar primeiro no perfil atual (evita capturar caminhos de outro usuario) ---
for %%D in ("%LocalAppData%\Programs\Python" "%UserProfile%\AppData\Local\Programs\Python") do (
    if exist %%D (
        for /d %%V in (%%D\Python3*) do (
            call :choose_python "%%V\python.exe"
            if defined SYS_PYTHON goto :eof
        )
    )
)

rem --- depois buscar no PATH ---
for %%P in (pythonw.exe python.exe py.exe) do (
    for /f "delims=" %%I in ('where %%P 2^>nul') do (
        call :choose_python "%%I"
        if defined SYS_PYTHON goto :eof
    )
)

rem --- usar Python Launcher para localizar instalações de qualquer usuário ---
for /f "delims=" %%I in ('py -0p 2^>nul') do (
    call :choose_python "%%I"
    if defined SYS_PYTHON goto :eof
)

rem --- por fim, procura em pastas de sistema comuns ---
for %%D in ("%ProgramFiles%\Python" "%ProgramFiles(x86)%\Python") do (
    if exist %%D (
        for /d %%V in (%%D\Python3*) do (
            call :choose_python "%%V\python.exe"
            if defined SYS_PYTHON goto :eof
        )
    )
)

rem --- procurar em locais comuns se não estiver no PATH ---
for %%D in ("%LocalAppData%\Programs\Python" "%UserProfile%\AppData\Local\Programs\Python" "%ProgramFiles%\Python" "%ProgramFiles(x86)%\Python") do (
    if exist %%D (
        for /d %%V in (%%D\Python3*) do (
            call :choose_python "%%V\python.exe"
            if defined SYS_PYTHON goto :eof
        )
    )
)
goto :eof

:choose_python
set "CANDIDATE=%~1"
set "CANDIDATE_DIR=%~dp1"
if exist "%CANDIDATE_DIR%pythonw.exe" (
    set "SYS_PYTHON=%CANDIDATE_DIR%pythonw.exe"
    exit /b
)
if exist "%CANDIDATE%" (
    set "SYS_PYTHON=%CANDIDATE%"
)
exit /b

:need_python
echo.
echo [CarimboPDF] Python 3.10+ não encontrado neste computador.
echo Instale o Python em https://www.python.org/downloads/ (marque "Add Python to PATH") e reabra este atalho.
echo Dica: sempre abra via "Iniciar - Carimbar PDF (GUI).cmd" (duplo clique) e não diretamente o arquivo .pyw.
pause
exit /b 1

:venv_failed
echo.
echo [CarimboPDF] Falha ao criar ambiente virtual (.venv).
pause
exit /b 1

:pip_failed
echo.
echo [CarimboPDF] Falha ao instalar dependencias. Verifique a conexão e tente novamente:
echo    "%PYTHON%" -m pip install -r "%ROOT%requirements.txt"
pause
exit /b 1
