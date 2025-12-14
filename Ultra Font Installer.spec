# -*- mode: python ; coding: utf-8 -*-
# Ultra Font Installer - PyInstaller Spec File
# Constructeur: JULAI | Version: 2.0

import os
import sys

block_cipher = None

# Chemin de base du projet
BASE_DIR = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(BASE_DIR, 'src', 'main.py')],
    pathex=[BASE_DIR, os.path.join(BASE_DIR, 'src')],
    binaries=[],
    datas=[
        (os.path.join(BASE_DIR, 'assets'), 'assets'),
        (os.path.join(BASE_DIR, 'locales'), 'locales'),
        (os.path.join(BASE_DIR, 'bin'), 'bin'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtSvg',
        'qfluentwidgets',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'PIL.ImageQt',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Ultra Font Installer',
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
    icon=os.path.join(BASE_DIR, 'assets', 'logo.png'),
    uac_admin=True,
    version=os.path.join(BASE_DIR, 'version_info.txt'),
)
