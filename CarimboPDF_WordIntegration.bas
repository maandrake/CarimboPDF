Attribute VB_Name = "CarimboPDF_WordIntegration"
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' CarimboPDF - Integração com Microsoft Word VBA
' 
' Este módulo permite utilizar o CarimboPDF diretamente no Microsoft Word
' para adicionar carimbos de cidade e data em documentos PDF.
'
' Funcionalidades:
' - Exportar documento Word para PDF
' - Aplicar carimbo de data/cidade no PDF
' - Opções de formatação e proteção
' - Interface simples para uso em macros
'
' Autor: Marcos Despachante
' Versão: 1.0
' Data: Setembro 2025
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Option Explicit

' Constantes para configuração padrão
Private Const PYTHON_SCRIPT_PATH As String = "src\data_hora_pdf\cli.py"
Private Const DEFAULT_CITY As String = "São Paulo"
Private Const DEFAULT_FONT_SIZE As String = "12"
Private Const DEFAULT_COLOR As String = "#000000"

' Estrutura para opções de carimbo
Public Type CarimboOptions
    Cidade As String
    FonteSize As String
    Fonte As String
    Cor As String
    Negrito As Boolean
    Italico As Boolean
    Pagina As Long
    SenhaProtecao As String
    RestringirEdicao As Boolean
    DesativarCopia As Boolean
    CriptografarConteudo As Boolean
    CaminhoLogo As String
    LarguraLogoCm As String
    MargemLogoCm As String
End Type

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' Função principal para carimbar o documento ativo
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Public Function CarimbarDocumentoAtivo(Optional opcoes As CarimboOptions) As Boolean
    Dim docAtivo As Document
    Dim caminhoDocumento As String
    Dim caminhoPDF As String
    
    On Error GoTo ErrorHandler
    
    ' Verificar se há documento ativo
    Set docAtivo = ActiveDocument
    If docAtivo Is Nothing Then
        MsgBox "Nenhum documento ativo encontrado.", vbExclamation, "CarimboPDF"
        CarimbarDocumentoAtivo = False
        Exit Function
    End If
    
    ' Verificar se o documento foi salvo
    If docAtivo.Saved = False Or docAtivo.Path = "" Then
        MsgBox "Por favor, salve o documento antes de continuar.", vbInformation, "CarimboPDF"
        CarimbarDocumentoAtivo = False
        Exit Function
    End If
    
    caminhoDocumento = docAtivo.FullName
    caminhoPDF = Replace(caminhoDocumento, ".docx", ".pdf")
    caminhoPDF = Replace(caminhoPDF, ".doc", ".pdf")
    
    ' Exportar para PDF e aplicar carimbo
    CarimbarDocumentoAtivo = CarimbarDocumento(caminhoDocumento, caminhoPDF, opcoes)
    
    Exit Function
    
ErrorHandler:
    MsgBox "Erro ao carimbar documento: " & Err.Description, vbCritical, "CarimboPDF"
    CarimbarDocumentoAtivo = False
End Function

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' Função para carimbar um documento específico
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Public Function CarimbarDocumento(caminhoWord As String, caminhoPDF As String, Optional opcoes As CarimboOptions) As Boolean
    Dim doc As Document
    Dim resultado As Boolean
    
    On Error GoTo ErrorHandler
    
    ' Abrir documento se necessário
    If Dir(caminhoWord) = "" Then
        MsgBox "Arquivo não encontrado: " & caminhoWord, vbCritical, "CarimboPDF"
        CarimbarDocumento = False
        Exit Function
    End If
    
    ' Tentar abrir o documento
    Set doc = Documents.Open(caminhoWord, ReadOnly:=True)
    
    ' Exportar para PDF
    If Not ExportarParaPDF(doc, caminhoPDF) Then
        doc.Close SaveChanges:=False
        CarimbarDocumento = False
        Exit Function
    End If
    
    ' Fechar documento
    doc.Close SaveChanges:=False
    
    ' Aplicar carimbo no PDF
    resultado = AplicarCarimbo(caminhoPDF, opcoes)
    
    If resultado Then
        MsgBox "Documento carimbado com sucesso!" & vbCrLf & "Arquivo: " & caminhoPDF, vbInformation, "CarimboPDF"
    End If
    
    CarimbarDocumento = resultado
    
    Exit Function
    
ErrorHandler:
    If Not doc Is Nothing Then
        doc.Close SaveChanges:=False
    End If
    MsgBox "Erro ao processar documento: " & Err.Description, vbCritical, "CarimboPDF"
    CarimbarDocumento = False
