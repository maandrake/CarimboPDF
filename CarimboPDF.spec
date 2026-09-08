# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

ROOT = Path(SPECPATH)
a = Analysis(
    [str(ROOT / 'CarimboPDF_GUI.pyw')],
    pathex=[str(ROOT / 'src')],
    binaries=[],
    datas=[
        (str(ROOT / 'Logo.jpg'), '.'),
        (str(ROOT / 'src/data_hora_pdf/assets'), 'data_hora_pdf/assets'),
    ],
    hiddenimports=['babel.numbers'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='CarimboPDF', debug=False, bootloader_ignore_signals=False,
    strip=False, upx=False, console=False,
    icon=str(ROOT / 'src/data_hora_pdf/assets/carimbopdf.ico'),
)
