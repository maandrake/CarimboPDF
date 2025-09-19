# Integração VBA 7.1 com Word - CarimboPDF

## Visão Geral

Este documento descreve a implementação da integração entre VBA 7.1 no Microsoft Word e o sistema CarimboPDF para consulta de dados de veículos através do DETRAN.

## Arquitetura da Solução

### Componentes Principais

1. **API REST Local** (`vba_integration.py`)
   - Microserviço HTTP local em Python Flask
   - Endpoints para consulta de veículos
   - Gerenciamento de sessão e autenticação
   - Porta padrão: 8080

2. **CLI Offline** (`vehicle_query_cli.py`)
   - Ferramenta de linha de comando
   - Suporte a processamento em lote
   - Múltiplos formatos de saída (JSON, texto, CSV)

3. **Módulos VBA** (`CarimboPDF_VehicleQuery.bas`)
   - Comunicação HTTP com API
   - Estruturas de dados para veículos
   - Funções de integração com Word

4. **Formulário Word** (`VehicleQueryForm.frm`)
   - Interface gráfica no Word
   - Campos de entrada e exibição
   - Integração com documento ativo

## Instalação e Configuração

### Pré-requisitos

- Python 3.10+ com pip
- Microsoft Word com VBA habilitado
- Conexão com internet (para consultas DETRAN)

### Instalação do Backend

```bash
# Clonar/baixar o projeto CarimboPDF
cd CarimboPDF

# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar PYTHONPATH
export PYTHONPATH="$PWD/src"  # Linux/macOS
set PYTHONPATH=%CD%\src       # Windows
```

### Configuração do VBA

1. **Importar Módulos VBA:**
   - Abrir Word
   - Pressionar Alt+F11 para abrir o Editor VBA
   - Arquivo → Importar → Selecionar `vba/CarimboPDF_VehicleQuery.bas`

2. **Importar Formulário (Opcional):**
   - No Editor VBA: Arquivo → Importar → Selecionar `vba/VehicleQueryForm.frm`

3. **Configurar Referências:**
   - No Editor VBA: Ferramentas → Referências
   - Marcar "Microsoft XML, v6.0" (ou versão disponível)

## Uso da Solução

### Iniciar o Serviço API

```bash
# Método 1: Direto
python -m data_hora_pdf.vba_integration --port 8080

# Método 2: Com configuração personalizada
python -m data_hora_pdf.vba_integration --port 8080 --debug
```

### Usar no Word VBA

```vba
' Exemplo básico de consulta
Sub ExemploConsultaVeiculo()
    Dim vehicle As VehicleData
    vehicle = ConsultarPlaca("ABC1234", "SC")
    
    ExibirDadosVeiculo vehicle
    InserirDadosNoDocumento vehicle
End Sub

' Teste com formulário
Sub AbrirFormularioConsulta()
    VehicleQueryForm.Show
End Sub
```

### Usar CLI Offline

```bash
# Consulta simples
python -m data_hora_pdf.vehicle_query_cli --placa ABC1234 --uf SC

# Salvar em arquivo
python -m data_hora_pdf.vehicle_query_cli --placa ABC1234 --output veiculo.json

# Formato texto legível
python -m data_hora_pdf.vehicle_query_cli --placa ABC1234 --format text

# Processamento em lote
python -m data_hora_pdf.vehicle_query_cli --batch placas.txt --output resultados.json
```

## Endpoints da API

### GET /health
Verificação de status do serviço.

