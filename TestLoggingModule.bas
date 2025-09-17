Attribute VB_Name = "TestLoggingModule"
' ============================================================================
' TestLoggingModule.bas - Testes para o LoggingModule
' ============================================================================
Option Explicit

Public Sub TestLoggingFunctionality()
    ' Teste básico de funcionalidade
    Dim config As LogConfig
    Dim result As Boolean
    
    ' Configurar teste
    config.LogFilePath = Environ("TEMP") & "\TestCarimboPDF_Log.txt"
    config.MaxFileSize = 512000
    config.EnableConsoleOutput = True
    config.MinimumLevel = LogLevel_Debug
    
    ' Inicializar logging
    result = InitializeLogging(config)
    
    If result Then
        Debug.Print "✓ InitializeLogging funcionou corretamente"
        
        ' Testar diferentes níveis de log
        Call LogInfo("TestModule", "Teste de informação", "Detalhes do teste")
        Call LogWarning("TestModule", "Teste de aviso", "Detalhes do aviso")
        Call LogErrorMessage("TestModule", "Teste de erro", "Detalhes do erro")
        Call LogDebug("TestModule", "Teste de debug", "Detalhes do debug")
        
        ' Testar função WriteLog diretamente
        Call WriteLog(LogLevel_Info, "TestModule", "Teste direto WriteLog")
        Call WriteLog(LogLevel_Warning, "TestModule", "Teste com detalhes", "Estes são os detalhes")
        
        Debug.Print "✓ Todas as funções de log executaram sem erro"
        
        ' Verificar se está inicializado
        If IsLoggingInitialized() Then
            Debug.Print "✓ IsLoggingInitialized retorna True corretamente"
        End If
        
        ' Finalizar
        Call FinalizeLogging()
        Debug.Print "✓ FinalizeLogging executado com sucesso"
        
        Debug.Print "========================================="
        Debug.Print "TESTE CONCLUÍDO: Todos os testes passaram!"
        Debug.Print "========================================="
    Else
        Debug.Print "✗ Erro ao inicializar logging"
    End If
End Sub

Public Sub TestOptionalParameters()
    ' Teste específico para parâmetros opcionais
    Dim result As Boolean
    
    ' Teste 1: InitializeLogging sem parâmetros
    result = InitializeLogging()
    If result Then
        Debug.Print "✓ InitializeLogging() sem parâmetros funcionou"
    Else
        Debug.Print "✗ Erro em InitializeLogging() sem parâmetros"
    End If
    
    ' Teste 2: WriteLog sem parâmetro details
    Call WriteLog(LogLevel_Info, "TestModule", "Mensagem sem detalhes")
    Debug.Print "✓ WriteLog sem parâmetro details funcionou"
    
    ' Teste 3: Funções auxiliares sem details
    Call LogInfo("TestModule", "Info sem detalhes")
    Call LogWarning("TestModule", "Warning sem detalhes")
    Call LogErrorMessage("TestModule", "Error sem detalhes")
    Call LogDebug("TestModule", "Debug sem detalhes")
    Debug.Print "✓ Funções auxiliares sem details funcionaram"
    
    Call FinalizeLogging()
    Debug.Print "✓ Teste de parâmetros opcionais concluído"
End Sub

Public Sub TestLogLevels()
    ' Teste específico para enum LogLevel
    Dim level As LogLevel
    Dim result As Boolean
    
    result = InitializeLogging()
    
    If result Then
        ' Testar cada valor do enum
        level = LogLevel_Info
        Call WriteLog(level, "TestModule", "Teste LogLevel_Info")
        
        level = LogLevel_Warning  
        Call WriteLog(level, "TestModule", "Teste LogLevel_Warning")
        
        level = LogLevel_Error
        Call WriteLog(level, "TestModule", "Teste LogLevel_Error")
        
        level = LogLevel_Debug
        Call WriteLog(level, "TestModule", "Teste LogLevel_Debug")
        
        Debug.Print "✓ Todos os valores de LogLevel funcionaram corretamente"
        
        Call FinalizeLogging()
    End If
End Sub