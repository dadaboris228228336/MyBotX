#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 Processes Package - Разбитые процессы по модулям
Содержит отдельные файлы для каждого процесса всех модулей MyBotX
"""

# Game Launcher Processes
from .game_process_01_init import GameProcess01Init
from .game_process_02_check_app import GameProcess02CheckApp
from .game_process_03_play_market import GameProcess03PlayMarket
from .game_process_04_launch_direct import GameProcess04LaunchDirect
from .game_process_05_launch_intent import GameProcess05LaunchIntent
from .game_process_06_launch_monkey import GameProcess06LaunchMonkey
from .game_process_07_auto_launch import GameProcess07AutoLaunch

# ADB Manager Processes
from .adb_process_01_init import ADBProcess01Init
from .adb_process_02_check_port import ADBProcess02CheckPort
from .adb_process_03_find_port import ADBProcess03FindPort
from .adb_process_05_connect import ADBProcess05Connect

# BlueStacks Manager Processes
from .bs_process_01_init import BSProcess01Init
from .bs_process_02_search import BSProcess02Search
from .bs_process_03_status import BSProcess03Status
from .bs_process_04_control import BSProcess04Control

# Dependency Checker Processes
from .dep_process_01_init import DepProcess01Init
from .dep_process_02_parse import DepProcess02Parse
from .dep_process_03_check import DepProcess03Check
from .dep_process_04_install import DepProcess04Install

__all__ = [
    # Game Launcher Processes (7 процессов)
    'GameProcess01Init',
    'GameProcess02CheckApp',
    'GameProcess03PlayMarket',
    'GameProcess04LaunchDirect',
    'GameProcess05LaunchIntent',
    'GameProcess06LaunchMonkey',
    'GameProcess07AutoLaunch',

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
    
    # Dependency Checker Processes (4 процесса)
    'DepProcess01Init',
    'DepProcess02Parse',
    'DepProcess03Check',
    'DepProcess04Install',
    ]