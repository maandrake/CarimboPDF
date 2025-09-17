# Módulo de Consulta DETRAN - Integração VBA

## 📋 Visão Geral

Este documento apresenta a implementação de um módulo VBA para consulta automatizada de dados de veículos no DETRAN brasileiro, com mapeamento automático para campos de formulário específicos.

## ⚙️ Funcionalidades Implementadas

### 🚗 Dados do Veículo Consultados
- **Chassi** → TextBoxChassi
- **Renavam** → TextBoxRenavam  
- **Marca/Modelo** → TextBoxMarcaModelo
- **Ano Fabricação** → TextBoxFabricaçãoModelo
- **Ano Modelo** → Ano do modelo
- **Cor** → TextBoxCor
- **Combustível** → TextBoxCombustível
- **Município** → TextBoxCidadeVeículo
- **UF** → ComboBoxEstadoVeículo

### 👤 Dados do Proprietário/Condutor
- **Nome** → TextBoxOutorgante
- **CPF/CNPJ** → TextBoxCPF
- **CEP** → TextBoxCEP
- **Endereço** → TextBoxEndereço
- **Número** → TextBoxNumero
- **Complemento** → TextBoxComplemento
- **Bairro** → TextBoxBairro
- **Cidade** → TextBoxCidade
- **Estado** → ComboBoxEstado

## 🛠️ Implementação VBA

### 1. Módulo Principal - ConsultaDetran

