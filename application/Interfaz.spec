# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules

base_path = os.path.abspath(os.getcwd())
entry_file = os.path.join(base_path, "main.py")
icon_file = os.path.join(base_path, "application", "icon.ico")

a = Analysis(
    [entry_file],
    pathex=[base_path],
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules("customtkinter"),
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
    name="MEySLahuella",
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
    icon=icon_file if os.path.exists(icon_file) else None,
)