End Function

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' Função para exportar documento Word para PDF
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Private Function ExportarParaPDF(doc As Document, caminhoPDF As String) As Boolean
    On Error GoTo ErrorHandler
    
    ' Exportar como PDF com qualidade otimizada
    doc.ExportAsFixedFormat _
        OutputFileName:=caminhoPDF, _
        ExportFormat:=wdExportFormatPDF, _
        OpenAfterExport:=False, _
        OptimizeFor:=wdExportOptimizeForQuality, _
        Range:=wdExportAllDocument, _
        Item:=wdExportDocumentContent, _
        IncludeDocProps:=True, _
        KeepIRM:=True, _
        CreateBookmarks:=wdExportCreateNoBookmarks, _
        DocStructureTags:=True, _
        BitmapMissingFonts:=True, _
        UseDocumentPrintingOrder:=True
    
    ExportarParaPDF = True
    Exit Function
    
ErrorHandler:
    MsgBox "Erro ao exportar para PDF: " & Err.Description, vbCritical, "CarimboPDF"
    ExportarParaPDF = False
End Function

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' Função para aplicar carimbo no PDF usando o script Python
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Private Function AplicarCarimbo(caminhoPDF As String, opcoes As CarimboOptions) As Boolean
    Dim comando As String
    Dim scriptPath As String
    Dim resultado As Long
    
    On Error GoTo ErrorHandler
    
    ' Verificar se o arquivo Python existe
    scriptPath = ObterCaminhoScript()
    If Dir(scriptPath) = "" Then
        MsgBox "Script Python não encontrado: " & scriptPath & vbCrLf & _
               "Certifique-se de que o CarimboPDF está instalado corretamente.", vbCritical, "CarimboPDF"
        AplicarCarimbo = False
        Exit Function
    End If
    
    ' Construir comando Python
    comando = ConstruirComandoPython(caminhoPDF, opcoes)
    
    ' Executar comando
    resultado = Shell(comando, vbHide)
    
    ' Aguardar um momento para o processamento
    Application.Wait (Now + TimeValue("0:00:02"))
    
    ' Verificar se o arquivo foi processado
    If Dir(caminhoPDF) <> "" Then
        AplicarCarimbo = True
    Else
        MsgBox "Falha ao processar o arquivo PDF.", vbCritical, "CarimboPDF"
        AplicarCarimbo = False
    End If
    
    Exit Function
    
ErrorHandler:
    MsgBox "Erro ao executar carimbo: " & Err.Description, vbCritical, "CarimboPDF"
    AplicarCarimbo = False
