# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules

# Rutas base
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
entry_file = os.path.join(base_path, "src", "ui", "Interfaz.py")
theme_file = os.path.join(base_path, "src", "ui", "theme.json")
icon_file = os.path.join(base_path, "src", "ui", "icon.ico")  # opcional

a = Analysis(
    [entry_file],
    pathex=[base_path],
    binaries=[],
    datas=[
        (theme_file, "src/ui"),  # <- asegura que theme.json esté empaquetado
    ],
    hiddenimports=collect_submodules('customtkinter'),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Interfaz',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # True para ver errores en consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file if os.path.exists(icon_file) else None
)