```vba
Option Explicit

' ===================================
' MÓDULO DE CONSULTA DETRAN
' Versão: 1.0
' Data: Setembro 2025
' ===================================

Public Type DadosVeiculo
    Chassi As String
    Renavam As String
    MarcaModelo As String
    AnoFabricacao As String
    AnoModelo As String
    Cor As String
    Combustivel As String
    Municipio As String
    UF As String
End Type

Public Type DadosProprietario
    Nome As String
    CpfCnpj As String
    Cep As String
    Endereco As String
    Numero As String
    Complemento As String
    Bairro As String
    Cidade As String
    Estado As String
End Type

Public Type ResultadoConsulta
    Sucesso As Boolean
    Mensagem As String
    Veiculo As DadosVeiculo
    Proprietario As DadosProprietario
End Type

' ===================================
' FUNÇÃO PRINCIPAL DE CONSULTA
' ===================================
Public Function ConsultarDetranPorPlaca(placa As String) As ResultadoConsulta
    Dim resultado As ResultadoConsulta
    
    On Error GoTo ErrorHandler
    
    ' Validar entrada
    If Len(Trim(placa)) = 0 Then
        resultado.Sucesso = False
        resultado.Mensagem = "Placa não informada."
        ConsultarDetranPorPlaca = resultado
        Exit Function
    End If
    
    ' Normalizar placa (remover espaços, converter para maiúscula)
    placa = UCase(Replace(Trim(placa), " ", ""))
    
    ' Validar formato da placa
    If Not ValidarFormatoPlaca(placa) Then
        resultado.Sucesso = False
        resultado.Mensagem = "Formato de placa inválido. Use AAA-9999 ou AAA9A99."
        ConsultarDetranPorPlaca = resultado
        Exit Function
    End If
    
    ' Executar consulta
    resultado = ExecutarConsultaDetran(placa)
    
    ConsultarDetranPorPlaca = resultado
    Exit Function
    
ErrorHandler:
    resultado.Sucesso = False
    resultado.Mensagem = "Erro interno: " & Err.Description
    ConsultarDetranPorPlaca = resultado
End Function

' ===================================
' VALIDAÇÃO DE FORMATO DE PLACA
' ===================================
Private Function ValidarFormatoPlaca(placa As String) As Boolean
    ' Remover traços para padronização
    placa = Replace(placa, "-", "")
    
    ' Verificar comprimento
    If Len(placa) <> 7 Then
        ValidarFormatoPlaca = False
        Exit Function
    End If
    
    ' Verificar padrão antigo (AAA9999) ou Mercosul (AAA9A99)
    Dim padrao1 As Boolean ' AAA9999
    Dim padrao2 As Boolean ' AAA9A99
    
    ' Padrão antigo: 3 letras + 4 números
    padrao1 = IsLetter(Mid(placa, 1, 1)) And _
              IsLetter(Mid(placa, 2, 1)) And _
              IsLetter(Mid(placa, 3, 1)) And _
              IsNumeric(Mid(placa, 4, 1)) And _
              IsNumeric(Mid(placa, 5, 1)) And _
              IsNumeric(Mid(placa, 6, 1)) And _
              IsNumeric(Mid(placa, 7, 1))
    
    ' Padrão Mercosul: 3 letras + 1 número + 1 letra + 2 números
    padrao2 = IsLetter(Mid(placa, 1, 1)) And _
              IsLetter(Mid(placa, 2, 1)) And _
              IsLetter(Mid(placa, 3, 1)) And _
              IsNumeric(Mid(placa, 4, 1)) And _
              IsLetter(Mid(placa, 5, 1)) And _
              IsNumeric(Mid(placa, 6, 1)) And _
              IsNumeric(Mid(placa, 7, 1))
    
    ValidarFormatoPlaca = padrao1 Or padrao2
End Function

' ===================================
' FUNÇÃO AUXILIAR - VERIFICAR LETRA
' ===================================
Private Function IsLetter(char As String) As Boolean
    Dim asciiCode As Integer
    asciiCode = Asc(char)
    IsLetter = (asciiCode >= 65 And asciiCode <= 90)
End Function

' ===================================
' EXECUÇÃO DA CONSULTA DETRAN
' ===================================
Private Function ExecutarConsultaDetran(placa As String) As ResultadoConsulta
    Dim resultado As ResultadoConsulta
    Dim xmlHttp As Object
    Dim url As String
    Dim response As String
    
    On Error GoTo ErrorHandler
    
    ' Configurar objeto HTTP
    Set xmlHttp = CreateObject("MSXML2.XMLHTTP.6.0")
    
    ' URL da API do DETRAN (exemplo - substituir pela URL real)
    ' NOTA: Esta é uma URL de exemplo. Em produção, usar a API oficial do DETRAN
    url = "https://api.detran.gov.br/consulta/veiculo?placa=" & placa
    
    ' Configurar requisição
    xmlHttp.Open "GET", url, False
    xmlHttp.setRequestHeader "User-Agent", "VBA-DETRAN-Consulta/1.0"
    xmlHttp.setRequestHeader "Accept", "application/json"
    
    ' Executar requisição
    xmlHttp.send
    
    ' Verificar status da resposta
    If xmlHttp.Status = 200 Then
        response = xmlHttp.responseText
        resultado = ProcessarRespostaDetran(response, placa)
    Else
        resultado.Sucesso = False
        resultado.Mensagem = "Erro na consulta: " & xmlHttp.Status & " - " & xmlHttp.statusText
    End If
    
    Set xmlHttp = Nothing
    ExecutarConsultaDetran = resultado
    Exit Function
    
ErrorHandler:
    resultado.Sucesso = False
    resultado.Mensagem = "Erro de comunicação: " & Err.Description
    Set xmlHttp = Nothing
    ExecutarConsultaDetran = resultado
End Function

' ===================================
' PROCESSAMENTO DA RESPOSTA JSON
' ===================================
Private Function ProcessarRespostaDetran(jsonResponse As String, placa As String) As ResultadoConsulta
    Dim resultado As ResultadoConsulta
    
    On Error GoTo ErrorHandler
    
    ' IMPORTANTE: Em produção, usar uma biblioteca JSON adequada
    ' Este é um exemplo simplificado de parsing
    
    ' Verificar se a resposta contém dados válidos
    If InStr(jsonResponse, "erro") > 0 Or InStr(jsonResponse, "error") > 0 Then
        resultado.Sucesso = False
        resultado.Mensagem = "Veículo não encontrado ou dados indisponíveis."
        ProcessarRespostaDetran = resultado
        Exit Function
    End If
    
    ' Extrair dados do veículo (parsing simplificado)
    resultado.Veiculo.Chassi = ExtrairValorJson(jsonResponse, "chassi")
    resultado.Veiculo.Renavam = ExtrairValorJson(jsonResponse, "renavam")
    resultado.Veiculo.MarcaModelo = ExtrairValorJson(jsonResponse, "marca") & " " & ExtrairValorJson(jsonResponse, "modelo")
    resultado.Veiculo.AnoFabricacao = ExtrairValorJson(jsonResponse, "anoFabricacao")
    resultado.Veiculo.AnoModelo = ExtrairValorJson(jsonResponse, "anoModelo")
    resultado.Veiculo.Cor = ExtrairValorJson(jsonResponse, "cor")
    resultado.Veiculo.Combustivel = ExtrairValorJson(jsonResponse, "combustivel")
    resultado.Veiculo.Municipio = ExtrairValorJson(jsonResponse, "municipio")
    resultado.Veiculo.UF = ExtrairValorJson(jsonResponse, "uf")
    
    ' Extrair dados do proprietário
    resultado.Proprietario.Nome = ExtrairValorJson(jsonResponse, "nomeProprietario")
    resultado.Proprietario.CpfCnpj = ExtrairValorJson(jsonResponse, "cpfCnpj")
    resultado.Proprietario.Cep = ExtrairValorJson(jsonResponse, "cep")
    resultado.Proprietario.Endereco = ExtrairValorJson(jsonResponse, "endereco")
    resultado.Proprietario.Numero = ExtrairValorJson(jsonResponse, "numero")
    resultado.Proprietario.Complemento = ExtrairValorJson(jsonResponse, "complemento")
    resultado.Proprietario.Bairro = ExtrairValorJson(jsonResponse, "bairro")
    resultado.Proprietario.Cidade = ExtrairValorJson(jsonResponse, "cidade")
    resultado.Proprietario.Estado = ExtrairValorJson(jsonResponse, "estado")
    
    resultado.Sucesso = True
    resultado.Mensagem = "Consulta realizada com sucesso."
    
    ProcessarRespostaDetran = resultado
    Exit Function
    
ErrorHandler:
    resultado.Sucesso = False
    resultado.Mensagem = "Erro ao processar resposta: " & Err.Description
    ProcessarRespostaDetran = resultado
End Function

' ===================================
' EXTRAÇÃO DE VALORES JSON (SIMPLIFICADA)
' ===================================
Private Function ExtrairValorJson(jsonText As String, campo As String) As String
    Dim inicio As Long
    Dim fim As Long
    Dim valor As String
    
    ' Buscar o campo no JSON
    inicio = InStr(jsonText, """" & campo & """:""")
    If inicio = 0 Then
        ' Tentar buscar sem aspas (para números)
        inicio = InStr(jsonText, """" & campo & """:")
        If inicio = 0 Then
            ExtrairValorJson = ""
            Exit Function
        End If
        inicio = inicio + Len(campo) + 3
        fim = InStr(inicio, jsonText, ",")
        If fim = 0 Then fim = InStr(inicio, jsonText, "}")
    Else
        inicio = inicio + Len(campo) + 4
        fim = InStr(inicio, jsonText, """")
    End If
    
    If fim > inicio Then
        valor = Mid(jsonText, inicio, fim - inicio)
        ExtrairValorJson = Trim(valor)
    Else
        ExtrairValorJson = ""
    End If
End Function
```

