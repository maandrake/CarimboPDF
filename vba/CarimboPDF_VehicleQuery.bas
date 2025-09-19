' VBA Module for CarimboPDF Integration with Word
' Este módulo fornece funcionalidades para consultar dados de veículos
' e integrar com o sistema CarimboPDF para carimbagem automática

Option Explicit

' Constantes de configuração
Private Const API_BASE_URL As String = "http://127.0.0.1:8080"
Private Const API_TIMEOUT As Long = 30000 ' 30 segundos
Private Const HTTP_STATUS_OK As Long = 200
Private Const HTTP_STATUS_NOT_FOUND As Long = 404
Private Const HTTP_STATUS_BAD_REQUEST As Long = 400

' Estrutura para dados do veículo
Public Type VehicleData
    Placa As String
    UF As String
    Marca As String
    Modelo As String
    AnoFabricacao As Integer
    AnoModelo As Integer
    Cor As String
    Combustivel As String
    Categoria As String
    Proprietario As String
    Municipio As String
    Situacao As String
    ConsultaTimestamp As String
End Type

' Estrutura para resposta da API
Public Type ApiResponse
    Success As Boolean
    ErrorCode As String
    ErrorMessage As String
    Timestamp As String
End Type

' Função principal para consultar placa
Public Function ConsultarPlaca(placa As String, Optional uf As String = "SC") As VehicleData
    On Error GoTo ErrorHandler
    
    Dim vehicle As VehicleData
    Dim response As ApiResponse
    
    ' Validar entrada
    If Len(Trim(placa)) < 7 Then
        Err.Raise vbObjectError + 1001, "ConsultarPlaca", "Placa deve ter pelo menos 7 caracteres"
    End If
    
    ' Normalizar placa
    placa = UCase(Trim(placa))
    uf = UCase(Trim(uf))
    
    ' Fazer requisição HTTP
    Dim httpRequest As Object
    Set httpRequest = CreateObject("MSXML2.ServerXMLHTTP60")
    
    Dim requestUrl As String
    requestUrl = API_BASE_URL & "/consulta/placa"
    
    Dim requestBody As String
    requestBody = "{""placa"": """ & placa & """, ""uf"": """ & uf & """}"
    
    ' Configurar e enviar requisição
    With httpRequest
        .Open "POST", requestUrl, False
        .setRequestHeader "Content-Type", "application/json"
        .setRequestHeader "Accept", "application/json"
        .setTimeouts 0, 0, 0, API_TIMEOUT
        .send requestBody
    End With
    
    ' Processar resposta
    If httpRequest.Status = HTTP_STATUS_OK Then
        vehicle = ParseVehicleResponse(httpRequest.responseText)
    ElseIf httpRequest.Status = HTTP_STATUS_NOT_FOUND Then
        Err.Raise vbObjectError + 1002, "ConsultarPlaca", "Veículo não encontrado"
    ElseIf httpRequest.Status = HTTP_STATUS_BAD_REQUEST Then
        Err.Raise vbObjectError + 1003, "ConsultarPlaca", "Dados de entrada inválidos"
    Else
        Err.Raise vbObjectError + 1004, "ConsultarPlaca", "Erro no servidor: " & httpRequest.Status
    End If
    
    ConsultarPlaca = vehicle
    Exit Function
    
ErrorHandler:
    Dim errorMsg As String
    errorMsg = "Erro ao consultar placa " & placa & ": " & Err.Description
    
    ' Log do erro (opcional)
    Debug.Print "CarimboPDF VBA Error: " & errorMsg
    
    ' Re-raise error com contexto
    Err.Raise Err.Number, "ConsultarPlaca", errorMsg
End Function

' Função para verificar se o serviço está disponível
Public Function VerificarServicoDisponivel() As Boolean
    On Error GoTo ErrorHandler
    
    Dim httpRequest As Object
    Set httpRequest = CreateObject("MSXML2.ServerXMLHTTP60")
    
    Dim requestUrl As String
    requestUrl = API_BASE_URL & "/health"
    
    With httpRequest
        .Open "GET", requestUrl, False
        .setTimeouts 0, 0, 0, 5000 ' 5 segundos timeout
        .send
    End With
    
    VerificarServicoDisponivel = (httpRequest.Status = HTTP_STATUS_OK)
    Exit Function
    
ErrorHandler:
    VerificarServicoDisponivel = False
End Function

' Função para fazer login no sistema DETRAN
Public Function FazerLogin(Optional username As String = "", Optional password As String = "") As Boolean
    On Error GoTo ErrorHandler
    
    Dim httpRequest As Object
    Set httpRequest = CreateObject("MSXML2.ServerXMLHTTP60")
    
    Dim requestUrl As String
    requestUrl = API_BASE_URL & "/auth/login"
    
    Dim requestBody As String
    If username <> "" And password <> "" Then
        requestBody = "{""username"": """ & username & """, ""password"": """ & password & """}"
    Else
        requestBody = "{}"
    End If
    
    With httpRequest
        .Open "POST", requestUrl, False
        .setRequestHeader "Content-Type", "application/json"
        .setRequestHeader "Accept", "application/json"
        .setTimeouts 0, 0, 0, API_TIMEOUT
        .send requestBody
    End With
    
    FazerLogin = (httpRequest.Status = HTTP_STATUS_OK)
    Exit Function
    
ErrorHandler:
    FazerLogin = False
End Function

' Função auxiliar para parsear resposta JSON do veículo
Private Function ParseVehicleResponse(jsonText As String) As VehicleData
    On Error GoTo ErrorHandler
    
    Dim vehicle As VehicleData
    Dim json As Object
    
    ' Parse JSON usando ScriptControl (para compatibilidade)
    Set json = CreateObject("ScriptControl")
    json.Language = "JScript"
    json.AddCode "function parseJSON(jsonString) { return eval('(' + jsonString + ')'); }"
    
    Dim parsedJson As Object
    Set parsedJson = json.Run("parseJSON", jsonText)
    
    ' Extrair dados do veículo
    If parsedJson.success Then
        With vehicle
            .Placa = GetJsonValue(parsedJson.data, "placa", "")
            .UF = GetJsonValue(parsedJson.data, "uf", "")
            .Marca = GetJsonValue(parsedJson.data, "marca", "")
            .Modelo = GetJsonValue(parsedJson.data, "modelo", "")
            .AnoFabricacao = CInt(GetJsonValue(parsedJson.data, "ano_fabricacao", 0))
            .AnoModelo = CInt(GetJsonValue(parsedJson.data, "ano_modelo", 0))
            .Cor = GetJsonValue(parsedJson.data, "cor", "")
            .Combustivel = GetJsonValue(parsedJson.data, "combustivel", "")
            .Categoria = GetJsonValue(parsedJson.data, "categoria", "")
            .Proprietario = GetJsonValue(parsedJson.data, "proprietario", "")
            .Municipio = GetJsonValue(parsedJson.data, "municipio", "")
            .Situacao = GetJsonValue(parsedJson.data, "situacao", "")
            .ConsultaTimestamp = GetJsonValue(parsedJson.data, "consulta_timestamp", "")
        End With
    Else
        Err.Raise vbObjectError + 1005, "ParseVehicleResponse", "Resposta da API indica falha"
    End If
    
    ParseVehicleResponse = vehicle
    Exit Function
    
ErrorHandler:
    Err.Raise vbObjectError + 1006, "ParseVehicleResponse", "Erro ao processar resposta: " & Err.Description
End Function

' Função auxiliar para extrair valores do JSON
Private Function GetJsonValue(jsonObj As Object, key As String, defaultValue As Variant) As Variant
    On Error Resume Next
    
    Dim value As Variant
    value = CallByName(jsonObj, key, VbGet)
    
    If Err.Number <> 0 Or IsNull(value) Or IsEmpty(value) Then
        GetJsonValue = defaultValue
    Else
        GetJsonValue = value
    End If
    
    On Error GoTo 0
End Function

' Função para exibir dados do veículo formatados
Public Sub ExibirDadosVeiculo(vehicle As VehicleData)
    Dim msg As String
    msg = "DADOS DO VEÍCULO" & vbCrLf & vbCrLf
    msg = msg & "Placa: " & vehicle.Placa & vbCrLf
    msg = msg & "UF: " & vehicle.UF & vbCrLf
    msg = msg & "Marca/Modelo: " & vehicle.Marca & " " & vehicle.Modelo & vbCrLf
    msg = msg & "Ano Fabricação: " & vehicle.AnoFabricacao & vbCrLf
    msg = msg & "Ano Modelo: " & vehicle.AnoModelo & vbCrLf
    msg = msg & "Cor: " & vehicle.Cor & vbCrLf
    msg = msg & "Combustível: " & vehicle.Combustivel & vbCrLf
    msg = msg & "Categoria: " & vehicle.Categoria & vbCrLf
    msg = msg & "Proprietário: " & vehicle.Proprietario & vbCrLf
    msg = msg & "Município: " & vehicle.Municipio & vbCrLf
    msg = msg & "Situação: " & vehicle.Situacao & vbCrLf
    msg = msg & "Consulta: " & vehicle.ConsultaTimestamp
    
    MsgBox msg, vbInformation, "CarimboPDF - Consulta de Veículo"
End Sub

' Função para inserir dados do veículo no documento Word
Public Sub InserirDadosNoDocumento(vehicle As VehicleData)
    On Error GoTo ErrorHandler
    
    Dim doc As Document
    Set doc = ActiveDocument
    
    ' Inserir dados na posição atual do cursor
    With Selection
        .TypeText "DADOS DO VEÍCULO" & vbCrLf
        .Font.Bold = True
        .TypeText "Placa: " & vehicle.Placa & " - " & vehicle.UF & vbCrLf
        .Font.Bold = False
        .TypeText "Marca/Modelo: " & vehicle.Marca & " " & vehicle.Modelo & vbCrLf
        .TypeText "Ano: " & vehicle.AnoFabricacao & "/" & vehicle.AnoModelo & vbCrLf
        .TypeText "Cor: " & vehicle.Cor & vbCrLf
        .TypeText "Combustível: " & vehicle.Combustivel & vbCrLf
        .TypeText "Categoria: " & vehicle.Categoria & vbCrLf
        .TypeText "Proprietário: " & vehicle.Proprietario & vbCrLf
        .TypeText "Município: " & vehicle.Municipio & vbCrLf
        .TypeText "Situação: " & vehicle.Situacao & vbCrLf
        .TypeText "Consulta realizada em: " & vehicle.ConsultaTimestamp & vbCrLf
    End With
    
    Exit Sub
    
ErrorHandler:
    MsgBox "Erro ao inserir dados no documento: " & Err.Description, vbCritical, "CarimboPDF VBA"
End Sub

' Procedimento principal para demonstração
Public Sub TestarConsultaVeiculo()
    On Error GoTo ErrorHandler
    
    ' Verificar se o serviço está disponível
    If Not VerificarServicoDisponivel() Then
        MsgBox "Serviço CarimboPDF não está disponível. Verifique se o servidor está rodando.", vbCritical, "Erro de Conexão"
        Exit Sub
    End If
    
    ' Solicitar placa ao usuário
    Dim placa As String
    placa = InputBox("Digite a placa do veículo:", "Consulta de Veículo", "ABC1234")
    
    If placa = "" Then Exit Sub
    
    ' Fazer login (opcional para demonstração)
    FazerLogin
    
    ' Consultar veículo
    Dim vehicle As VehicleData
    vehicle = ConsultarPlaca(placa)
    
    ' Exibir dados
    ExibirDadosVeiculo vehicle
    
    ' Perguntar se deseja inserir no documento
    Dim resposta As VbMsgBoxResult
    resposta = MsgBox("Deseja inserir os dados no documento atual?", vbYesNo + vbQuestion, "Inserir Dados")
    
    If resposta = vbYes Then
        InserirDadosNoDocumento vehicle
    End If
    
    Exit Sub
    
ErrorHandler:
    MsgBox "Erro durante a consulta: " & Err.Description, vbCritical, "CarimboPDF VBA"
End Sub