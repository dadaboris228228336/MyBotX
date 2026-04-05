#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCENARIO/scenario_04_adb_actions.py
ADB-команды для каждого типа шага сценария.
"""

import subprocess
import time
from pathlib import Path

PATTERNS_DIR = Path(__file__).parent.parent.parent / "processes" / "BOT" / "patterns"


def _get_adb() -> str:
    local = Path(__file__).parent.parent.parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    return str(local) if local.exists() else "adb"


def _run(device: str, args: list, timeout: int = 10):
    return subprocess.run([_get_adb(), "-s", device, *args],
                         capture_output=True, timeout=timeout)


def do_tap(device: str, x: int, y: int):
    _run(device, ["shell", "input", "tap", str(x), str(y)])


def do_swipe(device: str, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
    _run(device, ["shell", "input", "swipe",
                  str(x1), str(y1), str(x2), str(y2), str(duration)])


def do_key(device: str, keycode: int):
    _run(device, ["shell", "input", "keyevent", str(keycode)])


def do_text(device: str, text: str):
    _run(device, ["shell", "input", "text", text.replace(" ", "%s")])


def do_launch(device: str, package: str):
    _run(device, ["shell", "monkey", "-p", package,
                  "-c", "android.intent.category.LAUNCHER", "1"])


def do_stop(device: str, package: str):
    _run(device, ["shell", "am", "force-stop", package])


def do_pinch(device: str, zoom_in: bool, times: int):
    cx, cy, offset = 540, 960, 200
    for _ in range(times):
        if zoom_in:
            do_swipe(device, cx - offset, cy, cx, cy, 300)
            do_swipe(device, cx + offset, cy, cx, cy, 300)
        else:
            do_swipe(device, cx, cy, cx - offset, cy, 300)
            do_swipe(device, cx, cy, cx + offset, cy, 300)
        time.sleep(0.3)


def do_find_and_tap(device: str, pattern: str, threshold: float,
                    retries: int, retry_delay: float, log=None) -> bool:
    """
    Делает скриншот, ищет паттерн через OpenCV, кликает если нашёл.
    Повторяет retries раз с паузой retry_delay секунд.
    Возвращает True если нашёл и нажал.
    """
    import subprocess, io
    import numpy as np
    import cv2
    from PIL import Image

    pattern_path = PATTERNS_DIR / f"{pattern}.png"
    if not pattern_path.exists():
        if log:
            log(f"  ❌ Паттерн не найден: {pattern}.png", "error")
        return False

    template = cv2.imread(str(pattern_path))
    if template is None:
        if log:
            log(f"  ❌ Не удалось загрузить: {pattern}.png", "error")
        return False

    for attempt in range(1, retries + 1):
        # Скриншот
        result = _run(device, ["exec-out", "screencap", "-p"], timeout=15)
        if result.returncode != 0:
            if log:
                log("  ❌ Ошибка скриншота", "error")
            return False

        img = Image.open(io.BytesIO(result.stdout)).convert("RGB")
        screen = np.array(img)[:, :, ::-1]

        # Проверяем размеры
        if (template.shape[0] > screen.shape[0] or
                template.shape[1] > screen.shape[1]):
            if log:
                log(f"  ❌ Паттерн больше экрана! "
                    f"Паттерн: {template.shape[1]}x{template.shape[0]}, "
                    f"Экран: {screen.shape[1]}x{screen.shape[0]}", "error")
            return False

        # Template matching
        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            h, w = template.shape[:2]
            cx = max_loc[0] + w // 2
            cy = max_loc[1] + h // 2
            do_tap(device, cx, cy)
            if log:
                log(f"  ✅ '{pattern}' найден ({max_val:.2f}) → tap ({cx},{cy})", "success")
            return True

        if log:
            log(f"  ⚠ попытка {attempt}/{retries}: '{pattern}' не найден ({max_val:.2f})", "warning")
        if attempt < retries:
            time.sleep(retry_delay)

    if log:
        log(f"  ⏭ '{pattern}' не найден за {retries} попыток — пропускаем", "warning")
    return False