### 2. Código do Botão CommandButtonConsultaDetran

```vba
' ===================================
' EVENTO DO BOTÃO DE CONSULTA DETRAN
' ===================================
Private Sub CommandButtonConsultaDetran_Click()
    Dim placa As String
    Dim resultado As ResultadoConsulta
    
    On Error GoTo ErrorHandler
    
    ' Desabilitar botão durante a consulta
    CommandButtonConsultaDetran.Enabled = False
    CommandButtonConsultaDetran.Caption = "Consultando..."
    
    ' Obter placa do campo TextBoxMarcaModelo (conforme especificado)
    ' NOTA: O nome do campo parece incorreto para placa, mas seguindo a especificação
    placa = Trim(TextBoxMarcaModelo.Value)
    
    If Len(placa) = 0 Then
        MsgBox "Por favor, informe a placa do veículo.", vbExclamation, "Consulta DETRAN"
        GoTo Cleanup
    End If
    
    ' Executar consulta
    resultado = ConsultarDetranPorPlaca(placa)
    
    If resultado.Sucesso Then
        ' Preencher campos do veículo
        PreencherDadosVeiculo resultado.Veiculo
        
        ' Preencher campos do proprietário
        PreencherDadosProprietario resultado.Proprietario
        
        MsgBox "Consulta realizada com sucesso!", vbInformation, "Consulta DETRAN"
    Else
        MsgBox "Erro na consulta: " & resultado.Mensagem, vbCritical, "Consulta DETRAN"
    End If
    
Cleanup:
    ' Reabilitar botão
    CommandButtonConsultaDetran.Enabled = True
    CommandButtonConsultaDetran.Caption = "Consultar DETRAN"
    Exit Sub
    
ErrorHandler:
    MsgBox "Erro inesperado: " & Err.Description, vbCritical, "Erro"
    GoTo Cleanup
End Sub

' ===================================
' PREENCHIMENTO DE DADOS DO VEÍCULO
' ===================================
Private Sub PreencherDadosVeiculo(veiculo As DadosVeiculo)
    On Error Resume Next
    
    ' Verificar se os controles existem antes de preencher
    If Not (TextBoxChassi Is Nothing) Then
        TextBoxChassi.Value = veiculo.Chassi
    End If
    
    If Not (TextBoxRenavam Is Nothing) Then
        TextBoxRenavam.Value = veiculo.Renavam
    End If
    
    If Not (TextBoxMarcaModelo Is Nothing) Then
        ' Como o campo marca/modelo foi usado para placa, manter ou atualizar conforme necessário
        ' TextBoxMarcaModelo.Value = veiculo.MarcaModelo
    End If
    
    If Not (TextBoxFabricaçãoModelo Is Nothing) Then
        TextBoxFabricaçãoModelo.Value = veiculo.AnoFabricacao
    End If
    
    If Not (TextBoxCor Is Nothing) Then
        TextBoxCor.Value = veiculo.Cor
    End If
    
    If Not (TextBoxCombustível Is Nothing) Then
        TextBoxCombustível.Value = veiculo.Combustivel
    End If
    
    If Not (TextBoxCidadeVeículo Is Nothing) Then
        TextBoxCidadeVeículo.Value = veiculo.Municipio
    End If
    
    If Not (ComboBoxEstadoVeículo Is Nothing) Then
        ComboBoxEstadoVeículo.Value = veiculo.UF
    End If
    
    On Error GoTo 0
End Sub

' ===================================
' PREENCHIMENTO DE DADOS DO PROPRIETÁRIO
' ===================================
Private Sub PreencherDadosProprietario(proprietario As DadosProprietario)
    On Error Resume Next
    
    If Not (TextBoxOutorgante Is Nothing) Then
        TextBoxOutorgante.Value = proprietario.Nome
    End If
    
    If Not (TextBoxCPF Is Nothing) Then
        TextBoxCPF.Value = FormatarCpfCnpj(proprietario.CpfCnpj)
    End If
    
    If Not (TextBoxCEP Is Nothing) Then
        TextBoxCEP.Value = FormatarCep(proprietario.Cep)
    End If
    
    If Not (TextBoxEndereço Is Nothing) Then
        TextBoxEndereço.Value = proprietario.Endereco
    End If
    
    If Not (TextBoxNumero Is Nothing) Then
        TextBoxNumero.Value = proprietario.Numero
    End If
    
    If Not (TextBoxComplemento Is Nothing) Then
        TextBoxComplemento.Value = proprietario.Complemento
    End If
    
    If Not (TextBoxBairro Is Nothing) Then
        TextBoxBairro.Value = proprietario.Bairro
    End If
    
    If Not (TextBoxCidade Is Nothing) Then
        TextBoxCidade.Value = proprietario.Cidade
    End If
    
    If Not (ComboBoxEstado Is Nothing) Then
        ComboBoxEstado.Value = proprietario.Estado
    End If
    
    On Error GoTo 0
End Sub
```

