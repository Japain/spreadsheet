# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 6.x spec file for Quarterly (quarterly.exe)
# Build mode: --onedir (produces dist/quarterly/quarterly.exe)
# Note: UPX disabled — UPX can corrupt Qt binaries on Windows

import os

# Since quarterly.spec is in build/quarterly.spec, the project root is one level up
PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))

a = Analysis(
    [os.path.join(PROJECT_ROOT, 'src', 'main.py')],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[],
    hiddenimports=[
        'openpyxl',
        'openpyxl.cell._writer',
        'openpyxl.styles.builtins',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'pytestqt'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='quarterly',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,  # always empty in PyInstaller 6.x; included for template completeness
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='quarterly',
)
