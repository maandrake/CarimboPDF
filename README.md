# CarimboPDF

Utilitário profissional em Python para carimbar PDFs com cidade e data por extenso, incluindo **proteção avançada com senha** e **interface gráfica moderna**.

## ⭐ Principais Funcionalidades

- 📅 **Carimbo automático** com cidade e data por extenso em português
- 🖼️ **Inserção de logo** com ajuste automático de tamanho
- 🔐 **Proteção avançada** com senha para edição, restrições de cópia e criptografia AES-256
- 🖥️ **Interface gráfica moderna** centralizada e sem console
- 💾 **Persistência automática** de todas as configurações
- 👁️ **Controle de visibilidade** da senha com opção de salvar como padrão
- 🎨 **Customização completa** de fonte, cor, posição e estilo

## 🚀 Execução Rápida

### Forma mais simples (Recomendada):
**Duplo clique** no arquivo:
```
Iniciar - Carimbar PDF (GUI).cmd
```

### Alternativas:
```powershell
# Executar arquivo Python diretamente (sem console)
CarimboPDF_GUI.pyw

# Via linha de comando (desenvolvimento)
python -m data_hora_pdf.cli
```

## 📋 Requisitos
- Python 3.10+
- pip
- Windows, macOS ou Linux

## 🔧 Instalação

### 1. Clone ou baixe o projeto
### 2. Instale as dependências:

```powershell
# Opcional: criar ambiente virtual (recomendado)
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# ou
source .venv/bin/activate     # Linux/macOS

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configuração opcional:
Para desenvolvimento via terminal, configure o PYTHONPATH:
```powershell
$env:PYTHONPATH = "$PWD/src"  # Windows PowerShell
# ou
export PYTHONPATH="$PWD/src"  # Linux/macOS
```

## 🖥️ Interface Gráfica

A interface gráfica oferece **experiência profissional** com:

### ✨ Características da Interface:
- 🎯 **Centralizada automaticamente** na tela
- 🚫 **Sem console** - apenas a interface limpa
- 💾 **Salvamento automático** de configurações ao fechar
- 🔄 **Carregamento automático** das últimas configurações usadas
- 👁️ **Controle de senha** com opção mostrar/ocultar
- ⚙️ **Todas as opções** disponíveis em interface amigável

### 📁 Configurações Básicas:
- **PDF de entrada:** Selecionar arquivo com botão de navegação
- **PDF de saída:** Automático ou escolher local específico
- **☑ Salvar no mesmo arquivo:** Conveniência para substituir original
- **Cidade:** Personalizar cidade do carimbo (padrão: São Paulo)

### 🎨 Formatação Avançada:
- **Página:** Escolher qual página carimbar (0 = primeira)
- **Fonte:** helv, times, cour ou nome customizado
- **Tamanho:** Ajustar tamanho da fonte em pontos
- **Cor:** Seletor HEX (#000000 = preto)
- **Estilo:** Negrito, itálico ou combinações

### 🖼️ Logo Personalizado:
- **Arquivo:** JPG, PNG ou outros formatos suportados
- **Largura:** Tamanho em centímetros (padrão: 2.0 cm)
- **Margem:** Distância das bordas (padrão: 0.5 cm)
- **Posição:** Canto inferior esquerdo automaticamente

### 🔐 Proteção Avançada:
- **Senha para edição:** Documento abre sem senha, mas protege edição
- **☑ Mostrar senha:** Ver senha enquanto digita para conferência
- **☑ Salvar como padrão:** Reutilizar senha em próximos documentos
- **☑ Restringir edição:** Impede modificações e anotações
- **☑ Desativar cópia:** Bloqueia cópia de texto e imagens
- **☑ Criptografar conteúdo:** Proteção AES-256 para máxima segurança

### 🎛️ Configuração por Variável de Ambiente:
```powershell
$env:CIDADE_PADRAO = "São Paulo"
```

## 💻 Linha de Comando (CLI)

Para usuários avançados e automação:

### Uso Básico:
```powershell
python -m data_hora_pdf.cli --input entrada.pdf --output saida.pdf --cidade "São Paulo"
```

### Sobrescrever arquivo original:
```powershell
python -m data_hora_pdf.cli --input documento.pdf --in-place --cidade "São Paulo"
```

### 📝 Parâmetros Disponíveis:

#### Básicos:
- `--input`: Caminho do PDF de entrada
- `--output`: Caminho do PDF de saída
- `--cidade`: Nome da cidade para o carimbo
- `--in-place`: Sobrescrever o arquivo original
- `--page`: Índice da página (0 = primeira, 1 = segunda, etc.)

#### Formatação:
- `--font-size`: Tamanho da fonte em pontos (padrão: 12)
- `--font`: Família da fonte - helv|times|cour (padrão: helv)
- `--color`: Cor em formato HEX (padrão: #000000)
- `--bold`: Aplicar negrito
- `--italic`: Aplicar itálico
- `--x`, `--y`: Posição customizada em pontos (opcional)

#### Logo:
- `--logo-path`: Caminho do arquivo de logo (JPG/PNG)
- `--logo-width-cm`: Largura do logo em centímetros (padrão: 2.0)
- `--logo-margin-cm`: Margem do logo em centímetros (padrão: 0.5)

#### 🔐 Proteção:
- `--protection-password`: Senha para proteção de edição
- `--restrict-editing`: Restringir edição do documento
- `--no-copy`: Desativar cópia de texto e imagens
- `--encrypt-content`: Criptografar com AES-256

### 🛡️ Exemplos de Proteção:

#### PDF com senha básica:
```powershell
python -m data_hora_pdf.cli --input doc.pdf --output protegido.pdf --cidade "São Paulo" --protection-password "minhaSenha123"
```

#### PDF com restrições completas:
```powershell
python -m data_hora_pdf.cli --input doc.pdf --output ultra_seguro.pdf --cidade "São Paulo" --protection-password "senhaForte" --restrict-editing --no-copy --encrypt-content
```

#### PDF com logo personalizado:
```powershell
python -m data_hora_pdf.cli --input doc.pdf --output com_logo.pdf --cidade "São Paulo" --logo-path "meu_logo.png" --logo-width-cm 3.0
```

## 💾 Persistência de Configurações

A interface gráfica possui **sistema inteligente de configurações**:

### 🔄 Salvamento Automático:
**Todas as configurações são salvas automaticamente quando:**
- Clicar no botão "Sair"
- Fechar a janela pelo "X"
- Encerrar a aplicação de qualquer forma

### 📂 Local de Armazenamento:
```
Windows: C:\Users\SeuUsuario\.data_hora_pdf\config.json
Linux:   /home/usuario/.data_hora_pdf/config.json
macOS:   /Users/usuario/.data_hora_pdf/config.json
```

### ⚙️ Configurações Salvas:
- ✅ **Básicas:** Cidade, página, opção in-place
- ✅ **Formatação:** Fonte, tamanho, cor, negrito, itálico
- ✅ **Logo:** Caminho, largura, margem
- ✅ **Proteção:** Restrições (exceto senha por segurança)
- ✅ **Interface:** Preferências de uso

### 🔐 Controle de Senha:
- **👁️ Mostrar/Ocultar:** Checkbox temporário para ver senha
- **💾 Salvar como padrão:** Apenas se explicitamente autorizado
- **🔒 Segurança:** Senha não salva por padrão para proteção

### 📄 Exemplo de Arquivo de Configuração:
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
  "logo_path": "C:/caminho/para/logo.png",
  "logo_width_cm": 2.0,
  "logo_margin_cm": 0.5,
  "restrict_editing": true,
  "no_copy": false,
  "encrypt_content": false,
  "save_password": false
}
```

## 🧪 Teste Rápido
### 1. Gerar PDF de exemplo:
```powershell
python .\scripts\make_dummy_pdf.py
```

### 2. Testar via interface gráfica:
```
Duplo clique em: Iniciar - Carimbar PDF (GUI).cmd
```

### 3. Testar via linha de comando:
```powershell
python -m data_hora_pdf.cli --input dummy.pdf --output dummy_carimbado.pdf --cidade "São Paulo"
```

### 4. Resultado esperado:
```
SÃO PAULO
3 DE SETEMBRO DE 2025.
```
*Posicionado no canto inferior direito do PDF*

## 🔍 Funcionalidades Técnicas