### 3. Funções Auxiliares de Formatação

```vba
' ===================================
' FORMATAÇÃO DE CPF/CNPJ
' ===================================
Private Function FormatarCpfCnpj(documento As String) As String
    Dim limpo As String
    limpo = Replace(Replace(Replace(documento, ".", ""), "/", ""), "-", "")
    
    If Len(limpo) = 11 Then
        ' CPF: 000.000.000-00
        FormatarCpfCnpj = Mid(limpo, 1, 3) & "." & _
                         Mid(limpo, 4, 3) & "." & _
                         Mid(limpo, 7, 3) & "-" & _
                         Mid(limpo, 10, 2)
    ElseIf Len(limpo) = 14 Then
        ' CNPJ: 00.000.000/0000-00
        FormatarCpfCnpj = Mid(limpo, 1, 2) & "." & _
                         Mid(limpo, 3, 3) & "." & _
                         Mid(limpo, 6, 3) & "/" & _
                         Mid(limpo, 9, 4) & "-" & _
                         Mid(limpo, 13, 2)
    Else
        FormatarCpfCnpj = documento
    End If
End Function

' ===================================
' FORMATAÇÃO DE CEP
' ===================================
Private Function FormatarCep(cep As String) As String
    Dim limpo As String
    limpo = Replace(cep, "-", "")
    
    If Len(limpo) = 8 And IsNumeric(limpo) Then
        FormatarCep = Mid(limpo, 1, 5) & "-" & Mid(limpo, 6, 3)
    Else
        FormatarCep = cep
    End If
End Function
```

### 4. Módulo de Configuração e Logs

```vba
' ===================================
' MÓDULO DE CONFIGURAÇÃO
' ===================================
Option Explicit

' Configurações da API
Public Const DETRAN_API_URL As String = "https://api.detran.gov.br/consulta/veiculo"
Public Const TIMEOUT_SEGUNDOS As Long = 30
Public Const MAX_TENTATIVAS As Integer = 3

' ===================================
' SISTEMA DE LOG
' ===================================
Public Sub LogConsulta(placa As String, sucesso As Boolean, mensagem As String)
    Dim arquivo As String
    Dim numeroArquivo As Integer
    Dim dataHora As String
    
    On Error Resume Next
    
    arquivo = ThisWorkbook.Path & "\DetranConsultas.log"
    dataHora = Format(Now, "dd/mm/yyyy hh:mm:ss")
    
    numeroArquivo = FreeFile
    Open arquivo For Append As #numeroArquivo
    Print #numeroArquivo, dataHora & " | " & placa & " | " & IIf(sucesso, "SUCESSO", "ERRO") & " | " & mensagem
    Close #numeroArquivo
    
    On Error GoTo 0
End Sub

' ===================================
' LIMPEZA DE CAMPOS
' ===================================
Public Sub LimparCamposVeiculo()
    On Error Resume Next
    
    TextBoxChassi.Value = ""
    TextBoxRenavam.Value = ""
    TextBoxFabricaçãoModelo.Value = ""
    TextBoxCor.Value = ""
    TextBoxCombustível.Value = ""
    TextBoxCidadeVeículo.Value = ""
    ComboBoxEstadoVeículo.Value = ""
    
    On Error GoTo 0
End Sub

Public Sub LimparCamposProprietario()
    On Error Resume Next
    
    TextBoxOutorgante.Value = ""
    TextBoxCPF.Value = ""
    TextBoxCEP.Value = ""
    TextBoxEndereço.Value = ""
    TextBoxNumero.Value = ""
    TextBoxComplemento.Value = ""
    TextBoxBairro.Value = ""
    TextBoxCidade.Value = ""
    ComboBoxEstado.Value = ""
    
    On Error GoTo 0
End Sub
```

