# CarimboPDF development

Read README.md and EXECUTAVEIS.md for current installation and behavior.
Use Python 3.10+ with Tkinter for GUI development.

## Architecture
- cli.py: argparse and terminal errors; import Tkinter only for GUI mode.
- gui.py: ttk interface and ProcessPoolExecutor; never process PDFs on the Tk event loop.
- stamper.py: preserve default template coordinates and existing input encryption.
- config.py: validate preferences, save atomically, never persist passwords.
- dates.py: shared validation; reject invalid and future dates.

## Validation
Install with `python -m pip install -e ".[dev]"`.
Run `ruff check src tests`, `ruff format --check src tests`, and `pytest -q`.
GUI tests skip when Tcl/Tk or a display is unavailable; run them on Windows or with a display before release.
Run the documented CLI scenarios for basic stamping, in-place editing, logo, and AES protection.
Build on Windows with `python -m PyInstaller --noconfirm CarimboPDF.spec`.

## Invariants
- Failed image insertion, encryption, or writes must not replace existing output.
- Never fall back to saving without requested protection.
- Preserve city (337, 280) and date (391, 307) unless explicit coordinates are supplied.
- No password in config, logs, or error messages.
- Keep Tk calls in the parent process and use freeze_support for frozen applications.
- Keep compatibility flags and document behavior changes in README.md.
