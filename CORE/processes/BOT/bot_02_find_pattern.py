#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 BOT/bot_02_find_pattern.py
Логика: Ищет паттерн (картинку кнопки) на скриншоте через OpenCV Template Matching.
        Возвращает координаты центра найденного элемента.
"""

import cv2
import numpy as np
from pathlib import Path


PATTERNS_DIR = Path(__file__).parent / "patterns"


class BotFindPattern:
    """Поиск паттерна на скриншоте через OpenCV"""

    def __init__(self, log_callback=None):
        self.log = log_callback or print

    def find(self, screenshot: np.ndarray, pattern_name: str, threshold: float = 0.8) -> tuple | None:
        """
        Ищет паттерн на скриншоте.

        Args:
            screenshot:    numpy array скриншота (BGR)
            pattern_name:  имя файла паттерна без расширения (например "btn_attack")
            threshold:     порог совпадения 0.0-1.0 (0.8 = 80% совпадение)

        Returns:
            (x, y) координаты центра найденного паттерна или None
        """
        pattern_path = PATTERNS_DIR / f"{pattern_name}.png"

        if not pattern_path.exists():
            self.log(f"❌ Паттерн не найден: {pattern_path}")
            return None

        pattern = cv2.imread(str(pattern_path))
        if pattern is None:
            self.log(f"❌ Не удалось загрузить паттерн: {pattern_name}")
            return None

        # Template matching
        result = cv2.matchTemplate(screenshot, pattern, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < threshold:
            self.log(f"⚠️ Паттерн '{pattern_name}' не найден (совпадение: {max_val:.2f})")
            return None

        # Центр найденного паттерна
        h, w = pattern.shape[:2]
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2

        self.log(f"✅ Паттерн '{pattern_name}' найден: ({cx}, {cy}) совпадение: {max_val:.2f}")
        return (cx, cy)

    def find_all(self, screenshot: np.ndarray, pattern_name: str, threshold: float = 0.8) -> list:
        """
        Ищет ВСЕ вхождения паттерна на скриншоте.
        Полезно для поиска нескольких одинаковых кнопок (например, несколько шахт).

        Returns:
            список координат [(x1,y1), (x2,y2), ...]
        """
        pattern_path = PATTERNS_DIR / f"{pattern_name}.png"
        if not pattern_path.exists():
            return []

        pattern = cv2.imread(str(pattern_path))
        if pattern is None:
            return []

        result = cv2.matchTemplate(screenshot, pattern, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)

        h, w = pattern.shape[:2]
        points = []
        for pt in zip(*locations[::-1]):
            cx = pt[0] + w // 2
            cy = pt[1] + h // 2
            points.append((cx, cy))

        # Убираем дубликаты (точки ближе 20px считаются одним объектом)
        filtered = []
        for p in points:
            if not any(abs(p[0]-f[0]) < 20 and abs(p[1]-f[1]) < 20 for f in filtered):
                filtered.append(p)

        self.log(f"✅ Паттерн '{pattern_name}': найдено {len(filtered)} вхождений")
        return filtered
