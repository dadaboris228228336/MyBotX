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
    Zoom in/out в BlueStacks через Ctrl + колёсико мыши.
    seconds — сколько секунд крутить колёсико.
    """
    try:
        import pyautogui
        import win32gui
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

        # Перемещаем курсор в центр окна BlueStacks и крутим колёсико
        pyautogui.moveTo(cx, cy, duration=0.1)
        # scroll(-3) = вниз = zoom OUT (отдалить), scroll(3) = вверх = zoom IN (приблизить)
        # В BlueStacks с Ctrl: вниз = отдалить, вверх = приблизить
        scroll_dir = -3 if zoom_in else 3
        interval   = 0.05
        ticks      = int(seconds / interval)

        pyautogui.keyDown("ctrl")
        for _ in range(ticks):
            pyautogui.scroll(scroll_dir, x=cx, y=cy)
            _time.sleep(interval)
        pyautogui.keyUp("ctrl")

        if log:
            d = "🔍 zoom_in" if zoom_in else "🔭 zoom_out"
            log(f"  {d} {seconds}с (Ctrl+scroll)", "dim")

    except ImportError as e:
        if log:
            log(f"  ❌ Нужен pyautogui/pywin32: pip install pyautogui pywin32", "error")
    except Exception as e:
        if log:
            log(f"  ❌ Ошибка zoom: {e}", "error")


def do_pinch_swipe(device: str, zoom_in: bool, times: int, log=None):
    """
    Pinch через два параллельных свайпа.
    Координаты для горизонтального экрана 1280x720: центр (640, 360).
    """
    import threading
    cx, cy, offset = 640, 360, 200  # горизонтальный экран CoC

    def swipe1():
        if zoom_in:
            _run(device, ["shell", "input", "swipe",
                          str(cx - offset), str(cy), str(cx - 50), str(cy), "500"])
        else:
            _run(device, ["shell", "input", "swipe",
                          str(cx - 50), str(cy), str(cx - offset), str(cy), "500"])

    def swipe2():
        if zoom_in:
            _run(device, ["shell", "input", "swipe",
                          str(cx + offset), str(cy), str(cx + 50), str(cy), "500"])
        else:
            _run(device, ["shell", "input", "swipe",
                          str(cx + 50), str(cy), str(cx + offset), str(cy), "500"])

    for _ in range(times):
        t1 = threading.Thread(target=swipe1)
        t2 = threading.Thread(target=swipe2)
        t1.start(); t2.start()
        t1.join();  t2.join()
        time.sleep(0.5)

    if log:
        direction = "🔍 pinch_in" if zoom_in else "🔭 pinch_out"
        log(f"  {direction} x{times} (parallel swipe, center={cx},{cy})", "dim")


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
