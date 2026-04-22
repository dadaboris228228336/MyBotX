#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 OPENCV/cv_01_template_match.py
Единственная ответственность: поиск паттерна на скриншоте через OpenCV Template Matching.
Не импортирует subprocess, easyocr или ADB-модули.
"""

import cv2
import numpy as np
from pathlib import Path


class TemplateMatch:
    """Поиск паттерна на скриншоте через cv2.TM_CCOEFF_NORMED."""

    def __init__(self, patterns_dir: Path, log_callback=None):
        self.patterns_dir = Path(patterns_dir)
        self.log = log_callback or print

    def find(self, screenshot: np.ndarray, pattern_name: str,
             threshold: float = 0.8) -> tuple | None:
        """
        Ищет паттерн на скриншоте.

        Args:
            screenshot:   BGR numpy array скриншота
            pattern_name: имя файла без расширения (например "ATAKA")
            threshold:    порог совпадения 0.0-1.0

        Returns:
            (cx, cy) центр найденного паттерна или None
        """
        pattern_path = self.patterns_dir / f"{pattern_name}.png"

        if not pattern_path.exists():
            self.log(f"❌ Паттерн не найден: {pattern_path}")
            return None

        pattern = cv2.imread(str(pattern_path))
        if pattern is None:
            self.log(f"❌ Не удалось загрузить паттерн: {pattern_name}")
            return None

        # Проверка размеров
        sh, sw = screenshot.shape[:2]
        ph, pw = pattern.shape[:2]
        if ph > sh or pw > sw:
            self.log(f"❌ Паттерн '{pattern_name}' ({pw}x{ph}) больше скриншота ({sw}x{sh})")
            return None

        result = cv2.matchTemplate(screenshot, pattern, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < threshold:
            self.log(f"⚠️ Паттерн '{pattern_name}' не найден (совпадение: {max_val:.2f})")
            return None

        cx = max_loc[0] + pw // 2
        cy = max_loc[1] + ph // 2
        self.log(f"✅ Паттерн '{pattern_name}' найден: ({cx}, {cy}) совпадение: {max_val:.2f}")
        return (cx, cy)

    def find_all(self, screenshot: np.ndarray, pattern_name: str,
                 threshold: float = 0.8) -> list:
        """
        Ищет ВСЕ вхождения паттерна на скриншоте.

        Returns:
            список [(cx, cy), ...] без дубликатов в радиусе 20px
        """
        pattern_path = self.patterns_dir / f"{pattern_name}.png"

        if not pattern_path.exists():
            self.log(f"❌ Паттерн не найден: {pattern_path}")
            return []

        pattern = cv2.imread(str(pattern_path))
        if pattern is None:
            return []

        sh, sw = screenshot.shape[:2]
        ph, pw = pattern.shape[:2]
        if ph > sh or pw > sw:
            self.log(f"❌ Паттерн '{pattern_name}' больше скриншота")
            return []

        result = cv2.matchTemplate(screenshot, pattern, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)

        points = []
        for pt in zip(*locations[::-1]):
            cx = pt[0] + pw // 2
            cy = pt[1] + ph // 2
            points.append((cx, cy))

        # Дедупликация: точки ближе 20px считаются одним объектом
        filtered = []
        for p in points:
            if not any(abs(p[0] - f[0]) < 20 and abs(p[1] - f[1]) < 20 for f in filtered):
                filtered.append(p)

        self.log(f"✅ Паттерн '{pattern_name}': найдено {len(filtered)} вхождений")
        return filtered
