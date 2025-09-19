' VBA Module Example for Microsoft Word Integration with CarimboPDF
' Copy this code to a new module in Word VBA Editor (Alt+F11)

Option Explicit

' =====================================================
' EXEMPLO COMPLETO DE USO DA API CARIMBOPDF
' =====================================================

Sub ExemploCompletoVBA()
    ' Este é um exemplo completo de como usar a integração VBA com CarimboPDF
    On Error GoTo ErrorHandler
    
    ' 1. Verificar se o serviço está disponível
    If Not VerificarServicoDisponivel() Then
        MsgBox "Serviço CarimboPDF não está disponível." & vbCrLf & _
               "Verifique se o servidor está rodando com:" & vbCrLf & _
               "python -m data_hora_pdf.cli --vba-api --vba-port 8080", _
               vbCritical, "Erro de Conexão"
        Exit Sub
    End If
    
    ' 2. Fazer login no sistema DETRAN (opcional)
    If Not FazerLogin() Then
        MsgBox "Aviso: Falha no login DETRAN. Continuando com dados simulados.", _
               vbExclamation, "Aviso de Login"
    End If
    
    ' 3. Solicitar placa ao usuário
    Dim placa As String
    placa = InputBox("Digite a placa do veículo para consulta:", _
                     "Consulta DETRAN", "ABC1234")
    
    If placa = "" Then
        MsgBox "Operação cancelada pelo usuário.", vbInformation
        Exit Sub
    End If
    
    ' 4. Consultar dados do veículo
    Dim vehicle As VehicleData
    vehicle = ConsultarPlaca(placa, "SC")
    
    ' 5. Exibir dados em caixa de diálogo
    ExibirDadosVeiculo vehicle
    
    ' 6. Perguntar se deseja inserir no documento
    Dim resposta As VbMsgBoxResult
    resposta = MsgBox("Deseja inserir os dados do veículo no documento atual?", _
                      vbYesNo + vbQuestion, "Inserir Dados")
    
    If resposta = vbYes Then
        ' 7. Inserir dados no documento Word
        InserirDadosNoDocumento vehicle
        MsgBox "Dados inseridos com sucesso no documento!", _
               vbInformation, "Inserção Completa"
    End If
    
    Exit Sub
    
ErrorHandler:
    Dim errorMsg As String
    Select Case Err.Number
        Case vbObjectError + 1002
            errorMsg = "Veículo não encontrado para a placa " & placa
        Case vbObjectError + 1003
            errorMsg = "Dados de entrada inválidos. Verifique a placa."
        Case vbObjectError + 1004
            errorMsg = "Erro no servidor DETRAN. Tente novamente mais tarde."
        Case Else
            errorMsg = "Erro inesperado: " & Err.Description
    End Select
    
    MsgBox errorMsg, vbCritical, "Erro na Consulta"
End Sub

' =====================================================
' EXEMPLO COM MÚLTIPLAS PLACAS
' =====================================================

Sub ConsultarMultiplasPlacas()
    ' Exemplo de como consultar múltiplas placas de uma vez
    On Error GoTo ErrorHandler
    
    ' Lista de placas para consultar
    Dim placas As Variant
    placas = Array("ABC1234", "XYZ5678", "DEF9012")
    
    ' Verificar conectividade
    If Not VerificarServicoDisponivel() Then
        MsgBox "Serviço indisponível", vbCritical
        Exit Sub
    End If
    
    ' Fazer login uma vez
    FazerLogin
    
    Dim i As Integer
    Dim vehicle As VehicleData
    Dim resultados As String
    
    resultados = "CONSULTA EM LOTE - RESULTADOS" & vbCrLf & vbCrLf
    
    ' Consultar cada placa
    For i = 0 To UBound(placas)
        On Error Resume Next ' Continuar mesmo com erro individual
        
        vehicle = ConsultarPlaca(CStr(placas(i)), "SC")
        
        If Err.Number = 0 Then
            resultados = resultados & placas(i) & ": " & _
                        vehicle.Marca & " " & vehicle.Modelo & " " & _
                        vehicle.AnoFabricacao & vbCrLf
        Else
            resultados = resultados & placas(i) & ": ERRO - " & _
                        Err.Description & vbCrLf
        End If
        
        Err.Clear
        On Error GoTo ErrorHandler
    Next i
    
    ' Exibir resultados
    MsgBox resultados, vbInformation, "Resultados da Consulta em Lote"
    
    Exit Sub
    
ErrorHandler:
    MsgBox "Erro durante consulta em lote: " & Err.Description, vbCritical
