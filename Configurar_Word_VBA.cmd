@echo off
REM ===================================================================================
REM CarimboPDF - Script de configuração para integração com Word VBA
REM 
REM Este script facilita a configuração do CarimboPDF para uso com Microsoft Word VBA
REM 
REM Uso: Executar como administrador para configuração do sistema
REM ===================================================================================

echo ================================================
echo    CarimboPDF - Configuração para Word VBA
echo ================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não está instalado ou não está no PATH
    echo Por favor, instale Python 3.8+ e adicione ao PATH
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python encontrado
python --version

REM Verificar se pip está disponível
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: pip não está disponível
    echo Por favor, reinstale Python com pip incluído
    pause
    exit /b 1
)

echo ✓ pip encontrado
echo.

REM Instalar dependências Python
echo Instalando dependências do CarimboPDF...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependências
    pause
    exit /b 1
)

echo ✓ Dependências instaladas com sucesso
echo.

REM Testar funcionalidade básica
echo Testando funcionalidade básica...
python scripts\make_dummy_pdf.py
if errorlevel 1 (
    echo ERRO: Falha ao criar PDF de teste
    pause
    exit /b 1
)

echo ✓ PDF de teste criado
echo.

REM Testar carimbo
set PYTHONPATH=%CD%\src
python -m data_hora_pdf.cli --input dummy.pdf --output dummy_teste_vba.pdf --cidade "São Paulo"
if errorlevel 1 (
    echo ERRO: Falha ao testar carimbo
    pause
    exit /b 1
)

echo ✓ Teste de carimbo concluído com sucesso
echo.

REM Criar pasta de documentos do usuário se não existir
if not exist "%USERPROFILE%\CarimboPDF" (
    mkdir "%USERPROFILE%\CarimboPDF"
)

REM Copiar arquivos necessários para pasta do usuário
copy /Y src\data_hora_pdf\*.py "%USERPROFILE%\CarimboPDF\" >nul 2>&1
copy /Y CarimboPDF_WordIntegration.bas "%USERPROFILE%\CarimboPDF\" >nul 2>&1
copy /Y requirements.txt "%USERPROFILE%\CarimboPDF\" >nul 2>&1

echo ✓ Arquivos copiados para %USERPROFILE%\CarimboPDF\
echo.

echo ================================================
echo     Configuração concluída com sucesso!
echo ================================================
echo.
echo PRÓXIMOS PASSOS:
echo.
echo 1. Abra Microsoft Word
echo 2. Pressione Alt+F11 para abrir o Editor VBA
echo 3. No menu, clique em "Arquivo" > "Importar Arquivo..."
echo 4. Selecione o arquivo: %USERPROFILE%\CarimboPDF\CarimboPDF_WordIntegration.bas
echo 5. O módulo será adicionado ao seu projeto VBA
echo.
echo EXEMPLO DE USO:
echo - Para carimbo simples: execute a macro "CarimbarDocumentoSimples"
echo - Para carimbo com proteção: execute "CarimbarDocumentoComProtecao"
echo - Para carimbo personalizado: execute "CarimbarDocumentoPersonalizado"
echo.
echo DOCUMENTAÇÃO:
echo - Consulte o arquivo README.md para mais informações
echo - Exemplos de código estão no arquivo .bas importado
echo.
echo Pressione qualquer tecla para continuar...
pause >nul