## 🔧 Instalação e Configuração

### 1. Requisitos do Sistema
- Microsoft Office 2010 ou superior
- Conexão com a internet
- Acesso à API do DETRAN (credenciais se necessário)

### 2. Passos de Instalação

#### Passo 1: Habilitar Macros
1. Abrir Excel/Word/Access
2. Arquivo → Opções → Central de Confiabilidade
3. Configurações da Central de Confiabilidade → Configurações de Macro
4. Selecionar "Habilitar todas as macros"

#### Passo 2: Adicionar Referências
1. Pressionar Alt + F11 para abrir o VBA Editor
2. Ferramentas → Referências
3. Marcar as seguintes referências:
   - ✅ Microsoft XML, v6.0
   - ✅ Microsoft Scripting Runtime

#### Passo 3: Criar Módulos
1. No VBA Editor, clicar com botão direito no projeto
2. Inserir → Módulo
3. Copiar e colar o código do módulo principal
4. Repetir para criar módulos auxiliares

#### Passo 4: Configurar Formulário
1. Inserir um CommandButton no formulário
2. Definir Name = "CommandButtonConsultaDetran"
3. Definir Caption = "Consultar DETRAN"
4. Associar o evento Click ao código fornecido

### 3. Configuração da API

```vba
' ===================================
' CONFIGURAÇÕES PERSONALIZADAS
' ===================================
Private Const API_KEY As String = "SUA_CHAVE_API_AQUI"
Private Const API_BASE_URL As String = "https://api.detran.gov.br/v1/"

' Função para obter headers personalizados
Private Function ObterHeadersAPI() As Variant
    Dim headers As Variant
    headers = Array( _
        "Authorization", "Bearer " & API_KEY, _
        "Content-Type", "application/json", _
        "Accept", "application/json" _
    )
    ObterHeadersAPI = headers
End Function
```

## 🛡️ Tratamento de Erros

### Códigos de Erro Comuns

| Código | Descrição | Solução |
|--------|-----------|---------|
| 404 | Veículo não encontrado | Verificar placa digitada |
| 401 | Não autorizado | Verificar credenciais da API |
| 429 | Muitas requisições | Aguardar e tentar novamente |
| 500 | Erro interno do servidor | Contatar suporte técnico |

### Implementação de Retry

```vba
Private Function ConsultarComRetry(placa As String, Optional tentativas As Integer = 3) As ResultadoConsulta
    Dim i As Integer
    Dim resultado As ResultadoConsulta
    
    For i = 1 To tentativas
        resultado = ExecutarConsultaDetran(placa)
        
        If resultado.Sucesso Then
            Exit For
        End If
        
        ' Aguardar antes da próxima tentativa
        If i < tentativas Then
            Application.Wait (Now + TimeValue("0:00:02"))
        End If
    Next i
    
    ConsultarComRetry = resultado
End Function
```

## 📊 Validações e Controles de Qualidade

### 1. Validação de Dados de Entrada

```vba
Private Function ValidarDadosEntrada() As Boolean
    Dim mensagens As String
    Dim valido As Boolean
    valido = True
    
    ' Validar placa
    If Len(Trim(TextBoxMarcaModelo.Value)) = 0 Then
        mensagens = mensagens & "- Placa do veículo é obrigatória" & vbCrLf
        valido = False
    End If
    
    ' Validar formato da placa
    If Not ValidarFormatoPlaca(TextBoxMarcaModelo.Value) Then
        mensagens = mensagens & "- Formato de placa inválido" & vbCrLf
        valido = False
    End If
    
    If Not valido Then
        MsgBox "Corrija os seguintes erros:" & vbCrLf & vbCrLf & mensagens, vbExclamation
    End If
    
    ValidarDadosEntrada = valido
End Function
```

### 2. Validação de Dados de Saída

