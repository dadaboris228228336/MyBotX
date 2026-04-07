"""
BASE_VIEW — модуль управления видом базы Clash of Clans.

Публичные интерфейсы:
    load_constants(path)        — загрузка констант из JSON
    save_constants(data, path)  — сохранение констант в JSON
"""

from .base_00_constants import load_constants, save_constants

__all__ = [
    "load_constants",
    "save_constants",
]
