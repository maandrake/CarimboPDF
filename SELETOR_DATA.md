# Seletor de Data Personalizada - CarimboPDF

## ✅ Funcionalidades Implementadas

### 🗓️ **Seletor de Data na Interface Gráfica**
- **Widget de calendário** usando tkcalendar (DateEntry)
- **Checkbox "Usar data personalizada"** para ativar/desativar
- **Validação automática** - não permite datas futuras
- **Fallback inteligente** - se tkcalendar não estiver disponível, usa campo de texto
- **Estado inicial desabilitado** - só ativa quando marcado pelo usuário

### 🖥️ **Interface Visual**
- Checkbox: "☐ Usar data personalizada:"
- Widget calendário ao lado (habilitado/desabilitado conforme checkbox)
- Formato brasileiro: DD/MM/AAAA
- Cores personalizadas: fundo azul escuro, texto branco
- Largura otimizada: 12 caracteres

### 💻 **Linha de Comando (CLI)**
- Novo parâmetro: `--date DD/MM/AAAA`
- **Exemplo:** `python -m data_hora_pdf.cli --input doc.pdf --output result.pdf --cidade "São Paulo" --date "01/08/2025"`
- **Validação:** Rejeita datas futuras com mensagem de erro clara
- **Formato:** Aceita apenas DD/MM/AAAA (ex: 01/08/2025)

### 🔒 **Validações de Segurança**
- ✅ **Data futura rejeitada** tanto na GUI quanto no CLI
- ✅ **Formato de data validado** (DD/MM/AAAA)
- ✅ **Data máxima:** Hoje (não permite futuro)
- ✅ **Fallback:** Se data inválida, usa data de hoje com aviso

### 💾 **Persistência**
- ✅ **Configuração salva:** Checkbox "usar data personalizada"
- ✅ **Data salva:** Última data selecionada (se válida)
- ✅ **Carregamento inteligente:** Verifica se data salva não é futura
- ✅ **Formato JSON:** Data armazenada como "YYYY-MM-DD"

## 🧪 Exemplos de Uso

### Interface Gráfica:
1. Abrir aplicação: `CarimboPDF_GUI.pyw`
2. Marcar "☐ Usar data personalizada"
3. Clicar no campo de data para abrir calendário
4. Selecionar data desejada (não futura)
5. Configurar outros campos normalmente
6. Clicar "Carimbar"

### Linha de Comando:
```powershell
# Data personalizada válida
python -m data_hora_pdf.cli --input doc.pdf --output result.pdf --cidade "São Paulo" --date "15/08/2025"

# Data de hoje (comportamento padrão)
python -m data_hora_pdf.cli --input doc.pdf --output result.pdf --cidade "São Paulo"

# Erro: data futura
python -m data_hora_pdf.cli --input doc.pdf --output result.pdf --cidade "São Paulo" --date "31/12/2025"
# Resultado: "error: A data não pode ser futura."
```

## 🔧 Dependências Adicionadas
- **tkcalendar==1.6.1** - Widget de calendário moderno
- **babel** - Dependência do tkcalendar para localização

## 📋 Arquivo de Configuração Atualizado

```json
{
  "inplace": true,
  "cidade": "São Paulo",
  "page": 0,
  "font_size": 12.0,
  "font": "helv",
  "color": "#000000",
  "bold": false,
  "italic": false,
  "logo_path": "",
  "logo_width_cm": 2.0,
  "logo_margin_cm": 0.5,
  "restrict_editing": false,
  "no_copy": false,
  "encrypt_content": false,
  "save_password": false,
  "use_custom_date": true,           // NOVO
  "custom_date": "2025-08-15"        // NOVO
}
```

## 🎯 Casos de Uso

### 1. **Documentos Retroativos**
- Contratos assinados em data anterior
- Atas de reunião de datas passadas
- Documentos com data específica necessária

### 2. **Conformidade Legal**
- Documentos que precisam refletir data real do evento
- Assinaturas eletrônicas com data específica
- Registros históricos com data correta

### 3. **Workflow de Documentos**
- Processamento em lote de documentos antigos
- Correção de datas em documentos existentes
- Padronização de datas em arquivos históricos

## 🛡️ Segurança e Validação

### Validações Implementadas:
- ✅ **Formato de data:** Aceita apenas DD/MM/AAAA
- ✅ **Data futura:** Rejeitada com erro claro
- ✅ **Data inválida:** Tratamento de exceção com fallback
- ✅ **Calendário limitado:** MaxDate = hoje

### Comportamento Defensivo:
- Se tkcalendar não estiver instalado: usa campo texto
- Se data for inválida: usa data de hoje + aviso
- Se data for futura: rejeita com erro explicativo
- Se data salva for futura: carrega data de hoje

## 📊 Layout da Interface Atualizada

```
┌─────────────────────────────────────┐
│           Carimbar PDF              │
├─────────────────────────────────────┤
│ PDF entrada: [____] [Selecionar]    │
│ PDF saída:   [____] [Salvar]        │
│ ☑ Salvar no mesmo arquivo           │
│                                     │
│ Cidade: [São Paulo____________]     │
│ Página: [0]                         │
│ ☐ Usar data personalizada: [📅]     │  ← NOVO
│                                     │
│ Tamanho fonte: [12] Fonte: [helv]   │
│ Cor: [#000000] ☐Negrito ☐Itálico   │
│                                     │
│ Logo: [____] [Selecionar]           │
│ Largura: [2.0] Margem: [0.5]        │
│                                     │
│ ═════ PROTEÇÃO DO DOCUMENTO ═════   │
│ Senha: [****] ☐Mostrar ☐Padrão      │
│ ☐Restringir edição ☐Desab. cópia   │
│ ☐Criptografar conteúdo              │
│                                     │
│           [Carimbar] [Sair]         │
└─────────────────────────────────────┘
```

**Status: Implementação Completa ✅**
- Interface gráfica com calendário funcional
- Linha de comando com validação
- Persistência de configurações
- Validação de segurança
- Documentação atualizada
