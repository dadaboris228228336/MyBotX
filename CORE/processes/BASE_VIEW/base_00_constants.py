"""
Хелпер для загрузки и сохранения констант BASE_VIEW из/в JSON-файл.
"""

import json
import os
from typing import Any


def load_constants(path: str) -> dict:
    """
    Загружает константы из JSON-файла.

    Args:
        path: путь к JSON-файлу констант

    Returns:
        Словарь с константами. При ошибке чтения возвращает пустой словарь.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        print(f"[BASE_VIEW] Предупреждение: не удалось загрузить константы из {path}: {e}")
        return {}


def save_constants(data: dict, path: str) -> bool:
    """
    Сохраняет константы в JSON-файл.

    Args:
        data: словарь с константами
        path: путь к JSON-файлу для записи

    Returns:
        True если сохранение прошло успешно, False при ошибке.
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (OSError, TypeError, ValueError) as e:
        print(f"[BASE_VIEW] Ошибка: не удалось сохранить константы в {path}: {e}")
        return False
