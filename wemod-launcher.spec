# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Add source directory to path
src_path = str(Path(__file__).parent / "src")
sys.path.insert(0, src_path)

block_cipher = None

a = Analysis(
    ['src/wemod_launcher/wemod.py'],
    pathex=[src_path],
    binaries=[],
    datas=[],
    hiddenimports=[
        # Qt6 modules - required for PyQt6
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        # CLI framework
        'click',
        'click.core',
        'click.decorators',
        # Application modules
        'wemod_launcher.cli',
        'wemod_launcher.gfx.welcome_screen',
        'wemod_launcher.gfx.download_popup',
        'wemod_launcher.utils.logger',
        'wemod_launcher.utils.configuration',
        'wemod_launcher.utils.consts',
        'wemod_launcher.pfx.wine_utils',
        # Standard library modules that might not be auto-detected
        'json',
        'threading',
        'pathlib',
        'signal',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'FreeSimpleGUI',  # Exclude old GUI library
        'tkinter',        # Often included by default but not needed
        'matplotlib',     # Heavy dependency, exclude if not needed
        'numpy',          # Heavy dependency, exclude if not needed
    ],
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
    name='wemod-launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI app on Windows/macOS
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if you have one
)

# For Linux AppImage support
app = BUNDLE(
    exe,
    name='wemod-launcher.app',
    icon=None,
    bundle_identifier='org.uk.shymega.deckCheatz.wemod-launcher',
)
