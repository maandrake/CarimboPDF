Attribute VB_Name = "LoggingModule"
' ============================================================================
' LoggingModule.bas - Módulo de logging compatível com VBA Word
' ============================================================================
Option Explicit

' Enumeração para níveis de log
Public Enum LogLevel
    LogLevel_Info = 1
    LogLevel_Warning = 2
    LogLevel_Error = 3
    LogLevel_Debug = 4
End Enum

' Tipo personalizado para configuração de logging
Public Type LogConfig
    LogFilePath As String
    MaxFileSize As Long
    EnableConsoleOutput As Boolean
    MinimumLevel As LogLevel
End Type

' Variáveis globais do módulo
Private m_IsInitialized As Boolean
Private m_CurrentConfig As LogConfig
Private m_LogFileNumber As Integer

' ============================================================================
' Inicialização do sistema de logging
' ============================================================================
Public Function InitializeLogging(Optional ByRef customConfig As LogConfig) As Boolean
    On Error GoTo ErrorHandler
    
    ' Configuração padrão
    If VarPtr(customConfig.LogFilePath) = 0 Then
        m_CurrentConfig.LogFilePath = Environ("TEMP") & "\CarimboPDF_Log.txt"
        m_CurrentConfig.MaxFileSize = 1048576 ' 1MB
        m_CurrentConfig.EnableConsoleOutput = True
        m_CurrentConfig.MinimumLevel = LogLevel_Info
    Else
        m_CurrentConfig = customConfig
    End If
    
    ' Verificar se o diretório existe
    If Not FolderExists(GetFolderPath(m_CurrentConfig.LogFilePath)) Then
        MkDir GetFolderPath(m_CurrentConfig.LogFilePath)
    End If
    
    ' Obter número de arquivo livre
    m_LogFileNumber = FreeFile
    
    m_IsInitialized = True
    InitializeLogging = True
    
    ' Log inicial
    Call WriteLog(LogLevel_Info, "LoggingModule", "Sistema de logging inicializado", "Arquivo: " & m_CurrentConfig.LogFilePath)
    
    Exit Function
    
ErrorHandler:
    InitializeLogging = False
    m_IsInitialized = False
End Function

' ============================================================================
' Função principal para escrever logs
' ============================================================================
Public Sub WriteLog(ByVal level As LogLevel, ByVal moduleName As String, ByVal message As String, Optional ByVal details As String)
    On Error GoTo ErrorHandler
    
    If Not m_IsInitialized Then
        If Not InitializeLogging() Then
            Exit Sub
        End If
    End If
    
    ' Verificar se o nível é suficiente para log
    If level < m_CurrentConfig.MinimumLevel Then
        Exit Sub
    End If
    
    Dim logEntry As String
    Dim timestamp As String
    Dim levelText As String
    
    ' Formatar timestamp
    timestamp = Format(Now, "yyyy-mm-dd hh:nn:ss")
    
    ' Converter nível para texto
    Select Case level
        Case LogLevel_Info
            levelText = "INFO"
        Case LogLevel_Warning
            levelText = "WARN"
        Case LogLevel_Error
            levelText = "ERROR"
        Case LogLevel_Debug
            levelText = "DEBUG"
        Case Else
            levelText = "UNKNOWN"
    End Select
    
    ' Montar entrada do log
    logEntry = timestamp & " | " & levelText & " | " & moduleName & " | " & message
    If details <> "" Then
        logEntry = logEntry & " | Details: " & details
    End If
    
    ' Escrever no arquivo
    Call WriteToFile(logEntry)
    
    ' Escrever no console se habilitado
    If m_CurrentConfig.EnableConsoleOutput Then
        Debug.Print logEntry
    End If
    
    Exit Sub
    
ErrorHandler:
    ' Em caso de erro no logging, tentar escrever erro simples
    Debug.Print "ERRO NO LOGGING: " & Err.Description
End Sub

' ============================================================================
' Funções auxiliares específicas para cada nível de log
' ============================================================================
Public Sub LogInfo(ByVal moduleName As String, ByVal message As String, Optional ByVal details As String)
    Call WriteLog(LogLevel_Info, moduleName, message, details)
End Sub

Public Sub LogWarning(ByVal moduleName As String, ByVal message As String, Optional ByVal details As String)
    Call WriteLog(LogLevel_Warning, moduleName, message, details)
End Sub

Public Sub LogDebug(ByVal moduleName As String, ByVal message As String, Optional ByVal details As String)
    Call WriteLog(LogLevel_Debug, moduleName, message, details)
End Sub

' Função renomeada para evitar conflito com LogError
Public Sub LogErrorMessage(ByVal moduleName As String, ByVal message As String, Optional ByVal details As String)
    Call WriteLog(LogLevel_Error, moduleName, message, details)
End Sub

' ============================================================================
' Funções auxiliares privadas
' ============================================================================
Private Sub WriteToFile(ByVal logEntry As String)
    On Error GoTo ErrorHandler
    
    ' Verificar tamanho do arquivo
    If FileExists(m_CurrentConfig.LogFilePath) Then
        If FileLen(m_CurrentConfig.LogFilePath) > m_CurrentConfig.MaxFileSize Then
            Call RotateLogFile
        End If
    End If
    
    ' Escrever no arquivo
    Open m_CurrentConfig.LogFilePath For Append As #m_LogFileNumber
    Print #m_LogFileNumber, logEntry
    Close #m_LogFileNumber
    
    Exit Sub
    
ErrorHandler:
    ' Fechar arquivo em caso de erro
    On Error Resume Next
    Close #m_LogFileNumber
End Sub

Private Sub RotateLogFile()
    On Error Resume Next
    
    Dim backupPath As String
    backupPath = Replace(m_CurrentConfig.LogFilePath, ".txt", "_backup.txt")
    
    ' Remover backup antigo se existir
    If FileExists(backupPath) Then
        Kill backupPath
    End If
    
    ' Renomear arquivo atual para backup
    If FileExists(m_CurrentConfig.LogFilePath) Then
        Name m_CurrentConfig.LogFilePath As backupPath
    End If
End Sub

Private Function FileExists(ByVal filePath As String) As Boolean
    On Error Resume Next
    FileExists = (Dir(filePath) <> "")
End Function

Private Function FolderExists(ByVal folderPath As String) As Boolean
    On Error Resume Next
    FolderExists = (Dir(folderPath, vbDirectory) <> "")
End Function

Private Function GetFolderPath(ByVal filePath As String) As String
    Dim pos As Integer
    pos = InStrRev(filePath, "\")
    If pos > 0 Then
        GetFolderPath = Left(filePath, pos - 1)
    Else
        GetFolderPath = ""
    End If
End Function

' ============================================================================
' Função para finalizar o sistema de logging
' ============================================================================
Public Sub FinalizeLogging()
    On Error Resume Next
    
    If m_IsInitialized Then
        Call WriteLog(LogLevel_Info, "LoggingModule", "Sistema de logging finalizado")
        Close #m_LogFileNumber
        m_IsInitialized = False
    End If
End Sub

' ============================================================================
' Função para obter configuração atual
' ============================================================================
Public Function GetCurrentConfig() As LogConfig
    GetCurrentConfig = m_CurrentConfig
End Function

' ============================================================================
' Função para verificar se o logging está inicializado
' ============================================================================
Public Function IsLoggingInitialized() As Boolean
    IsLoggingInitialized = m_IsInitialized
End Function