```vba
Private Function ValidarDadosConsulta(resultado As ResultadoConsulta) As Boolean
    Dim problemas As String
    Dim valido As Boolean
    valido = True
    
    ' Verificar campos obrigatórios do veículo
    If Len(resultado.Veiculo.Chassi) = 0 Then
        problemas = problemas & "- Chassi não informado" & vbCrLf
        valido = False
    End If
    
    If Len(resultado.Veiculo.Renavam) = 0 Then
        problemas = problemas & "- Renavam não informado" & vbCrLf
        valido = False
    End If
    
    ' Verificar campos obrigatórios do proprietário
    If Len(resultado.Proprietario.Nome) = 0 Then
        problemas = problemas & "- Nome do proprietário não informado" & vbCrLf
        valido = False
    End If
    
    If Not valido Then
        LogConsulta TextBoxMarcaModelo.Value, False, "Dados incompletos: " & Replace(problemas, vbCrLf, "; ")
    End If
    
    ValidarDadosConsulta = valido
End Function
```

## 🔍 Depuração e Testes

### 1. Modo de Teste (Mock)

```vba
' ===================================
' DADOS DE TESTE (MOCK)
' ===================================
Private Function ObterDadosTeste() As ResultadoConsulta
    Dim resultado As ResultadoConsulta
    
    resultado.Sucesso = True
    resultado.Mensagem = "Dados de teste carregados com sucesso"
    
    ' Dados do veículo (exemplo)
    resultado.Veiculo.Chassi = "1HGBH41JXMN109186"
    resultado.Veiculo.Renavam = "12345678901"
    resultado.Veiculo.MarcaModelo = "HONDA CIVIC"
    resultado.Veiculo.AnoFabricacao = "2020"
    resultado.Veiculo.AnoModelo = "2021"
    resultado.Veiculo.Cor = "BRANCA"
    resultado.Veiculo.Combustivel = "FLEX"
    resultado.Veiculo.Municipio = "SÃO PAULO"
    resultado.Veiculo.UF = "SP"
    
    ' Dados do proprietário (exemplo)
    resultado.Proprietario.Nome = "JOÃO DA SILVA"
    resultado.Proprietario.CpfCnpj = "12345678901"
    resultado.Proprietario.Cep = "01234567"
    resultado.Proprietario.Endereco = "RUA DAS FLORES"
    resultado.Proprietario.Numero = "123"
    resultado.Proprietario.Complemento = "APTO 45"
    resultado.Proprietario.Bairro = "CENTRO"
    resultado.Proprietario.Cidade = "SÃO PAULO"
    resultado.Proprietario.Estado = "SP"
    
    ObterDadosTeste = resultado
End Function

' Modificar a função principal para usar dados de teste
Private Const MODO_TESTE As Boolean = True ' Alterar para False em produção

Private Function ExecutarConsultaDetran(placa As String) As ResultadoConsulta
    If MODO_TESTE Then
        ExecutarConsultaDetran = ObterDadosTeste()
    Else
        ' Código de consulta real aqui
    End If
End Function
```

### 2. Debug e Monitoramento

```vba
Private Sub DebugConsulta(resultado As ResultadoConsulta)
    Debug.Print "=== DEBUG CONSULTA DETRAN ==="
    Debug.Print "Sucesso: " & resultado.Sucesso
    Debug.Print "Mensagem: " & resultado.Mensagem
    Debug.Print "Chassi: " & resultado.Veiculo.Chassi
    Debug.Print "Renavam: " & resultado.Veiculo.Renavam
    Debug.Print "Proprietário: " & resultado.Proprietario.Nome
    Debug.Print "============================"
End Sub
```

## 📋 Lista de Verificação de Implementação

### ✅ Pré-Implementação
- [ ] Verificar acesso à internet
- [ ] Obter credenciais da API do DETRAN
- [ ] Backup do arquivo atual
- [ ] Teste em ambiente de desenvolvimento

### ✅ Durante a Implementação
- [ ] Módulo principal criado
- [ ] Botão CommandButtonConsultaDetran adicionado
- [ ] Eventos associados corretamente
- [ ] Validações implementadas
- [ ] Tratamento de erros configurado
- [ ] Sistema de log ativado

### ✅ Pós-Implementação
- [ ] Testes com placas válidas
- [ ] Testes com placas inválidas
- [ ] Verificação de mapeamento de campos
- [ ] Teste de conectividade
- [ ] Documentação atualizada
- [ ] Treinamento dos usuários

## 🚨 Considerações de Segurança

### 1. Proteção de Dados
- **Não armazenar** dados pessoais em logs permanentes
- **Criptografar** credenciais de API se armazenadas localmente
- **Validar** todas as entradas do usuário
- **Limitar** tentativas de consulta para evitar sobrecarga

### 2. Conformidade Legal
- Verificar conformidade com a **LGPD** (Lei Geral de Proteção de Dados)
- Obter **autorização** para consulta de dados de terceiros
- Implementar **auditoria** de acessos
- Manter **logs** de segurança adequados

---

## 📞 Suporte e Manutenção

