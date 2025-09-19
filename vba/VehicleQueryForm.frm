' UserForm code for VehicleQueryForm
' Formulário para consulta de veículos integrado ao Word

Option Explicit

Private Sub UserForm_Initialize()
    ' Configurar formulário na inicialização
    Me.Caption = "CarimboPDF - Consulta de Veículo"
    Me.Width = 400
    Me.Height = 500
    
    ' Configurar campos padrão
    txtUF.Text = "SC"
    txtPlaca.Text = ""
    
    ' Configurar combo de UF
    With cmbUF
        .AddItem "AC"
        .AddItem "AL"
        .AddItem "AP"
        .AddItem "AM"
        .AddItem "BA"
        .AddItem "CE"
        .AddItem "DF"
        .AddItem "ES"
        .AddItem "GO"
        .AddItem "MA"
        .AddItem "MT"
        .AddItem "MS"
        .AddItem "MG"
        .AddItem "PA"
        .AddItem "PB"
        .AddItem "PR"
        .AddItem "PE"
        .AddItem "PI"
        .AddItem "RJ"
        .AddItem "RN"
        .AddItem "RS"
        .AddItem "RO"
        .AddItem "RR"
        .AddItem "SC"
        .AddItem "SP"
        .AddItem "SE"
        .AddItem "TO"
        .Text = "SC" ' Valor padrão
    End With
    
    ' Verificar se o serviço está disponível
    VerificarConexao
End Sub

Private Sub btnConsultar_Click()
    On Error GoTo ErrorHandler
    
    ' Validar entrada
    If Trim(txtPlaca.Text) = "" Then
        MsgBox "Por favor, digite a placa do veículo.", vbExclamation, "Campo Obrigatório"
        txtPlaca.SetFocus
        Exit Sub
    End If
    
    If Len(Trim(txtPlaca.Text)) < 7 Then
        MsgBox "A placa deve ter pelo menos 7 caracteres.", vbExclamation, "Placa Inválida"
        txtPlaca.SetFocus
        Exit Sub
    End If
    
    ' Desabilitar controles durante consulta
    btnConsultar.Enabled = False
    lblStatus.Caption = "Consultando..."
    DoEvents
    
    ' Fazer consulta
    Dim vehicle As VehicleData
    vehicle = ConsultarPlaca(txtPlaca.Text, cmbUF.Text)
    
    ' Preencher formulário com dados retornados
    PreencherFormulario vehicle
    
    ' Reabilitar controles
    btnConsultar.Enabled = True
    lblStatus.Caption = "Consulta realizada com sucesso!"
    
    Exit Sub
    
ErrorHandler:
    btnConsultar.Enabled = True
    lblStatus.Caption = "Erro na consulta"
    
    Select Case Err.Number
        Case vbObjectError + 1002
            MsgBox "Veículo não encontrado para a placa informada.", vbExclamation, "Veículo Não Encontrado"
        Case vbObjectError + 1003
            MsgBox "Dados de entrada inválidos. Verifique a placa e UF.", vbExclamation, "Dados Inválidos"
        Case Else
            MsgBox "Erro durante a consulta: " & Err.Description, vbCritical, "Erro"
    End Select
End Sub

Private Sub btnInserirDocumento_Click()
    On Error GoTo ErrorHandler
    
    ' Verificar se há dados para inserir
    If Trim(lblPlacaResult.Caption) = "" Then
        MsgBox "Realize uma consulta primeiro antes de inserir dados no documento.", vbExclamation, "Nenhum Dado"
        Exit Sub
    End If
    
    ' Criar estrutura de dados do veículo
    Dim vehicle As VehicleData
    With vehicle
        .Placa = lblPlacaResult.Caption
        .UF = lblUFResult.Caption
        .Marca = lblMarcaResult.Caption
        .Modelo = lblModeloResult.Caption
        .AnoFabricacao = CInt(lblAnoFabResult.Caption)
        .AnoModelo = CInt(lblAnoModResult.Caption)
        .Cor = lblCorResult.Caption
        .Combustivel = lblCombustivelResult.Caption
        .Categoria = lblCategoriaResult.Caption
        .Proprietario = lblProprietarioResult.Caption
        .Municipio = lblMunicipioResult.Caption
        .Situacao = lblSituacaoResult.Caption
        .ConsultaTimestamp = lblTimestampResult.Caption
    End With
    
    ' Inserir dados no documento
    InserirDadosNoDocumento vehicle
    
    MsgBox "Dados inseridos no documento com sucesso!", vbInformation, "Inserção Concluída"
    
    Exit Sub
    
