#!/usr/bin/env python
"""
Script para executar o CarimboPDF em modo GUI sem console.
Use este arquivo para executar a aplicação sem mostrar o terminal.
"""

import sys
from multiprocessing import freeze_support
from pathlib import Path

# Adicionar o diretório src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Importar e executar
from data_hora_pdf.cli import main

if __name__ == "__main__":
    freeze_support()
    sys.exit(main())
