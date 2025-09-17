# CarimboPDF

CarimboPDF is a professional Python utility for stamping PDFs with city and date in Portuguese, featuring advanced password protection and a modern GUI interface.

**ALWAYS** reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Setup
- Install Python 3.10+ (Python 3.12+ recommended)
- Install system dependencies: `sudo apt-get update && sudo apt-get install -y python3-tk` (Linux)
- Create virtual environment: `python -m venv .venv` -- takes 3-5 seconds
- Activate environment:
  - Windows: `.\.venv\Scripts\Activate.ps1`
  - Linux/macOS: `source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt` -- takes 15-60 seconds. NEVER CANCEL. May timeout on slow networks, retry if needed.
- Configure PYTHONPATH: `export PYTHONPATH="$PWD/src"` (Linux/macOS) or `$env:PYTHONPATH = "$PWD/src"` (Windows)

### Build and Test
- **No build step required** - Python application runs directly
- Basic syntax validation: `python -m py_compile src/data_hora_pdf/cli.py src/data_hora_pdf/stamper.py src/data_hora_pdf/__init__.py` -- takes 0.1 seconds
- Generate test PDF: `python scripts/make_dummy_pdf.py` -- takes 0.1 seconds
- Test CLI functionality: `python -m data_hora_pdf.cli --input dummy.pdf --output test_output.pdf --cidade "São Paulo"` -- takes 0.2 seconds
- **No existing test framework** - manual validation only

### Run the Application
- **GUI Mode (Recommended):**
  - Windows: Double-click `Iniciar - Carimbar PDF (GUI).cmd`
  - Cross-platform: `python CarimboPDF_GUI.pyw`
  - CLI GUI mode: `python -m data_hora_pdf.cli --gui`
- **CLI Mode:**
  - Basic stamping: `python -m data_hora_pdf.cli --input file.pdf --output stamped.pdf --cidade "São Paulo"`
  - In-place editing: `python -m data_hora_pdf.cli --input file.pdf --in-place --cidade "Rio de Janeiro"`
  - With protection: `python -m data_hora_pdf.cli --input file.pdf --output secure.pdf --cidade "Brasília" --protection-password "senha123" --restrict-editing`

## Validation

### Required Test Scenarios
**ALWAYS** run these validation scenarios after making any changes:

1. **Basic PDF Stamping:**
   ```bash
   python scripts/make_dummy_pdf.py
   python -m data_hora_pdf.cli --input dummy.pdf --output test_basic.pdf --cidade "São Paulo"
   # Verify: PDF created successfully, no errors in output
   ```

2. **In-Place Editing:**
   ```bash
   python -m data_hora_pdf.cli --input dummy.pdf --in-place --cidade "Rio de Janeiro"
   # Verify: Original file modified, backup not created
   ```

3. **Advanced Features:**
   ```bash
   python -m data_hora_pdf.cli --input dummy.pdf --output test_advanced.pdf --cidade "Brasília" --font-size 16 --bold --italic --color "#FF0000" --protection-password "test123" --restrict-editing
   # Verify: PDF with red bold italic text and password protection
   ```

4. **Logo Functionality:**
   ```bash
   python -m data_hora_pdf.cli --input dummy.pdf --output test_logo.pdf --cidade "São Paulo" --logo-path Logo.jpg --logo-width-cm 2.5
   # Verify: Logo appears in bottom-left corner
   ```

5. **GUI Mode (if display available):**
   ```bash
   timeout 10 python -m data_hora_pdf.cli --gui
   # Should open GUI window or fail with display error (expected in headless)
   ```

6. **Complete Workflow Test:**
   ```bash
   python scripts/make_dummy_pdf.py
   python -m data_hora_pdf.cli --input dummy.pdf --output complete_test.pdf --cidade "Porto Alegre" --font-size 18 --bold --color "#0000FF" --logo-path Logo.jpg
   # Verify: Complete workflow completes in under 1 second with logo and formatting
   ```

