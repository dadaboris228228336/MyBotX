# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for MyBotX 1.0.0

import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent

a = Analysis(
    [str(ROOT / 'CORE' / 'main.py')],
    pathex=[str(ROOT / 'CORE')],
    binaries=[],
    datas=[
        (str(ROOT / 'CORE' / 'processes'), 'processes'),
        (str(ROOT / 'CORE' / 'UI'), 'UI'),
        (str(ROOT / 'CORE' / 'requirements.txt'), '.'),
        (str(ROOT / 'CORE' / 'mybotx.ico'), '.'),
        (str(ROOT / 'CONFIG'), 'CONFIG'),
        (str(ROOT / 'BOT_APPLICATIONS' / 'platform-tools'), 'BOT_APPLICATIONS/platform-tools'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'PIL.Image', 'PIL.ImageTk', 'PIL.ImageDraw', 'PIL.ImageFont',
        'cv2', 'numpy', 'psutil',
        'win32gui', 'win32con', 'win32api',
        'pyautogui',
        'processes.SCENARIO',
        'processes.SCENARIO.scenario_01_runner',
        'processes.SCENARIO.scenario_02_steps',
        'processes.SCENARIO.scenario_03_storage',
        'processes.SCENARIO.scenario_04_adb_actions',
        'processes.LOGGER',
        'processes.SETUP',
        'UI.scenario_editor',
        'UI.tabs.tab_main',
        'UI.tabs.tab_check',
        'UI.tabs.tab_bot',
        'UI.tabs.tab_about',
    ],
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
    name='MyBotX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # без консоли
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / 'CORE' / 'mybotx.ico'),
    version_file=str(ROOT / 'BUILD' / 'version_info.txt'),
)
