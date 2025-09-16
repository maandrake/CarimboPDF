# CarimboPDF - Integração com Microsoft Word VBA

## ✨ Visão Geral

Este guia mostra como integrar o CarimboPDF com Microsoft Word VBA, permitindo que você carimbem documentos PDF diretamente do Word usando macros em Visual Basic for Applications.

### 🎯 Funcionalidades da Integração

- ✅ **Conversão automática**: Word → PDF → Carimbo → PDF final
- ✅ **Interface VBA nativa**: Funções simples de chamar em macros
- ✅ **Configuração flexível**: Todas as opções do CarimboPDF disponíveis
- ✅ **Tratamento de erro robusto**: Mensagens claras para depuração
- ✅ **Compatibilidade total**: Funciona com Word 2016+ e Office 365

## 🚀 Instalação Rápida

### 1. Configuração Automática (Recomendada)

Execute como **administrador**:
```cmd
Configurar_Word_VBA.cmd
```

Este script:
- ✅ Verifica dependências Python
- ✅ Instala bibliotecas necessárias
- ✅ Testa a funcionalidade
- ✅ Copia arquivos para local apropriado
- ✅ Fornece instruções detalhadas

### 2. Configuração Manual

Se preferir configurar manualmente:

```cmd
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Testar funcionalidade
python scripts\make_dummy_pdf.py
python carimbo_vba_wrapper.py --input dummy.pdf --cidade "São Paulo" --vba-output

# 3. Importar módulo VBA no Word
# - Abrir Word → Alt+F11 → Arquivo → Importar → CarimboPDF_WordIntegration.bas
```

## 📋 Configuração no Word

### Passo 1: Importar Módulo VBA

1. **Abrir Word**
2. **Pressionar Alt+F11** (abre Editor VBA)
3. **Menu Arquivo → Importar Arquivo...**
4. **Selecionar**: `CarimboPDF_WordIntegration.bas`
5. **Confirmar importação**

### Passo 2: Configurar Segurança (se necessário)

1. **Word → Arquivo → Opções → Central de Confiabilidade**
2. **Configurações da Central de Confiabilidade**
3. **Configurações de Macro → Habilitar todas as macros**
4. **✅ Confiar no acesso ao modelo de objeto do projeto VBA**

## 💻 Uso Básico

### Exemplo 1: Carimbo Simples

```vba
Sub MeuCarimboSimples()
    ' Carimba o documento ativo com configurações padrão
    Call CarimbarDocumentoSimples()
End Sub
```

### Exemplo 2: Carimbo Personalizado

```vba
Sub MeuCarimboPersonalizado()
    Dim opcoes As CarimboOptions
    
    ' Configurar opções
    opcoes = CriarOpcoesPadrao()
    opcoes.Cidade = "Rio de Janeiro"
    opcoes.FonteSize = "14"
    opcoes.Negrito = True
    opcoes.Cor = "#0000FF"  ' Azul
    
    ' Aplicar carimbo
    Call CarimbarDocumentoAtivo(opcoes)
End Sub
```

### Exemplo 3: Carimbo com Proteção

```vba
Sub MeuCarimboProtegido()
    Dim opcoes As CarimboOptions
    Dim senha As String
    
    ' Solicitar senha
    senha = InputBox("Senha para proteger o PDF:", "CarimboPDF")
    If senha = "" Then Exit Sub
    
    ' Configurar proteção
    opcoes = CriarOpcoesPadrao()
    opcoes.SenhaProtecao = senha
    opcoes.RestringirEdicao = True
    opcoes.DesativarCopia = True
    opcoes.CriptografarConteudo = True
    
    ' Aplicar carimbo protegido
    Call CarimbarDocumentoAtivo(opcoes)
End Sub
```

## ⚙️ Opções Avançadas

### Estrutura CarimboOptions

```vba
Public Type CarimboOptions
    Cidade As String                ' "São Paulo", "Rio de Janeiro", etc.
    FonteSize As String            ' "12", "14", "16", etc.
    Fonte As String                ' "helv", "times", "cour"
    Cor As String                  ' "#000000", "#FF0000", "#0000FF"
    Negrito As Boolean             ' True/False
    Italico As Boolean             ' True/False
    Pagina As Long                 ' 1, 2, 3, etc. (1 = primeira página)
    SenhaProtecao As String        ' Senha para edição
    RestringirEdicao As Boolean    ' True/False
    DesativarCopia As Boolean      ' True/False
    CriptografarConteudo As Boolean ' True/False
    CaminhoLogo As String          ' "C:\logo.png" ou ""
    LarguraLogoCm As String        ' "2.0", "3.5", etc.
    MargemLogoCm As String         ' "0.5", "1.0", etc.
End Type
```

### Exemplo Completo com Todas as Opções

```vba
Sub CarimboCompleto()
    Dim opcoes As CarimboOptions
    
    ' Configurar todas as opções
    opcoes.Cidade = "Brasília"
    opcoes.FonteSize = "16"
    opcoes.Fonte = "times"
    opcoes.Cor = "#800080"  ' Roxo
    opcoes.Negrito = True
    opcoes.Italico = False
    opcoes.Pagina = 1
    opcoes.SenhaProtecao = "minhasenha123"
    opcoes.RestringirEdicao = True
    opcoes.DesativarCopia = False
    opcoes.CriptografarConteudo = True
    opcoes.CaminhoLogo = "C:\MeuLogo\logo.png"
    opcoes.LarguraLogoCm = "3.0"
    opcoes.MargemLogoCm = "1.0"
    
    ' Aplicar carimbo
    If CarimbarDocumentoAtivo(opcoes) Then
        MsgBox "Carimbo aplicado com sucesso!", vbInformation
    Else
        MsgBox "Falha ao aplicar carimbo.", vbCritical
    End If
End Sub
```

