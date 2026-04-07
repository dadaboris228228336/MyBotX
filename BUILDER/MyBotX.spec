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
        (str(ROOT / 'my_bot'), 'my_bot'),
    ],
    hiddenimports=[
        # PIL / Pillow
        'PIL._tkinter_finder',
        'PIL.Image', 'PIL.ImageTk', 'PIL.ImageDraw', 'PIL.ImageFont',
        # CV / numpy
        'cv2', 'numpy',
        # System
        'psutil',
        'win32gui', 'win32con', 'win32api', 'win32process', 'win32com',
        'pyautogui',
        # Session logger
        'session_logger',
        'processes.LOGGER',
        'processes.LOGGER.logger_01_session',
        # Setup / deps
        'processes.SETUP',
        'processes.SETUP.setup_01_check_requirements',
        'processes.DEPENDENCIES',
        'processes.DEPENDENCIES.dep_01_init',
        'processes.DEPENDENCIES.dep_02_parse',
        'processes.DEPENDENCIES.dep_03_check',
        'processes.DEPENDENCIES.dep_04_install',
        # ADB
        'processes.ADB',
        'processes.ADB.adb_01_init',
        'processes.ADB.adb_02_check_port',
        'processes.ADB.adb_03_find_port',
        'processes.ADB.adb_04_connect',
        # BlueStacks
        'processes.BLUESTACKS',
        'processes.BLUESTACKS.bs_01_init',
        'processes.BLUESTACKS.bs_02_search',
        'processes.BLUESTACKS.bs_03_status',
        'processes.BLUESTACKS.bs_04_control',
        'processes.BLUESTACKS.bs_05_window',
        # Game
        'processes.GAME',
        'processes.GAME.game_01_init',
        'processes.GAME.game_02_check_app',
        'processes.GAME.game_03_play_market',
        'processes.GAME.game_04_launch_direct',
        'processes.GAME.game_05_launch_intent',
        'processes.GAME.game_06_launch_monkey',
        'processes.GAME.game_07_auto_launch',
        # BOT
        'processes.BOT',
        'processes.BOT.bot_01_screenshot',
        'processes.BOT.bot_02_find_pattern',
        'processes.BOT.bot_03_tap',
        'processes.BOT.bot_04_actions',
        # Scenario
        'processes.SCENARIO',
        'processes.SCENARIO.scenario_01_runner',
        'processes.SCENARIO.scenario_02_steps',
        'processes.SCENARIO.scenario_03_storage',
        'processes.SCENARIO.scenario_04_adb_actions',
        # UI
        'UI.theme',
        'UI.widgets',
        'UI.pattern_editor',
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
    console=False,
    disable_windowed_traceback=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / 'CORE' / 'mybotx.ico'),
    version_file=str(ROOT / 'BUILDER' / 'version_info.txt'),
)
