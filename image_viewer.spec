# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files

# 收集PyQt6的数据文件
datas = collect_data_files('PyQt6')

# 添加应用图标（如果有的话）
# datas += [('icon.ico', '.')]  # Windows
# datas += [('icon.icns', '.')]  # macOS

block_cipher = None

a = Analysis(
    ['6_open_img.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'requests',
        'lxml',
        'lxml.html',
        'webbrowser',
        'json',
        'glob',
        'shutil',
        'time',
        'collections',
        'urllib.parse',
        'os.path',
        'math'
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Image Viewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if sys.platform == 'win32' else 'icon.icns' if sys.platform == 'darwin' else None,
)
