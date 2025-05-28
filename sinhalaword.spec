# -*- mode: python ; coding: utf-8 -*-
"""
Sinhala Word Processor - PyInstaller spec file
Copyright (c) 2025 L.J.Amila Prasad Perera
CC - Free to use by crediting the owner (L.J.Amila Prasad Perera)
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get the base directory
try:
    base_dir = os.path.abspath(os.path.dirname(__file__))
except NameError:
    # When running with PyInstaller directly, __file__ might not be defined
    base_dir = os.path.abspath(os.getcwd())

# Define paths
splash_image = os.path.join(base_dir, 'resources', 'splash', 'sinhalaword.png')
icon_file = os.path.join(base_dir, 'resources', 'splash', 'sinhalaword_icon.ico')

# Collect all necessary data files
datas = []
datas.extend(collect_data_files('app'))

# Explicitly add resources directory with its structure preserved
datas.append(('resources/', 'resources/'))
datas.append(('app/', 'app/'))

# Add dictionaries and other data files
if os.path.exists(os.path.join(base_dir, 'dictionaries')):
    datas.append(('dictionaries/', 'dictionaries/'))

# Add data directory if it exists
if os.path.exists(os.path.join(base_dir, 'data')):
    datas.append(('data/', 'data/'))
    
# # Explicitly add sinhalawordmap.json from data directory
# sinhalawordmap_path = os.path.join(base_dir, 'data', 'sinhalawordmap.json')
# if os.path.exists(sinhalawordmap_path):
#     # Add to root directory for backward compatibility
#     datas.append((sinhalawordmap_path, '.'))

# Add any JSON files in the root directory
for file in os.listdir(base_dir):
    if file.endswith('.json'):
        datas.append((file, '.'))

# Collect all necessary modules
hiddenimports = []
hiddenimports.extend(collect_submodules('PyQt6'))
hiddenimports.extend(collect_submodules('PySide6'))
hiddenimports.extend(['docx', 'reportlab', 'pypdf', 'json', 'os', 'sys', 'time', 're'])
hiddenimports.extend(['PySide6.QtPrintSupport', 'pyi_splash'])

a = Analysis(
    ['app/main.py'],
    pathex=[base_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

splash = Splash(
    splash_image,
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    text_color='white',
    minify_script=True,
    opacity=0.8,  # Add transparency
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash,
    splash.binaries,
    [],
    name='SinhalaWord',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

# Create a directory for the portable version
portable_dir = os.path.join('dist', 'SinhalaWord_Portable')
if not os.path.exists(portable_dir):
    os.makedirs(portable_dir)

# Create a simple batch file to run the application
with open(os.path.join(portable_dir, 'SinhalaWord.bat'), 'w') as f:
    f.write('@echo off\n')
    f.write('start "" "%~dp0\\SinhalaWord.exe"\n')

# Copy the executable to the portable directory
import shutil
shutil.copy2(os.path.join('dist', 'SinhalaWord.exe'), portable_dir)