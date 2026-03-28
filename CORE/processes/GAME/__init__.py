#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎮 GAME Package - Процессы запуска игры Clash of Clans
"""

from .game_01_init import GameProcess01Init
from .game_02_check_app import GameProcess02CheckApp
from .game_03_play_market import GameProcess03PlayMarket
from .game_04_launch_direct import GameProcess04LaunchDirect
from .game_05_launch_intent import GameProcess05LaunchIntent
from .game_06_launch_monkey import GameProcess06LaunchMonkey
from .game_07_auto_launch import GameProcess07AutoLaunch

__all__ = [
    'GameProcess01Init',
    'GameProcess02CheckApp',
    'GameProcess03PlayMarket',
    'GameProcess04LaunchDirect',
    'GameProcess05LaunchIntent',
    'GameProcess06LaunchMonkey',
    'GameProcess07AutoLaunch',
]
