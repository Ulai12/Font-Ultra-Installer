# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file pour Ultra Font Installer

import os
import sys

block_cipher = None

# Chemin de base du projet
base_path = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['src/main.py'],
    pathex=[base_path],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('locales', 'locales'),
        ('bin', 'bin'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
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
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Ultra Font Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Pas de console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.png',
    uac_admin=True,  # Demander les droits admin
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Ultra Font Installer',
)
