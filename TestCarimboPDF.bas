Sub TestCarimboPDF()
'
' TestCarimboPDF Macro
' Macro de teste para a integração CarimboPDF com Word VBA
' 
' Esta macro demonstra o uso básico do CarimboPDF no Word
' Certifique-se de que o módulo CarimboPDF_WordIntegration.bas foi importado
'

    ' Verificar se há documento ativo
    If ActiveDocument Is Nothing Then
        MsgBox "Por favor, abra um documento antes de executar esta macro.", vbExclamation, "Teste CarimboPDF"
        Exit Sub
    End If
    
    ' Verificar se o documento foi salvo
    If ActiveDocument.Saved = False Or ActiveDocument.Path = "" Then
        Dim resposta As VbMsgBoxResult
        resposta = MsgBox("O documento precisa ser salvo antes de continuar." & vbCrLf & _
                         "Deseja salvar agora?", vbYesNo + vbQuestion, "Teste CarimboPDF")
        
        If resposta = vbYes Then
            ActiveDocument.Save
        Else
            MsgBox "Operação cancelada pelo usuário.", vbInformation, "Teste CarimboPDF"
            Exit Sub
        End If
    End If
    
    ' Mostrar menu de opções
    Dim opcao As String
    opcao = InputBox("Escolha o tipo de teste:" & vbCrLf & vbCrLf & _
                    "1 - Carimbo simples (padrão)" & vbCrLf & _
                    "2 - Carimbo personalizado" & vbCrLf & _
                    "3 - Carimbo com proteção" & vbCrLf & vbCrLf & _
                    "Digite o número da opção:", "Teste CarimboPDF", "1")
    
    Select Case opcao
        Case "1"
            Call TesteCarimboSimples
        Case "2"
            Call TesteCarimboPersonalizado
        Case "3"
            Call TesteCarimboComProtecao
        Case ""
            ' Usuário cancelou
            Exit Sub
        Case Else
            MsgBox "Opção inválida. Usando carimbo simples.", vbInformation, "Teste CarimboPDF"
            Call TesteCarimboSimples
    End Select
End Sub

Private Sub TesteCarimboSimples()
    ' Teste com configurações padrão
    MsgBox "Aplicando carimbo simples com configurações padrão...", vbInformation, "Teste CarimboPDF"
    
    Call CarimbarDocumentoSimples()
End Sub

Private Sub TesteCarimboPersonalizado()
    ' Teste com configurações personalizadas
    Dim opcoes As CarimboOptions
    Dim cidade As String
    
    cidade = InputBox("Digite a cidade para o carimbo:", "Teste CarimboPDF", "São Paulo")
    If cidade = "" Then
        MsgBox "Operação cancelada.", vbInformation, "Teste CarimboPDF"
        Exit Sub
    End If
    
    MsgBox "Aplicando carimbo personalizado..." & vbCrLf & _
           "Cidade: " & cidade & vbCrLf & _
           "Fonte: 14pt, negrito, azul", vbInformation, "Teste CarimboPDF"
    
    opcoes = CriarOpcoesPadrao()
    opcoes.Cidade = cidade
    opcoes.FonteSize = "14"
    opcoes.Negrito = True
    opcoes.Cor = "#0000FF"  ' Azul
    
    Call CarimbarDocumentoAtivo(opcoes)
End Sub

Private Sub TesteCarimboComProtecao()
    ' Teste com proteção por senha
    Dim opcoes As CarimboOptions
    Dim senha As String
    
    senha = InputBox("Digite uma senha para proteger o PDF:" & vbCrLf & _
                    "(Deixe em branco para cancelar)", "Teste CarimboPDF")
    
    If senha = "" Then
        MsgBox "Operação cancelada.", vbInformation, "Teste CarimboPDF"
        Exit Sub
    End If
    
    MsgBox "Aplicando carimbo com proteção..." & vbCrLf & _
           "- Senha de proteção definida" & vbCrLf & _
           "- Edição restrita" & vbCrLf & _
           "- Cópia desabilitada", vbInformation, "Teste CarimboPDF"
    
    opcoes = CriarOpcoesPadrao()
    opcoes.SenhaProtecao = senha
    opcoes.RestringirEdicao = True
    opcoes.DesativarCopia = True
    
    Call CarimbarDocumentoAtivo(opcoes)
End Sub

Sub SobreCarimboPDF()
'
' Mostra informações sobre o CarimboPDF
'
    Dim info As String
    
    info = "CarimboPDF - Integração Word VBA" & vbCrLf & _
           "=====================================" & vbCrLf & vbCrLf & _
           "Versão: 1.0" & vbCrLf & _
           "Data: Setembro 2025" & vbCrLf & _
           "Autor: Marcos Despachante" & vbCrLf & vbCrLf & _
           "Funcionalidades:" & vbCrLf & _
           "• Conversão automática Word → PDF" & vbCrLf & _
           "• Carimbo de data e cidade" & vbCrLf & _
           "• Opções de formatação" & vbCrLf & _
           "• Proteção com senha" & vbCrLf & _
           "• Inserção de logo" & vbCrLf & vbCrLf & _
           "Para usar:" & vbCrLf & _
           "1. Abra ou crie um documento" & vbCrLf & _
           "2. Salve o documento" & vbCrLf & _
           "3. Execute a macro TestCarimboPDF" & vbCrLf & vbCrLf & _
           "Documentação completa em:" & vbCrLf & _
           "WORD_VBA_INTEGRATION.md"
    
    MsgBox info, vbInformation, "Sobre CarimboPDF"
End Sub

Sub VerificarInstalacao()
'
' Verifica se a instalação do CarimboPDF está correta
'
    Dim resultado As String
    
    resultado = "Verificação da Instalação CarimboPDF" & vbCrLf & _
                "======================================" & vbCrLf & vbCrLf
    
    ' Verificar se o módulo foi importado
    On Error Resume Next
    Dim teste As CarimboOptions
    If Err.Number = 0 Then
        resultado = resultado & "✓ Módulo VBA importado corretamente" & vbCrLf
    Else
        resultado = resultado & "✗ Módulo VBA não encontrado" & vbCrLf
        resultado = resultado & "  Importe o arquivo CarimboPDF_WordIntegration.bas" & vbCrLf
    End If
    On Error GoTo 0
    
    ' Verificar se há documento ativo
    If Not ActiveDocument Is Nothing Then
        resultado = resultado & "✓ Documento ativo encontrado" & vbCrLf
        
        If ActiveDocument.Saved And ActiveDocument.Path <> "" Then
            resultado = resultado & "✓ Documento salvo e com caminho válido" & vbCrLf
        Else
            resultado = resultado & "⚠ Documento não salvo ou sem caminho" & vbCrLf
        End If
    Else
        resultado = resultado & "⚠ Nenhum documento ativo" & vbCrLf
    End If
    
    resultado = resultado & vbCrLf & "Para teste completo, execute a macro TestCarimboPDF"
    
    MsgBox resultado, vbInformation, "Verificação CarimboPDF"
End Sub