# -*- mode: python; coding: utf-8 -*-
import os

# Root da aplicação (PyInstaller executa sem __file__)
ROOT = os.getcwd()

# Inclui a pasta src para resolver imports do pacote data_hora_pdf
PATHEX = [ROOT, os.path.join(ROOT, "src")]

# Logo padrão embutido ao lado do executável
DATAS = [(os.path.join(ROOT, "Logo.jpg"), ".")]

block_cipher = None

a = Analysis(
    ['CarimboPDF_GUI.pyw'],
    pathex=PATHEX,
    binaries=[],
    datas=DATAS,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CarimboPDF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