End Sub

' =====================================================
' EXEMPLO COM FORMATAÇÃO AVANÇADA NO WORD
' =====================================================

Sub InserirDadosFormatados()
    ' Exemplo de inserção com formatação avançada
    On Error GoTo ErrorHandler
    
    Dim placa As String
    placa = InputBox("Digite a placa:", "Consulta", "ABC1234")
    If placa = "" Then Exit Sub
    
    ' Consultar dados
    Dim vehicle As VehicleData
    vehicle = ConsultarPlaca(placa, "SC")
    
    ' Inserir com formatação avançada
    Dim doc As Document
    Set doc = ActiveDocument
    
    With Selection
        ' Título
        .Font.Name = "Arial"
        .Font.Size = 16
        .Font.Bold = True
        .Font.Color = RGB(0, 0, 128) ' Azul escuro
        .TypeText "DADOS DO VEÍCULO" & vbCrLf & vbCrLf
        
        ' Resetar formatação
        .Font.Size = 12
        .Font.Bold = False
        .Font.Color = RGB(0, 0, 0) ' Preto
        
        ' Criar tabela
        Dim tabela As Table
        Set tabela = doc.Tables.Add(Selection.Range, 6, 2)
        
        ' Preencher tabela
        With tabela
            .Cell(1, 1).Range.Text = "Placa:"
            .Cell(1, 2).Range.Text = vehicle.Placa & " - " & vehicle.UF
            .Cell(2, 1).Range.Text = "Veículo:"
            .Cell(2, 2).Range.Text = vehicle.Marca & " " & vehicle.Modelo
            .Cell(3, 1).Range.Text = "Ano:"
            .Cell(3, 2).Range.Text = vehicle.AnoFabricacao & "/" & vehicle.AnoModelo
            .Cell(4, 1).Range.Text = "Cor:"
            .Cell(4, 2).Range.Text = vehicle.Cor
            .Cell(5, 1).Range.Text = "Proprietário:"
            .Cell(5, 2).Range.Text = vehicle.Proprietario
            .Cell(6, 1).Range.Text = "Situação:"
            .Cell(6, 2).Range.Text = vehicle.Situacao
            
            ' Formatação da tabela
            .Borders.Enable = True
            .Range.Font.Name = "Arial"
            .Columns(1).Width = InchesToPoints(1.5)
            .Columns(2).Width = InchesToPoints(3.5)
            
            ' Cabeçalho em negrito
            .Columns(1).Range.Font.Bold = True
        End With
        
        ' Posicionar após a tabela
        Selection.EndKey Unit:=wdStory
        .TypeText vbCrLf & "Consulta realizada em: " & vehicle.ConsultaTimestamp & vbCrLf
    End With
    
    MsgBox "Dados inseridos com formatação avançada!", vbInformation
    
    Exit Sub
    
ErrorHandler:
    MsgBox "Erro ao inserir dados formatados: " & Err.Description, vbCritical
End Sub

' =====================================================
' EXEMPLO DE AUTOMAÇÃO COM DOCUMENTO TEMPLATE
' =====================================================

Sub PreencherTemplate()
    ' Exemplo de preenchimento automático de template com bookmarks
    On Error GoTo ErrorHandler
    
    Dim placa As String
    placa = InputBox("Digite a placa para preencher o template:", "Template", "ABC1234")
    If placa = "" Then Exit Sub
    
    ' Consultar dados
    Dim vehicle As VehicleData
    vehicle = ConsultarPlaca(placa, "SC")
    
    ' Preencher bookmarks no documento
    ' (Primeiro crie bookmarks no Word: Insert > Bookmark)
    Dim doc As Document
    Set doc = ActiveDocument
    
    ' Verificar e preencher bookmarks
    If doc.Bookmarks.Exists("Placa") Then
        doc.Bookmarks("Placa").Range.Text = vehicle.Placa
    End If
    
    If doc.Bookmarks.Exists("Marca") Then
        doc.Bookmarks("Marca").Range.Text = vehicle.Marca
    End If
    
    If doc.Bookmarks.Exists("Modelo") Then
        doc.Bookmarks("Modelo").Range.Text = vehicle.Modelo
    End If
    
    If doc.Bookmarks.Exists("Ano") Then
        doc.Bookmarks("Ano").Range.Text = CStr(vehicle.AnoFabricacao)
    End If
    
    If doc.Bookmarks.Exists("Cor") Then
        doc.Bookmarks("Cor").Range.Text = vehicle.Cor
    End If
    
    If doc.Bookmarks.Exists("Proprietario") Then
        doc.Bookmarks("Proprietario").Range.Text = vehicle.Proprietario
    End If
    
    MsgBox "Template preenchido com sucesso!", vbInformation
    
    Exit Sub
    
