# CarimboPDF - Executáveis e Atalhos

## 🚀 Como Executar

### Opção 1: Duplo clique no arquivo CMD
```
Iniciar - Carimbar PDF (GUI).cmd
```

### Opção 2: Executar arquivo Python diretamente
```
CarimboPDF_GUI.pyw
```

### Opção 3: Via linha de comando (para desenvolvimento)
```powershell
python -m data_hora_pdf.cli
```

## 📋 Características dos Executáveis

### `CarimboPDF_GUI.pyw`
- ✅ **Sem console**: Executa apenas a interface gráfica
- ✅ **Centralizado**: Janela aparece no centro da tela
- ✅ **Foco automático**: Janela fica em primeiro plano
- ✅ **Tamanho otimizado**: 580x500 pixels mínimo

### `Iniciar - Carimbar PDF (GUI).cmd`
- ✅ **Detecção automática**: Usa `pythonw.exe` se disponível
- ✅ **Fallback inteligente**: Se `pythonw.exe` não existir, usa `python.exe`
- ✅ **Ambiente virtual**: Prioriza o Python do venv se existir
- ✅ **PYTHONPATH configurado**: Não precisa de configuração manual

## 🎯 Interface Atualizada

### Novas Características:
- **Janela centralizada automaticamente**
- **Console ocultado no Windows**
- **Foco automático na abertura**
- **Tamanho mínimo otimizado**
- **Botão fechar (X) salva configurações**

### Layout:
```
┌─────────────────────────────────┐
│        Carimbar PDF             │
├─────────────────────────────────┤
│ PDF entrada: [____] [Selecionar]│
│ PDF saída:   [____] [Salvar]    │
│ ☑ Salvar no mesmo arquivo       │
│                                 │
│ Cidade: [São Paulo_______]      │
│ Página: [0] Fonte: [12] [helv]  │
│ Cor: [#000000] ☐Negrito ☐Itál. │
│                                 │
│ Logo: [____] [Selecionar]       │
│ Largura: [2.0] Margem: [0.5]    │
│                                 │
│ ═══ PROTEÇÃO DO DOCUMENTO ═══   │
│ Senha: [****] ☐Mostrar ☐Padrão  │
│ ☐Restringir edição ☐Desab.cópia │
│ ☐Criptografar conteúdo          │
│                                 │
│         [Carimbar] [Sair]       │
└─────────────────────────────────┘
```

## 🔧 Configurações Técnicas

### Ocultação do Console (Windows):
```python
import ctypes
hwnd = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.ShowWindow(hwnd, 0)
```

### Centralização da Janela:
```python
window_width = root.winfo_reqwidth()
window_height = root.winfo_reqheight()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
```

### Comportamento por Padrão:
- **Sempre abre GUI** se nenhum parâmetro específico for fornecido
- **Salva configurações** automaticamente ao fechar
- **Carrega configurações** automaticamente ao abrir
- **Foco na janela** para melhor experiência do usuário
