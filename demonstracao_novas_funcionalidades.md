> Documento histórico da versão 2. Para o comportamento atual, consulte [README.md](README.md).

# Demonstração das Novas Funcionalidades

Este documento demonstra as novas funcionalidades implementadas no CarimboPDF.

## 🔐 Funcionalidades de Proteção Implementadas

### 1. **Opção para Ver/Ocultar Senha**
- ✅ Campo de senha com opção "Mostrar" para alternar visibilidade
- ✅ Por padrão a senha aparece mascarada com asteriscos (*)
- ✅ Ao marcar "Mostrar", a senha fica visível para conferência

### 2. **Senha Padrão para Próximos Documentos**
- ✅ Checkbox "Salvar como padrão" no campo de senha
- ✅ Quando marcado, a senha é salva e reutilizada automaticamente
- ✅ Quando desmarcado, a senha não é persistida por segurança

### 3. **Persistência Automática de Configurações**
- ✅ Todas as configurações são salvas automaticamente ao fechar a aplicação
- ✅ Funciona tanto com o botão "Sair" quanto com o "X" da janela
- ✅ Configurações são restauradas na próxima abertura
- ✅ Arquivo salvo em: `~/.data_hora_pdf/config.json`

## 📊 Configurações Persistidas

As seguintes configurações são automaticamente salvas:

### Básicas:
- ✅ Cidade padrão
- ✅ Página a ser carimbada
- ✅ Opção "Salvar no mesmo arquivo"

### Formatação:
- ✅ Tamanho da fonte
- ✅ Família da fonte (helv/times/cour)
- ✅ Cor do texto
- ✅ Negrito e Itálico

### Logo:
- ✅ Caminho do arquivo de logo
- ✅ Largura do logo em cm
- ✅ Margem do logo em cm

### Proteção:
- ✅ Restrições de edição
- ✅ Desativar cópia
- ✅ Criptografia de conteúdo
- ✅ Opção de salvar senha (apenas se marcada)
- ✅ Senha de proteção (apenas se "salvar como padrão" estiver marcado)

## 🧪 Como Testar

1. **Abra a interface gráfica:**
   ```powershell
   python -m data_hora_pdf.cli --gui
   ```

2. **Configure algumas opções e feche a aplicação**

3. **Abra novamente e veja que as configurações foram mantidas**

4. **Teste a funcionalidade de senha:**
   - Digite uma senha
   - Marque "Mostrar" para ver a senha
   - Marque "Salvar como padrão"
   - Feche e abra novamente para ver a senha restaurada

## 📁 Localização dos Arquivos

- **Configurações:** `%USERPROFILE%\.data_hora_pdf\config.json`
- **Exemplo no Windows:** `C:\Users\SeuUsuario\.data_hora_pdf\config.json`

## 🔍 Exemplo de Arquivo de Configuração

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
  "restrict_editing": true,
  "no_copy": false,
  "encrypt_content": true,
  "save_password": true,
  "protection_password": "senha123"
}
```

## ✨ Melhorias na Interface

### Layout Melhorado:
- Seção "PROTEÇÃO DO DOCUMENTO" claramente destacada
- Campo de senha com controles inline (mostrar/salvar)
- Organização lógica das opções de proteção
- Separação visual entre diferentes tipos de configuração

### Experiência do Usuário:
- 🔄 **Persistência automática** - não precisa configurar tudo novamente
- 👁️ **Visibilidade da senha** - pode conferir se digitou corretamente
- 🔐 **Senha padrão opcional** - conveniência com segurança
- 💾 **Salvamento inteligente** - salva só quando realmente fechar

## 🛡️ Considerações de Segurança

- A senha só é salva se explicitamente autorizado pelo usuário
- O arquivo de configuração é local ao usuário
- A opção de mostrar senha é temporária (não persiste)
- Todas as funcionalidades de proteção do PDF foram mantidas