ErrorHandler:
    MsgBox "Erro ao preencher template: " & Err.Description & vbCrLf & _
           "Verifique se os bookmarks existem no documento.", vbCritical
End Sub

' =====================================================
' EXEMPLO DE CONFIGURAÇÃO E MONITORAMENTO
' =====================================================

Sub VerificarStatusSistema()
    ' Exemplo de verificação completa do sistema
    Dim msg As String
    msg = "STATUS DO SISTEMA CARIMBOPDF" & vbCrLf & vbCrLf
    
    ' Verificar conectividade
    If VerificarServicoDisponivel() Then
        msg = msg & "✓ Serviço CarimboPDF: DISPONÍVEL" & vbCrLf
    Else
        msg = msg & "✗ Serviço CarimboPDF: INDISPONÍVEL" & vbCrLf
    End If
    
    ' Verificar autenticação
    If FazerLogin() Then
        msg = msg & "✓ Autenticação DETRAN: SUCESSO" & vbCrLf
    Else
        msg = msg & "✗ Autenticação DETRAN: FALHA" & vbCrLf
    End If
    
    ' Teste de consulta
    On Error Resume Next
    Dim testVehicle As VehicleData
    testVehicle = ConsultarPlaca("ABC1234", "SC")
    
    If Err.Number = 0 Then
        msg = msg & "✓ Consulta de teste: FUNCIONANDO" & vbCrLf
    Else
        msg = msg & "✗ Consulta de teste: ERRO" & vbCrLf
    End If
    On Error GoTo 0
    
    msg = msg & vbCrLf & "Para mais informações, consulte os logs do sistema."
    
    MsgBox msg, vbInformation, "Status do Sistema"
End Sub

' =====================================================
' PROCEDIMENTOS DE CONFIGURAÇÃO INICIAL
' =====================================================

Sub ConfiguracaoInicial()
    ' Assistente de configuração inicial para novos usuários
    Dim msg As String
    msg = "ASSISTENTE DE CONFIGURAÇÃO - CARIMBOPDF VBA" & vbCrLf & vbCrLf
    msg = msg & "Este assistente vai verificar se tudo está configurado corretamente." & vbCrLf & vbCrLf
    msg = msg & "Passos necessários:" & vbCrLf
    msg = msg & "1. Servidor CarimboPDF rodando" & vbCrLf
    msg = msg & "2. Conectividade de rede" & vbCrLf
    msg = msg & "3. Referências VBA configuradas" & vbCrLf & vbCrLf
    msg = msg & "Deseja continuar com a verificação?"
    
    If MsgBox(msg, vbYesNo + vbQuestion, "Configuração Inicial") = vbNo Then
        Exit Sub
    End If
    
    ' Verificações passo a passo
    msg = "RESULTADOS DA VERIFICAÇÃO:" & vbCrLf & vbCrLf
    
    ' 1. Servidor
    If VerificarServicoDisponivel() Then
        msg = msg & "✓ Servidor CarimboPDF: OK" & vbCrLf
    Else
        msg = msg & "✗ Servidor CarimboPDF: FALHA" & vbCrLf
        msg = msg & "  → Execute: python -m data_hora_pdf.cli --vba-api" & vbCrLf
    End If
    
    ' 2. Referências (verificação básica)
    On Error Resume Next
    Dim xmlHttp As Object
    Set xmlHttp = CreateObject("MSXML2.ServerXMLHTTP60")
    If Err.Number = 0 Then
        msg = msg & "✓ Referência MSXML2: OK" & vbCrLf
    Else
        msg = msg & "✗ Referência MSXML2: FALHA" & vbCrLf
        msg = msg & "  → Ative em Ferramentas > Referências" & vbCrLf
    End If
    On Error GoTo 0
    
    ' 3. Teste funcional
    On Error Resume Next
    Dim testResult As VehicleData
    testResult = ConsultarPlaca("ABC1234", "SC")
    If Err.Number = 0 Then
        msg = msg & "✓ Teste funcional: OK" & vbCrLf
    Else
        msg = msg & "✗ Teste funcional: FALHA" & vbCrLf
        msg = msg & "  → Erro: " & Err.Description & vbCrLf
    End If
    On Error GoTo 0
    
    msg = msg & vbCrLf & "Configuração concluída!"
    MsgBox msg, vbInformation, "Resultado da Configuração"
End Sub