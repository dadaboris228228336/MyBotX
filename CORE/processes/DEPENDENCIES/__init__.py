#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📦 DEPENDENCIES Package - Процессы управления Python зависимостями
"""

from .dep_01_init import DepProcess01Init
from .dep_02_parse import DepProcess02Parse
from .dep_03_check import DepProcess03Check
from .dep_04_install import DepProcess04Install

__all__ = [
    'DepProcess01Init',
    'DepProcess02Parse',
    'DepProcess03Check',
    'DepProcess04Install',
]
