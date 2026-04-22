#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⏱️ OCR/ocr_03_parse_timer.py
Парсинг таймеров из OCR текста: "1h 30m" → 5400, "01:30:00" → 5400.
"""

import re


def parse_timer(text: str) -> int | None:
    """
    Конвертирует строку таймера в общее количество секунд.

    Поддерживаемые форматы:
        "HH:MM:SS"  → часы*3600 + минуты*60 + секунды
        "MM:SS"     → минуты*60 + секунды
        "Xh Ym Zs"  → любая комбинация часов/минут/секунд
        "Xh Ym"     → часы + минуты
        "Xm Zs"     → минуты + секунды
        "Xs"        → только секунды

    Args:
        text: строка из OCR

    Returns:
        общее количество секунд или None если формат не распознан
    """
    if not text:
        return None

    text = text.strip()

    # Заменяем O→0 (частая ошибка OCR)
    text = text.replace("O", "0").replace("o", "0")

    # Формат HH:MM:SS
    m = re.fullmatch(r"(\d{1,2}):(\d{2}):(\d{2})", text)
    if m:
        h, mn, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return h * 3600 + mn * 60 + s

    # Формат MM:SS
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", text)
    if m:
        mn, s = int(m.group(1)), int(m.group(2))
        return mn * 60 + s

    # Натуральный формат: "1h 30m 15s" (любая комбинация)
    total = 0
    found = False

    h_match = re.search(r"(\d+)\s*h", text, re.IGNORECASE)
    if h_match:
        total += int(h_match.group(1)) * 3600
        found = True

    m_match = re.search(r"(\d+)\s*m(?!s)", text, re.IGNORECASE)
    if m_match:
        total += int(m_match.group(1)) * 60
        found = True

    s_match = re.search(r"(\d+)\s*s", text, re.IGNORECASE)
    if s_match:
        total += int(s_match.group(1))
        found = True

    if found:
        return total

    return None