### 📐 Sistema de Coordenadas:
- **Origem (0,0):** Canto superior esquerdo
- **Unidade:** Pontos (1 polegada = 72 pontos)
- **Posicionamento padrão:** Automático no canto inferior direito
- **Customização:** Coordenadas X,Y opcionais via parâmetros

### 🖼️ Processamento de Logo:
- **Formatos suportados:** JPG, PNG, e outros via PIL
- **Conversão automática:** RGB sem perfil ICC
- **Posicionamento:** Canto inferior esquerdo automaticamente
- **Redimensionamento:** Proporcional mantendo aspecto

### 🔐 Segurança Avançada:

#### Níveis de Proteção:
1. **Básica:** Apenas senha para edição
2. **Intermediária:** + Restrições de edição e cópia
3. **Avançada:** + Criptografia AES-256

#### Tecnologias Utilizadas:
- **PyMuPDF (fitz):** Manipulação de PDF e aplicação de proteções
- **Pillow (PIL):** Processamento otimizado de imagens
- **Tkinter:** Interface gráfica nativa multiplataforma

## 🌐 Compatibilidade

### Sistemas Operacionais:
- ✅ **Windows 10/11** - Totalmente testado
- ✅ **macOS** - Compatível via Python
- ✅ **Linux** - Compatível via Python

### Versões Python:
- ✅ **Python 3.10+** - Recomendado
- ✅ **Python 3.9** - Compatível
- ⚠️ **Python 3.8** - Limitações em alguns recursos

## 🆘 Solução de Problemas
### ❌ Interface não abre:
```powershell
# Verificar se Python está instalado
python --version

# Verificar dependências
pip list | findstr -i "fitz\|pillow\|tkinter"

# Executar com diagnóstico
python -m data_hora_pdf.cli --help
```

### 🐛 Erro de fonte:
Se aparecer erro de fonte, o sistema usa automaticamente a fonte padrão `helv` como fallback.

### 🔒 Problemas de proteção:
Se a proteção falhar, o PDF é salvo sem proteção e uma mensagem de aviso é exibida.

### 📁 Configurações corrompidas:
```powershell
# Deletar configurações (Windows)
Remove-Item "$env:USERPROFILE\.data_hora_pdf\config.json"
```

## 🧹 Manutenção do Repositório

### Limpeza de Branches de PRs Fechados
Para manter o repositório organizado, use o script de limpeza incluído:

```cmd
# Windows (fácil):
scripts\Limpeza_Branches_PRs.cmd

# Qualquer sistema:
python scripts/cleanup_closed_pr_branches.py
```

**Importante:** GitHub não permite excluir Pull Requests (isso é intencional para auditoria). O script apenas limpa os branches associados. Veja [`GERENCIAMENTO_PRS.md`](GERENCIAMENTO_PRS.md) para detalhes completos.

## 🤝 Contribuição

Este projeto é mantido para uso interno. Para sugestões ou problemas:
1. Documente o erro detalhadamente
2. Inclua versão do Python e sistema operacional
3. Forneça arquivo de exemplo se possível

## 📄 Licença

Projeto de uso interno - Marcos Despachante

---

## 📊 Resumo de Funcionalidades

| Funcionalidade | GUI | CLI | Descrição |
|----------------|-----|-----|-----------|
| 📅 Carimbo data/cidade | ✅ | ✅ | Texto automático em português |
| 🖼️ Logo personalizado | ✅ | ✅ | JPG/PNG redimensionado |
| 🎨 Formatação completa | ✅ | ✅ | Fonte, cor, tamanho, estilo |
| 🔐 Proteção com senha | ✅ | ✅ | Edição, cópia, criptografia |
| 💾 Configurações salvas | ✅ | ❌ | Persistência automática |
| 👁️ Mostrar/ocultar senha | ✅ | ❌ | Controle de visibilidade |
| 🎯 Interface centralizada | ✅ | ❌ | Sem console, experiência limpa |
| 🚀 Execução rápida | ✅ | ✅ | Duplo clique ou linha comando |
| 🧹 Limpeza de branches | ❌ | ✅ | Manutenção do repositório |

**Versão:** 2.0 - Atualizada em setembro de 2025
