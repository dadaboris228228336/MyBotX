#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔢 OCR/ocr_02_parse_number.py
Парсинг чисел из OCR текста: "500K" → 500000, "1.5M" → 1500000, "O" → 0.
"""

import re


def parse_number(text: str) -> int | None:
    """
    Парсит число из строки с поддержкой суффиксов K/M/B и замены O→0.

    Примеры:
        "500"    → 500
        "1.5K"   → 1500
        "2.3M"   → 2300000
        "1B"     → 1000000000
        "O"      → 0
        "abc"    → None

    Args:
        text: строка из OCR

    Returns:
        целое число или None если не распознано
    """
    if not text:
        return None

    text = text.strip().upper()

    # Специальный случай: буква O как ноль
    if text == "O":
        return 0

    # Заменяем O на 0 в числовом контексте (например "1O5" → "105")
    text = text.replace("O", "0")

    # Убираем пробелы и запятые (разделители тысяч)
    text = text.replace(" ", "").replace(",", "")

    # Проверяем суффиксы K/M/B
    multiplier = 1
    if text.endswith("K"):
        multiplier = 1_000
        text = text[:-1]
    elif text.endswith("M"):
        multiplier = 1_000_000
        text = text[:-1]
    elif text.endswith("B"):
        multiplier = 1_000_000_000
        text = text[:-1]

    # Извлекаем число (целое или с точкой)
    match = re.search(r"[\d.]+", text)
    if not match:
        return None

    try:
        num = float(match.group())
        return int(num * multiplier)
    except (ValueError, OverflowError):
        return None