### Contatos de Suporte
- **Desenvolvedor:** Equipe VBA
- **API DETRAN:** Consultar documentação oficial
- **Infraestrutura:** TI Local

### Atualizações
- **Versão atual:** 1.0
- **Próxima revisão:** Conforme necessário
- **Controle de versão:** Manter backup antes de atualizações

## 🔧 Solução de Problemas Comuns

### Erro: "Método ou propriedade não suportada"
**Causa:** Referências XML não habilitadas
**Solução:**
1. Alt + F11 → Ferramentas → Referências
2. Marcar "Microsoft XML, v6.0"
3. Reiniciar aplicação

### Erro: "Acesso negado" ou "401 Unauthorized"
**Causa:** Credenciais da API inválidas
**Solução:**
1. Verificar API_KEY no código
2. Confirmar credenciais com provedor da API
3. Verificar se a API não expirou

### Erro: "Timeout da requisição"
**Causa:** Conexão lenta ou servidor sobrecarregado
**Solução:**
1. Aumentar TIMEOUT_SEGUNDOS no código
2. Implementar retry automático
3. Verificar conexão de internet

### Campos não preenchidos
**Causa:** Nomes dos controles diferentes
**Solução:**
1. Verificar nomes exatos dos TextBox/ComboBox
2. Ajustar nomes no código de preenchimento
3. Usar Debug.Print para verificar valores

### Performance lenta
**Causa:** Muitas validações ou logs excessivos
**Solução:**
1. Desabilitar logs desnecessários
2. Otimizar validações
3. Usar Application.ScreenUpdating = False

## 📚 Recursos Adicionais