End Function

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' Função para construir o comando Python
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Private Function ConstruirComandoPython(caminhoPDF As String, opcoes As CarimboOptions) As String
    Dim comando As String
    Dim scriptPath As String
    
    scriptPath = ObterCaminhoScript()
    
    ' Comando base
    comando = "python """ & scriptPath & """ --input """ & caminhoPDF & """ --in-place"
    
    ' Adicionar cidade
    If opcoes.Cidade <> "" Then
        comando = comando & " --cidade """ & opcoes.Cidade & """"
    Else
        comando = comando & " --cidade """ & DEFAULT_CITY & """"
    End If
    
    ' Adicionar opções de formatação
    If opcoes.FonteSize <> "" Then
        comando = comando & " --font-size " & opcoes.FonteSize
    End If
    
    If opcoes.Fonte <> "" Then
        comando = comando & " --font """ & opcoes.Fonte & """"
    End If
    
    If opcoes.Cor <> "" Then
        comando = comando & " --color """ & opcoes.Cor & """"
    End If
    
    If opcoes.Negrito Then
        comando = comando & " --bold"
    End If
    
    If opcoes.Italico Then
        comando = comando & " --italic"
    End If
    
    If opcoes.Pagina > 0 Then
        comando = comando & " --page " & (opcoes.Pagina - 1) ' Converter para índice baseado em 0
    End If
    
    ' Adicionar opções de proteção
    If opcoes.SenhaProtecao <> "" Then
        comando = comando & " --protection-password """ & opcoes.SenhaProtecao & """"
    End If
    
    If opcoes.RestringirEdicao Then
        comando = comando & " --restrict-editing"
    End If
    
    If opcoes.DesativarCopia Then
        comando = comando & " --no-copy"
    End If
    
    If opcoes.CriptografarConteudo Then
        comando = comando & " --encrypt-content"
    End If
    
    ' Adicionar opções de logo
    If opcoes.CaminhoLogo <> "" Then
        comando = comando & " --logo-path """ & opcoes.CaminhoLogo & """"
    End If
    
    If opcoes.LarguraLogoCm <> "" Then
        comando = comando & " --logo-width-cm " & opcoes.LarguraLogoCm
    End If
    
    If opcoes.MargemLogoCm <> "" Then
        comando = comando & " --logo-margin-cm " & opcoes.MargemLogoCm
    End If
    
    ConstruirComandoPython = comando
End Function

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' Função para obter o caminho do script Python
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Private Function ObterCaminhoScript() As String
    Dim basePath As String
    Dim scriptPath As String
    
    ' Tentar encontrar o script em locais comuns
    basePath = ThisDocument.Path
    
    ' Verificar se está na mesma pasta do documento
    scriptPath = basePath & "\" & PYTHON_SCRIPT_PATH
    If Dir(scriptPath) <> "" Then
        ObterCaminhoScript = scriptPath
        Exit Function
    End If
    
    ' Verificar pasta pai
    scriptPath = Left(basePath, InStrRev(basePath, "\") - 1) & "\" & PYTHON_SCRIPT_PATH
    If Dir(scriptPath) <> "" Then
        ObterCaminhoScript = scriptPath
        Exit Function
    End If
    
    ' Verificar pasta de documentos do usuário
    scriptPath = Environ("USERPROFILE") & "\CarimboPDF\" & PYTHON_SCRIPT_PATH
    If Dir(scriptPath) <> "" Then
        ObterCaminhoScript = scriptPath
        Exit Function
    End If
    
    ' Retornar caminho padrão (pode não existir)
    ObterCaminhoScript = basePath & "\" & PYTHON_SCRIPT_PATH
End Function

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' Função auxiliar para criar opções padrão
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Public Function CriarOpcoesPadrao() As CarimboOptions
    Dim opcoes As CarimboOptions
    
    opcoes.Cidade = DEFAULT_CITY
    opcoes.FonteSize = DEFAULT_FONT_SIZE
    opcoes.Fonte = "helv"
    opcoes.Cor = DEFAULT_COLOR
    opcoes.Negrito = False
    opcoes.Italico = False
    opcoes.Pagina = 1
    opcoes.SenhaProtecao = ""
    opcoes.RestringirEdicao = False
    opcoes.DesativarCopia = False
    opcoes.CriptografarConteudo = False
    opcoes.CaminhoLogo = ""
    opcoes.LarguraLogoCm = "2.0"
    opcoes.MargemLogoCm = "0.5"
    
    CriarOpcoesPadrao = opcoes
End Function

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' Macro exemplo para uso simples
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Public Sub CarimbarDocumentoSimples()
    Dim opcoes As CarimboOptions
    
    ' Usar opções padrão
    opcoes = CriarOpcoesPadrao()
    
    ' Personalizar cidade se necessário
    ' opcoes.Cidade = "Rio de Janeiro"
    
    ' Carimbar documento ativo
    Call CarimbarDocumentoAtivo(opcoes)
End Sub

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' Macro exemplo com proteção
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Public Sub CarimbarDocumentoComProtecao()
    Dim opcoes As CarimboOptions
    Dim senha As String
    
    ' Solicitar senha ao usuário
    senha = InputBox("Digite a senha para proteção do PDF:", "Proteção CarimboPDF")
    If senha = "" Then Exit Sub
    
    ' Configurar opções com proteção
    opcoes = CriarOpcoesPadrao()
    opcoes.SenhaProtecao = senha
    opcoes.RestringirEdicao = True
    opcoes.DesativarCopia = True
    
    ' Carimbar documento ativo
    Call CarimbarDocumentoAtivo(opcoes)
End Sub

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' Macro exemplo com personalização completa
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Public Sub CarimbarDocumentoPersonalizado()
    Dim opcoes As CarimboOptions
    Dim cidade As String
    
    ' Solicitar cidade ao usuário
    cidade = InputBox("Digite a cidade para o carimbo:", "CarimboPDF", DEFAULT_CITY)
    If cidade = "" Then Exit Sub
    
    ' Configurar opções personalizadas
    opcoes = CriarOpcoesPadrao()
    opcoes.Cidade = cidade
    opcoes.FonteSize = "14"
    opcoes.Negrito = True
    opcoes.Cor = "#0000FF"  ' Azul
    
    ' Carimbar documento ativo
    Call CarimbarDocumentoAtivo(opcoes)
End Sub