### Expected Results
- All CLI commands complete in under 1 second for small PDFs
- Output messages show: `[data-hora-pdf] Fonte efetiva: [font] | bold=[bool] | italic=[bool]`
- Generated PDFs should contain "CIDADE" on first line and "DD DE MÊS DE AAAA." on second line
- Text positioned in bottom-right corner by default

## Common Tasks

### Project Structure
```
CarimboPDF/
├── src/data_hora_pdf/          # Main Python package
│   ├── __init__.py
│   ├── cli.py                  # Command-line interface and GUI
│   └── stamper.py              # Core PDF processing logic
├── scripts/
│   ├── make_dummy_pdf.py       # Generate test PDF
│   └── test_mupdf_permissions.py
├── CarimboPDF_GUI.pyw          # GUI launcher (no console)
├── Iniciar - Carimbar PDF (GUI).cmd  # Windows GUI launcher
├── Logo.jpg                    # Default logo file
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation
└── EXECUTAVEIS.md             # Executable documentation
```

### Key Dependencies
```
pymupdf==1.24.9      # PDF manipulation
Pillow==10.4.0       # Image processing  
tkcalendar==1.6.1    # Calendar widget for GUI
```

### CLI Parameters Reference
- `--input`: Input PDF path (required)
- `--output`: Output PDF path (or use `--in-place`)
- `--cidade`: City name for stamp (required)
- `--page`: Page index (0=first, default: 0)
- `--font-size`: Font size in points (default: 12)
- `--font`: Font family - helv|times|cour (default: helv)  
- `--color`: Text color in HEX (default: #000000)
- `--bold`, `--italic`: Text formatting
- `--logo-path`: Logo image file path
- `--logo-width-cm`: Logo width in cm (default: 2.0)
- `--logo-margin-cm`: Logo margin in cm (default: 0.5)
- `--protection-password`: Password for edit protection
- `--restrict-editing`: Disable document editing
- `--no-copy`: Disable text/image copying
- `--encrypt-content`: Enable AES-256 encryption
- `--date`: Custom date in DD/MM/YYYY format
- `--gui`: Launch GUI mode

### Configuration Persistence
GUI mode automatically saves settings to:
- Windows: `C:\Users\[user]\.data_hora_pdf\config.json`
- Linux: `/home/[user]/.data_hora_pdf/config.json`
- macOS: `/Users/[user]/.data_hora_pdf/config.json`

### Troubleshooting Commands
```bash
# Check Python version (needs 3.10+)
python --version

# Verify dependencies
pip list | grep -E "fitz|pillow|tkcalendar"

# Test basic functionality
python -m data_hora_pdf.cli --help

# Clear configuration if corrupted
rm ~/.data_hora_pdf/config.json  # Linux/macOS
```

### Working with the Code
- **Main entry point:** `src/data_hora_pdf/cli.py` (CLI and GUI logic)
- **PDF processing:** `src/data_hora_pdf/stamper.py` (core stamping functionality)
- **No linting configured** - use `python -m py_compile` for syntax validation
- **No automated tests** - rely on manual validation scenarios above
- **Font fallback:** Always uses 'helv' as default/fallback font
- **Error handling:** Application continues with warnings for non-critical failures

### Development Notes
- Application supports Windows, macOS, and Linux
- GUI requires system tkinter installation (`python3-tk` package on Linux)
- Logo files auto-detected as Logo.jpg/logo.jpg/Logo.png/logo.png in current directory
- Coordinates system: (0,0) at top-left, units in points (72pt = 1 inch)
- Default stamp position: bottom-right corner with automatic margins
- Configuration uses JSON format with UTF-8 encoding

## CRITICAL: Execution Timing
- **NEVER CANCEL** any operation - all commands complete quickly
- Virtual environment creation: 3-5 seconds
- Dependency installation: 15-60 seconds (may timeout on slow networks - retry)
- PDF generation: 0.1-0.2 seconds per file
- Syntax validation: 0.1 seconds
- **No long-running builds or tests** in this project

Always validate your changes work by running the complete validation scenarios before considering your work complete.