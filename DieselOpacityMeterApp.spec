# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hidden_imports = (
    collect_submodules('mysql.connector')
    + collect_submodules('pymodbus')
    + ['bcrypt']
)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('main.kv', '.'),
        ('screen_home.kv', '.'),
        ('screen_login.kv', '.'),
        ('screen_main.kv', '.'),
        ('screen_smoke_test.kv', '.'),
        ('screen_Calibration.kv', '.'),
        ('config.ini', '.'),
        ('assets/images', 'assets/images'),
        ('assets/fonts', 'assets/fonts'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[kivymd_hooks_path],
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
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='TRB-VIIMS-DieselOpacityMeterApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon='./assets/images/logo-emission-app.ico',
)
