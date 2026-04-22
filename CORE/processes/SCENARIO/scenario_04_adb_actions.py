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
                         capture_output=True, timeout=timeout,
                         creationflags=subprocess.CREATE_NO_WINDOW)


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


def do_pinch(device: str, zoom_in: bool, seconds: float = 2.0, log=None):
    """
    Zoom in/out в BlueStacks через настоящий мультитач pinch.
    Две точки движутся одновременно в противоположных направлениях.
    zoom_in=True  → точки расходятся (приближение)
    zoom_in=False → точки сходятся (отдаление)
    """
    try:
        import pyautogui
        import win32gui
        import win32con
        import ctypes
        import time as _time

        # Находим окно BlueStacks
        BS_TITLES = ["BlueStacks App Player", "BlueStacks", "HD-Player"]
        hwnd = None
        def cb(h, _):
            nonlocal hwnd
            t = win32gui.GetWindowText(h)
            if any(s.lower() in t.lower() for s in BS_TITLES) and win32gui.IsWindowVisible(h):
                hwnd = h
        win32gui.EnumWindows(cb, None)

        if not hwnd:
            if log:
                log("  ⚠ Окно BlueStacks не найдено", "warning")
            return

        # Центр окна BlueStacks
        rect = win32gui.GetWindowRect(hwnd)
        cx = (rect[0] + rect[2]) // 2
        cy = (rect[1] + rect[3]) // 2

        # Параметры pinch
        steps    = max(1, int(seconds * 20))   # шагов анимации
        interval = seconds / steps
        start_offset = 200   # начальное расстояние от центра (px)
        end_offset   = 50    # конечное расстояние от центра (px)

        if zoom_in:
            # Приближение: точки расходятся от центра
            offsets = [int(start_offset + (end_offset - start_offset) * i / steps)
                       for i in range(steps + 1)]
            offsets = list(reversed(offsets))  # от малого к большому
        else:
            # Отдаление: точки сходятся к центру
            offsets = [int(start_offset - (start_offset - end_offset) * i / steps)
                       for i in range(steps + 1)]

        # Выполняем pinch через Ctrl+scroll (надёжнее на BlueStacks)
        pyautogui.moveTo(cx, cy, duration=0.1)
        scroll_amount = 10 if zoom_in else -10
        ticks = max(1, int(seconds / 0.05))

        pyautogui.keyDown("ctrl")
        for _ in range(ticks):
            pyautogui.scroll(scroll_amount, x=cx, y=cy)
            _time.sleep(0.05)
        pyautogui.keyUp("ctrl")

        if log:
            d = "🔍 zoom_in" if zoom_in else "🔭 zoom_out"
            log(f"  {d} {seconds}с (Ctrl+scroll x{scroll_amount})", "dim")

    except ImportError as e:
        if log:
            log(f"  ❌ Нужен pyautogui/pywin32: pip install pyautogui pywin32", "error")
    except Exception as e:
        if log:
            log(f"  ❌ Ошибка zoom: {e}", "error")


def do_pinch_swipe(device: str, zoom_in: bool, times: int, log=None):
    """
    Zoom через Ctrl + scroll в окне BlueStacks.
    zoom_in=True  → приближение (scroll вверх)
    zoom_in=False → отдаление (scroll вниз)
    times — количество прокруток (каждая = 10 единиц)
    """
    try:
        import pyautogui
        import win32gui
        import time as _time

        BS_TITLES = ["BlueStacks App Player", "BlueStacks", "HD-Player"]
        hwnd = None
        def cb(h, _):
            nonlocal hwnd
            t = win32gui.GetWindowText(h)
            if any(s.lower() in t.lower() for s in BS_TITLES) and win32gui.IsWindowVisible(h):
                hwnd = h
        win32gui.EnumWindows(cb, None)

        if not hwnd:
            if log:
                log("  ⚠ Окно BlueStacks не найдено", "warning")
            return

        rect = win32gui.GetWindowRect(hwnd)
        cx = (rect[0] + rect[2]) // 2
        cy = (rect[1] + rect[3]) // 2

        pyautogui.moveTo(cx, cy, duration=0.05)
        scroll_amount = 10 if zoom_in else -10

        pyautogui.keyDown("ctrl")
        for _ in range(times):
            pyautogui.scroll(scroll_amount, x=cx, y=cy)
            _time.sleep(0.05)
        pyautogui.keyUp("ctrl")

        if log:
            d = "🔍 zoom_in" if zoom_in else "🔭 zoom_out"
            log(f"  {d} x{times} (Ctrl+scroll)", "dim")

    except Exception as e:
        if log:
            log(f"  ❌ Ошибка zoom: {e}", "error")


def do_find_and_tap(device: str, pattern: str, threshold: float,
                    retries: int, retry_delay: float, log=None) -> bool:
    """
    Делает скриншот, ищет паттерн через OpenCV, кликает если нашёл.
    Повторяет retries раз с паузой retry_delay секунд.
    Возвращает True если нашёл и нажал.
    Делегирует захват экрана → SCREENSHOT, поиск → OPENCV.
    """
    from ..SCREENSHOT import ScreenshotCapture
    from ..OPENCV import TemplateMatch

    pattern_path = PATTERNS_DIR / f"{pattern}.png"
    if not pattern_path.exists():
        if log:
            log(f"  ❌ Паттерн не найден: {pattern}.png", "error")
        return False

    screenshotter = ScreenshotCapture(device, log)
    matcher = TemplateMatch(PATTERNS_DIR, log)

    for attempt in range(1, retries + 1):
        screen = screenshotter.capture()
        if screen is None:
            if log:
                log("  ❌ Ошибка скриншота", "error")
            return False

        coords = matcher.find(screen, pattern, threshold)
        if coords is not None:
            cx, cy = coords
            do_tap(device, cx, cy)
            if log:
                log(f"  ✅ '{pattern}' найден → tap ({cx},{cy})", "success")
            return True

        if log:
            log(f"  ⚠ попытка {attempt}/{retries}: '{pattern}' не найден", "warning")
        if attempt < retries:
            time.sleep(retry_delay)

    if log:
        log(f"  ⏭ '{pattern}' не найден за {retries} попыток — пропускаем", "warning")
    return False