## 🔧 Solução de Problemas

### ❌ "Script Python não encontrado"

**Causa**: Caminho do script não localizado automaticamente

**Solução**:
```vba
' Editar função ObterCaminhoScript() no módulo VBA
' Adicionar caminho específico:
ObterCaminhoScript = "C:\CaminhoCorreto\CarimboPDF\carimbo_vba_wrapper.py"
```

### ❌ "Python não está instalado"

**Causa**: Python não está no PATH do sistema

**Soluções**:
1. **Reinstalar Python** com opção "Add to PATH" marcada
2. **Ou modificar comando VBA**:
```vba
' Em ConstruirComandoPython(), trocar "python" por caminho completo:
comando = "C:\Python39\python.exe """ & scriptPath & """"
```

### ❌ "Erro de permissão"

**Causa**: Arquivo PDF aberto em outro programa

**Soluções**:
1. Fechar PDF em visualizadores (Adobe, Chrome, etc.)
2. Salvar documento Word antes de carimbar
3. Verificar permissões da pasta de destino

### ❌ "Dependências não encontradas"

**Causa**: Bibliotecas Python não instaladas

**Solução**:
```cmd
pip install --upgrade pymupdf Pillow
```

### 🐛 Debug de Problemas

Para diagnosticar problemas, adicione debug no VBA:

```vba
' Adicionar no início da função AplicarCarimbo():
Debug.Print "Comando: " & comando
Debug.Print "Script Path: " & scriptPath
Debug.Print "PDF Path: " & caminhoPDF
```

Visualizar saída: **Ctrl+G** no Editor VBA → Janela Imediata

## 📁 Estrutura de Arquivos

```
CarimboPDF/
├── CarimboPDF_WordIntegration.bas    # Módulo VBA principal
├── carimbo_vba_wrapper.py            # Wrapper Python otimizado
├── Configurar_Word_VBA.cmd           # Script de configuração
├── src/data_hora_pdf/                # Código principal Python
├── Logo.jpg                          # Logo padrão (opcional)
└── requirements.txt                  # Dependências Python
```

## 🌐 Compatibilidade

### Versões Suportadas
- ✅ **Microsoft Word 2016+**
- ✅ **Office 365**
- ✅ **Python 3.8+**
- ✅ **Windows 10/11**

### Limitações
- ⚠️ **VBA requer Windows** (não funciona em Word Online)
- ⚠️ **Necessita Python instalado** localmente
- ⚠️ **Requer permissões de macro** habilitadas

## 🔒 Considerações de Segurança

### Macros Seguras
- ✅ **Código fonte aberto** - pode revisar antes de usar
- ✅ **Sem acesso à rede** - trabalha apenas com arquivos locais
- ✅ **Não modifica sistema** - apenas processa PDFs

### Boas Práticas
1. **Manter Python atualizado**
2. **Usar senhas fortes** para proteção de PDF
3. **Backup documentos** importantes antes de carimbar
4. **Testar em ambiente de desenvolvimento** primeiro

## 📊 Exemplos de Integração

### Carimbo em Lote

```vba
Sub CarimbarPastaCompleta()
    Dim pasta As String
    Dim arquivo As String
    Dim opcoes As CarimboOptions
    
    ' Configurar opções
    opcoes = CriarOpcoesPadrao()
    opcoes.Cidade = "São Paulo"
    
    ' Selecionar pasta
    pasta = "C:\MeusDocumentos\"
    arquivo = Dir(pasta & "*.docx")
    
    ' Processar todos os arquivos .docx
    Do While arquivo <> ""
        Call CarimbarDocumento(pasta & arquivo, _
                              Replace(pasta & arquivo, ".docx", ".pdf"), opcoes)
        arquivo = Dir()
    Loop
    
    MsgBox "Processamento em lote concluído!", vbInformation
End Sub
```

### Interface de Usuario

```vba
Sub CarimboComInterface()
    Dim cidade As String
    Dim fontSize As String
    Dim usarSenha As VbMsgBoxResult
    Dim opcoes As CarimboOptions
    
    ' Coletar informações do usuário
    cidade = InputBox("Digite a cidade:", "CarimboPDF", "São Paulo")
    If cidade = "" Then Exit Sub
    
    fontSize = InputBox("Tamanho da fonte (8-24):", "CarimboPDF", "12")
    If fontSize = "" Then fontSize = "12"
    
    usarSenha = MsgBox("Deseja proteger o PDF com senha?", vbYesNo, "CarimboPDF")
    
    ' Configurar opções
    opcoes = CriarOpcoesPadrao()
    opcoes.Cidade = cidade
    opcoes.FonteSize = fontSize
    
    If usarSenha = vbYes Then
        opcoes.SenhaProtecao = InputBox("Digite a senha:", "CarimboPDF")
        opcoes.RestringirEdicao = True
    End If
    
    ' Aplicar carimbo
    Call CarimbarDocumentoAtivo(opcoes)
End Sub
```

---

## 📞 Suporte

Para dúvidas ou problemas:

1. **Consulte primeiro** este guia completo
2. **Verifique logs** na Janela Imediata do VBA (Ctrl+G)
3. **Teste wrapper Python** manualmente:
   ```cmd
   python carimbo_vba_wrapper.py --input teste.pdf --cidade "São Paulo" --vba-output
   ```

### Status do Projeto
- 🟢 **Ativo** - Mantido regularmente
- 🟢 **Estável** - Testado em ambiente de produção
- 🟢 **Compatível** - Word 2016+ e Office 365

**Versão**: 1.0 - Setembro 2025