**Resposta:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "CarimboPDF-VBA-Integration"
  }
}
```

### POST /consulta/placa
Consulta dados de veículo por placa.

**Requisição:**
```json
{
  "placa": "ABC1234",
  "uf": "SC"
}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "placa": "ABC1234",
    "uf": "SC",
    "marca": "VOLKSWAGEN",
    "modelo": "GOL",
    "ano_fabricacao": 2020,
    "ano_modelo": 2020,
    "cor": "BRANCA",
    "combustivel": "FLEX",
    "categoria": "PARTICULAR",
    "proprietario": "PROPRIETÁRIO EXEMPLO",
    "municipio": "FLORIANÓPOLIS",
    "situacao": "REGULAR",
    "consulta_timestamp": "2025-09-19T19:10:11.549763"
  }
}
```

### POST /auth/login
Autenticação com sistema DETRAN.

**Requisição:**
```json
{
  "username": "usuario",
  "password": "senha"
}
```

## Configuração

### Arquivos de Configuração

1. **SGDW-ConsultaSC.ini** - Configurações legadas
2. **.env** - Variáveis de ambiente
3. **appsettings.json** - Configurações JSON estruturadas

### Parâmetros Principais

- `DETRAN_URL`: URL base do sistema DETRAN
- `API_PORT`: Porta do serviço REST (padrão: 8080)
- `HEADLESS_MODE`: Modo sem interface gráfica do navegador
- `DEFAULT_UF`: Estado padrão para consultas
- `LOG_LEVEL`: Nível de log (DEBUG, INFO, WARNING, ERROR)

## Tratamento de Erros

### Códigos de Erro Comuns

- `INVALID_REQUEST`: Dados de entrada inválidos
- `INVALID_PLATE`: Formato de placa incorreto
- `VEHICLE_NOT_FOUND`: Veículo não encontrado
- `LOGIN_FAILED`: Falha na autenticação
- `INTERNAL_ERROR`: Erro interno do servidor

### Mensagens no VBA

```vba
On Error GoTo ErrorHandler
' ... código ...
Exit Sub

ErrorHandler:
Select Case Err.Number
    Case vbObjectError + 1002
        MsgBox "Veículo não encontrado", vbExclamation
    Case vbObjectError + 1003
        MsgBox "Dados inválidos", vbExclamation
    Case Else
        MsgBox "Erro: " & Err.Description, vbCritical
End Select
```

## Segurança

### Autenticação
- Suporte a login com credenciais DETRAN
- Gerenciamento de sessão com timeout
- Renovação automática de sessão

### Comunicação
- API local apenas (127.0.0.1)
- HTTPS opcional para produção
- Validação de dados de entrada

### Logging
- Registro de todas as consultas
- Não armazenamento de senhas em logs
- Rotação automática de arquivos de log

## Monitoramento

### Logs
- Arquivo: `logs/carimbopdf-vba.log`
- Rotação: 10MB por arquivo, máximo 5 arquivos
- Formato: timestamp, nível, mensagem

### Métricas
- Número de consultas realizadas
- Tempo de resposta médio
- Taxa de sucesso/erro
- Status da sessão DETRAN

## Solução de Problemas

### Problema: "Serviço indisponível"
**Causa:** API não está rodando  
**Solução:** Iniciar o serviço com `python -m data_hora_pdf.vba_integration`

### Problema: "Veículo não encontrado"
**Causa:** Placa inexistente ou erro no DETRAN  
**Solução:** Verificar placa e tentar novamente

### Problema: "Erro de autenticação"
**Causa:** Credenciais inválidas ou sessão expirada  
**Solução:** Verificar credenciais ou fazer novo login

### Problema: "Timeout na consulta"
**Causa:** Rede lenta ou sobrecarga do DETRAN  
**Solução:** Aumentar timeout na configuração

## Exemplo Completo

### Configurar e Executar

```bash
# 1. Iniciar API
python -m data_hora_pdf.vba_integration --port 8080

# 2. Testar conectividade
curl http://127.0.0.1:8080/health

# 3. Consultar veículo
curl -X POST http://127.0.0.1:8080/consulta/placa \
  -H "Content-Type: application/json" \
  -d '{"placa": "ABC1234", "uf": "SC"}'
```

### Código VBA Completo

```vba
Sub ConsultaCompleta()
    ' Verificar conectividade
    If Not VerificarServicoDisponivel() Then
        MsgBox "Serviço indisponível"
        Exit Sub
    End If
    
    ' Fazer login
    If Not FazerLogin() Then
        MsgBox "Falha no login"
        Exit Sub
    End If
    
    ' Consultar veículo
    Dim vehicle As VehicleData
    vehicle = ConsultarPlaca("ABC1234", "SC")
    
    ' Inserir no documento
    InserirDadosNoDocumento vehicle
End Sub
```

## Suporte e Manutenção

Para suporte técnico ou reportar problemas:
1. Verificar logs em `logs/carimbopdf-vba.log`
2. Testar conectividade com `--test-connection`
3. Consultar documentação de APIs do DETRAN
4. Verificar configurações de rede e firewall