ErrorHandler:
    MsgBox "Erro ao inserir dados no documento: " & Err.Description, vbCritical, "Erro"
End Sub

Private Sub btnFechar_Click()
    Unload Me
End Sub

Private Sub btnLimpar_Click()
    ' Limpar campos de resultado
    LimparResultados
    
    ' Limpar campos de entrada
    txtPlaca.Text = ""
    txtPlaca.SetFocus
    
    lblStatus.Caption = "Pronto para consulta"
End Sub

Private Sub PreencherFormulario(vehicle As VehicleData)
    ' Preencher labels com dados do veículo
    lblPlacaResult.Caption = vehicle.Placa
    lblUFResult.Caption = vehicle.UF
    lblMarcaResult.Caption = vehicle.Marca
    lblModeloResult.Caption = vehicle.Modelo
    lblAnoFabResult.Caption = CStr(vehicle.AnoFabricacao)
    lblAnoModResult.Caption = CStr(vehicle.AnoModelo)
    lblCorResult.Caption = vehicle.Cor
    lblCombustivelResult.Caption = vehicle.Combustivel
    lblCategoriaResult.Caption = vehicle.Categoria
    lblProprietarioResult.Caption = vehicle.Proprietario
    lblMunicipioResult.Caption = vehicle.Municipio
    lblSituacaoResult.Caption = vehicle.Situacao
    lblTimestampResult.Caption = vehicle.ConsultaTimestamp
    
    ' Habilitar botão de inserção
    btnInserirDocumento.Enabled = True
End Sub

Private Sub LimparResultados()
    ' Limpar todos os campos de resultado
    lblPlacaResult.Caption = ""
    lblUFResult.Caption = ""
    lblMarcaResult.Caption = ""
    lblModeloResult.Caption = ""
    lblAnoFabResult.Caption = ""
    lblAnoModResult.Caption = ""
    lblCorResult.Caption = ""
    lblCombustivelResult.Caption = ""
    lblCategoriaResult.Caption = ""
    lblProprietarioResult.Caption = ""
    lblMunicipioResult.Caption = ""
    lblSituacaoResult.Caption = ""
    lblTimestampResult.Caption = ""
    
    ' Desabilitar botão de inserção
    btnInserirDocumento.Enabled = False
End Sub

Private Sub VerificarConexao()
    If VerificarServicoDisponivel() Then
        lblConexao.Caption = "✓ Conectado ao serviço CarimboPDF"
        lblConexao.ForeColor = RGB(0, 128, 0) ' Verde
    Else
        lblConexao.Caption = "✗ Serviço CarimboPDF indisponível"
        lblConexao.ForeColor = RGB(255, 0, 0) ' Vermelho
    End If
End Sub

Private Sub txtPlaca_KeyPress(KeyAscii As Integer)
    ' Converter para maiúscula automaticamente
    If KeyAscii >= 97 And KeyAscii <= 122 Then
        KeyAscii = KeyAscii - 32
    End If
    
    ' Permitir apenas letras, números e backspace
    If Not ((KeyAscii >= 48 And KeyAscii <= 57) Or _
            (KeyAscii >= 65 And KeyAscii <= 90) Or _
            KeyAscii = 8) Then
        KeyAscii = 0
    End If
End Sub

Private Sub txtPlaca_Change()
    ' Limpar resultados quando a placa for alterada
    If lblPlacaResult.Caption <> "" Then
        LimparResultados
        lblStatus.Caption = "Pronto para consulta"
    End If
End Sub