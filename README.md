# data-hora-pdf

Utilitário simples em Python para carimbar em um PDF a cidade e a data por extenso, em uma posição determinada.

## Requisitos
- Python 3.10+
- pip

## Instalação de dependências

```powershell
# Opcional: criar venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

Se rodar o CLI diretamente no terminal, exporte PYTHONPATH para apontar para a pasta `src` (no Windows PowerShell, apenas na sessão atual):

```powershell
$env:PYTHONPATH = "$PWD/src"
```

## Uso (GUI automático)

Executar sem parâmetros abre um seletor de arquivo. Por padrão, o modo GUI salva no mesmo arquivo (in-place) após confirmação.

```powershell
python -m data_hora_pdf.cli
```

Você pode informar a cidade via argumento ou variável de ambiente:

```powershell
python -m data_hora_pdf.cli --gui --cidade "São Paulo"
# ou
$env:CIDADE_PADRAO = "São Paulo"; python -m data_hora_pdf.cli --gui
```

Se quiser salvar em outro arquivo, informe `--output <arquivo.pdf>`.

Se `--cidade` for omitido, usa `CIDADE_PADRAO` e, se não existir, o fallback "Lages/SC.".

## Uso (CLI tradicional)

```powershell
python -m data_hora_pdf.cli --input <entrada.pdf> --output <saida.pdf> --cidade "São Paulo" --page 0
```
Ou para sobrescrever o arquivo de entrada:
```powershell
python -m data_hora_pdf.cli --input <entrada.pdf> --in-place --cidade "São Paulo"
```

Parâmetros:
- --input: caminho do PDF de entrada
- --output: caminho do PDF de saída
- --cidade: cidade a ser inserida
- --page: índice da página (0 = primeira)
- --x, --y: posição em pontos (opcionais); se omitidos, usa posições padrão em cm: cidade em 11,9 x 9,88 cm e data em 13,8 x 10,8 cm
- --font-size: tamanho da fonte (padrão 12)
- --color: cor em HEX (padrão #000000)
- --font: família/nome da fonte (helv|times|cour ou nome base do MuPDF)
- --bold: usar negrito
- --italic: usar itálico
- --logo-path: caminho do arquivo de logo (padrão: tenta Logo.jpg/Logo.png na pasta atual ou ao lado do PDF)
- --logo-width-cm: largura alvo do logo em centímetros (padrão 10.0 cm)
- --logo-margin-cm: margem a partir do canto inferior esquerdo em centímetros (padrão 10.0 cm)

Observações:
- O alinhamento do texto é fixo para a direita (right) no código; o parâmetro --align foi removido.

## Teste rápido
1) Gere um PDF em branco:
```powershell
python .\scripts\make_dummy_pdf.py
```
2) Carimbe via CLI:
```powershell
python -m data_hora_pdf.cli --input dummy.pdf --output dummy_carimbado.pdf --cidade "São Paulo"
```

Resultado: `São Paulo, 13 de agosto de 2025` no canto inferior direito.

## Notas
- Coordenadas em pontos (1 polegada = 72pt). A origem (0,0) é o canto superior esquerdo.
- Compatível com Windows, macOS e Linux.
- O logo, quando presente, é convertido automaticamente para PNG RGB sem perfil ICC antes da inserção, evitando avisos como "ICC profile (N=4) is not RGB" do MuPDF. Para melhores resultados, use imagens RGB.
