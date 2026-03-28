#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 Processes Package - Разбитые процессы по модулям
Содержит отдельные файлы для каждого процесса всех модулей MyBotX
"""

# ADB Manager Processes
from .ADB import (
    ADBProcess01Init,
    ADBProcess02CheckPort,
    ADBProcess03FindPort,
    ADBProcess05Connect,
)

# BlueStacks Manager Processes
from .BLUESTACKS import (
    BSProcess01Init,
    BSProcess02Search,
    BSProcess03Status,
    BSProcess04Control,
)

# Game Launcher Processes
from .GAME import (
    GameProcess01Init,
    GameProcess02CheckApp,
    GameProcess03PlayMarket,
    GameProcess04LaunchDirect,
    GameProcess05LaunchIntent,
    GameProcess06LaunchMonkey,
    GameProcess07AutoLaunch,
)

# Dependency Checker Processes
from .DEPENDENCIES import (
    DepProcess01Init,
    DepProcess02Parse,
    DepProcess03Check,
    DepProcess04Install,
)

__all__ = [
    # ADB Manager Processes (4 процесса)
    'ADBProcess01Init',
    'ADBProcess02CheckPort',
    'ADBProcess03FindPort',
    'ADBProcess05Connect',

    # BlueStacks Manager Processes (4 процесса)
    'BSProcess01Init',
    'BSProcess02Search',
    'BSProcess03Status',
    'BSProcess04Control',

    # Game Launcher Processes (7 процессов)
    'GameProcess01Init',
    'GameProcess02CheckApp',
    'GameProcess03PlayMarket',
    'GameProcess04LaunchDirect',
    'GameProcess05LaunchIntent',
    'GameProcess06LaunchMonkey',
    'GameProcess07AutoLaunch',

    # Dependency Checker Processes (4 процесса)
    'DepProcess01Init',
    'DepProcess02Parse',
    'DepProcess03Check',
    'DepProcess04Install',
]