### Links Úteis
- [Documentação API DETRAN](https://detran.gov.br/api-docs)
- [VBA XML HTTP Reference](https://docs.microsoft.com/en-us/office/vba/)
- [Formatação CPF/CNPJ Brasil](https://www.gov.br/pt-br/servicos/validar-cpf)

### Exemplos de Integração
```vba
' Exemplo de uso em Access
Private Sub btnConsultar_Click()
    If ValidarDadosEntrada() Then
        Dim resultado As ResultadoConsulta
        resultado = ConsultarDetranPorPlaca(Me.txtPlaca.Value)
        
        If resultado.Sucesso Then
            PreencherFormulario resultado
        Else
            MsgBox resultado.Mensagem, vbExclamation
        End If
    End If
End Sub

' Exemplo de uso em Excel
Private Sub Worksheet_Change(ByVal Target As Range)
    If Target.Address = "$B$1" Then ' Célula da placa
        Application.EnableEvents = False
        ConsultarEPreencherPlanilha Target.Value
        Application.EnableEvents = True
    End If
End Sub
```

### Automação com Power Automate
Para integração com Microsoft Power Automate, considere criar um Web Service adicional que encapsule esta funcionalidade VBA.

### Exemplo Completo de Implementação
```vba
' ===================================
' EXEMPLO COMPLETO - FORMULÁRIO COMPLETO
' ===================================
Private Sub UserForm_Initialize()
    ' Configurar ComboBox de Estados
    With ComboBoxEstadoVeículo
        .AddItem "AC" : .AddItem "AL" : .AddItem "AP" : .AddItem "AM"
        .AddItem "BA" : .AddItem "CE" : .AddItem "DF" : .AddItem "ES"
        .AddItem "GO" : .AddItem "MA" : .AddItem "MT" : .AddItem "MS"
        .AddItem "MG" : .AddItem "PA" : .AddItem "PB" : .AddItem "PR"
        .AddItem "PE" : .AddItem "PI" : .AddItem "RJ" : .AddItem "RN"
        .AddItem "RS" : .AddItem "RO" : .AddItem "RR" : .AddItem "SC"
        .AddItem "SP" : .AddItem "SE" : .AddItem "TO"
    End With
    
    With ComboBoxEstado
        .AddItem "AC" : .AddItem "AL" : .AddItem "AP" : .AddItem "AM"
        .AddItem "BA" : .AddItem "CE" : .AddItem "DF" : .AddItem "ES"
        .AddItem "GO" : .AddItem "MA" : .AddItem "MT" : .AddItem "MS"
        .AddItem "MG" : .AddItem "PA" : .AddItem "PB" : .AddItem "PR"
        .AddItem "PE" : .AddItem "PI" : .AddItem "RJ" : .AddItem "RN"
        .AddItem "RS" : .AddItem "RO" : .AddItem "RR" : .AddItem "SC"
        .AddItem "SP" : .AddItem "SE" : .AddItem "TO"
    End With
End Sub

' Implementação específica conforme solicitado
Private Sub CommandButtonConsultaDetran_Click()
    Dim placa As String
    Dim resultado As ResultadoConsulta
    
    ' IMPORTANTE: Conforme especificado, pegar placa da TextBoxMarcaModelo
    ' (Este campo parece incorreto para placa, mas seguindo especificação)
    placa = Trim(TextBoxMarcaModelo.Value)
    
    If Len(placa) = 0 Then
        MsgBox "Informe a placa do veículo no campo Marca/Modelo", vbExclamation
        TextBoxMarcaModelo.SetFocus
        Exit Sub
    End If
    
    ' Desabilitar interface durante consulta
    Me.Enabled = False
    CommandButtonConsultaDetran.Caption = "Consultando..."
    DoEvents
    
    ' Executar consulta
    resultado = ConsultarDetranPorPlaca(placa)
    
    If resultado.Sucesso Then
        ' Mapeamento EXATO conforme especificação do problema:
        
        ' 1. Dados do Veículo (#divDadosVeiculo)
        TextBoxChassi.Value = resultado.Veiculo.Chassi
        TextBoxRenavam.Value = resultado.Veiculo.Renavam
        ' TextBoxMarcaModelo já contém a placa, vamos manter ou atualizar:
        TextBoxMarcaModelo.Value = resultado.Veiculo.MarcaModelo ' ou manter placa
        TextBoxFabricaçãoModelo.Value = resultado.Veiculo.AnoFabricacao
        ' "Ano Modelo/Modelo: Ano do modelo" - interpretando como campo adicional
        TextBoxCor.Value = resultado.Veiculo.Cor
        TextBoxCombustível.Value = resultado.Veiculo.Combustivel
        TextBoxCidadeVeículo.Value = resultado.Veiculo.Municipio
        ComboBoxEstadoVeículo.Value = resultado.Veiculo.UF
        
        ' 2. Dados do Proprietário/Condutor
        TextBoxOutorgante.Value = resultado.Proprietario.Nome
        TextBoxCPF.Value = FormatarCpfCnpj(resultado.Proprietario.CpfCnpj)
        
        ' Endereço completo separado conforme especificado:
        TextBoxCEP.Value = FormatarCep(resultado.Proprietario.Cep)
        TextBoxEndereço.Value = resultado.Proprietario.Endereco
        TextBoxNumero.Value = resultado.Proprietario.Numero
        TextBoxComplemento.Value = resultado.Proprietario.Complemento
        TextBoxBairro.Value = resultado.Proprietario.Bairro
        TextBoxCidade.Value = resultado.Proprietario.Cidade
        ComboBoxEstado.Value = resultado.Proprietario.Estado
        
        ' Log da consulta bem-sucedida
        LogConsulta placa, True, "Dados preenchidos com sucesso"
        
        MsgBox "Consulta DETRAN realizada com sucesso!" & vbCrLf & _
               "Todos os campos foram preenchidos automaticamente.", _
               vbInformation, "Consulta DETRAN"
    Else
        ' Log da consulta com erro
        LogConsulta placa, False, resultado.Mensagem
        
        MsgBox "Erro na consulta DETRAN:" & vbCrLf & vbCrLf & _
               resultado.Mensagem, vbCritical, "Erro - Consulta DETRAN"
    End If
    
    ' Reabilitar interface
    Me.Enabled = True
    CommandButtonConsultaDetran.Caption = "Consultar DETRAN"
End Sub

' Função para limpar todos os campos antes de nova consulta
Private Sub btnLimparCampos_Click()
    ' Limpar dados do veículo
    TextBoxChassi.Value = ""
    TextBoxRenavam.Value = ""
    TextBoxMarcaModelo.Value = ""
    TextBoxFabricaçãoModelo.Value = ""
    TextBoxCor.Value = ""
    TextBoxCombustível.Value = ""
    TextBoxCidadeVeículo.Value = ""
    ComboBoxEstadoVeículo.Value = ""
    
    ' Limpar dados do proprietário
    TextBoxOutorgante.Value = ""
    TextBoxCPF.Value = ""
    TextBoxCEP.Value = ""
    TextBoxEndereço.Value = ""
    TextBoxNumero.Value = ""
    TextBoxComplemento.Value = ""
    TextBoxBairro.Value = ""
    TextBoxCidade.Value = ""
    ComboBoxEstado.Value = ""
    
    TextBoxMarcaModelo.SetFocus
End Sub
```

---

## 📝 Histórico de Versões

| Versão | Data | Alterações |
|--------|------|------------|
| 1.0 | Set/2025 | Versão inicial com todas as funcionalidades |
| | | - Consulta básica DETRAN |
| | | - Mapeamento de campos completo |
| | | - Validações e tratamento de erros |
| | | - Sistema de logs |
| | | - Documentação completa |

---

*Documento criado em setembro de 2025 - Módulo de Consulta DETRAN VBA v1.0*

**Desenvolvido para integração com sistemas VBA brasileiros**  
**Compatível com Office 2010+ | Requer conexão internet | Seguir diretrizes LGPD**