#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪟 BLUESTACKS/bs_05_window.py
Управление окном BlueStacks и разрешением Android внутри эмулятора.

Фиксированное разрешение: 1280x720 (16:9, стандарт Clash of Clans).
Устанавливается через ADB — меняет реальное разрешение Android,
поэтому все скриншоты будут строго 1280x720 независимо от размера окна.
"""

import subprocess
from pathlib import Path

FIXED_WIDTH  = 1280
FIXED_HEIGHT = 720

BS_WINDOW_TITLES = ["BlueStacks App Player", "BlueStacks", "HD-Player"]


def _get_adb() -> str:
    local = Path(__file__).parent.parent.parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    return str(local) if local.exists() else "adb"


def set_fixed_resolution(device: str, log=None) -> bool:
    """
    Фиксирует разрешение Android внутри BlueStacks через ADB.
    adb shell wm size 1280x720
    Все последующие скриншоты будут строго 1280x720.
    """
    def _log(msg, tag="info"):
        if log:
            log(msg, tag)

    try:
        result = subprocess.run(
            [_get_adb(), "-s", device, "shell", "wm", "size",
             f"{FIXED_WIDTH}x{FIXED_HEIGHT}"],
            capture_output=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode == 0:
            _log(f"✅ Разрешение Android зафиксировано: {FIXED_WIDTH}x{FIXED_HEIGHT}", "success")
            return True
        else:
            _log(f"⚠ Не удалось задать разрешение: {result.stderr.decode()}", "warning")
            return False
    except Exception as e:
        _log(f"⚠ Ошибка wm size: {e}", "warning")
        return False


def get_current_resolution(device: str) -> tuple[int, int] | None:
    """Возвращает текущее разрешение Android (ширина, высота) или None."""
    try:
        result = subprocess.run(
            [_get_adb(), "-s", device, "shell", "wm", "size"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        # Вывод: "Physical size: 1280x720" или "Override size: 1280x720"
        for line in result.stdout.splitlines():
            if "size:" in line.lower():
                parts = line.split(":")[-1].strip().split("x")
                if len(parts) == 2:
                    return int(parts[0]), int(parts[1])
    except Exception:
        pass
    return None


def minimize_window(log=None) -> bool:
    """Сворачивает окно BlueStacks через win32gui."""
    try:
        import win32gui, win32con
        hwnd = _find_bs_hwnd()
        if not hwnd:
            return False
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        if log:
            log("📱 BlueStacks свёрнут", "info")
        return True
    except Exception:
        return False


def restore_window(log=None) -> bool:
    """Разворачивает окно BlueStacks через win32gui."""
    try:
        import win32gui, win32con
        hwnd = _find_bs_hwnd()
        if not hwnd:
            return False
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        if log:
            log("📱 BlueStacks развёрнут", "info")
        return True
    except Exception:
        return False


def _find_bs_hwnd():
    try:
        import win32gui
        found = []
        def cb(hwnd, _):
            t = win32gui.GetWindowText(hwnd)
            if any(s.lower() in t.lower() for s in BS_WINDOW_TITLES):
                if win32gui.IsWindowVisible(hwnd):
                    found.append(hwnd)
        win32gui.EnumWindows(cb, None)
        return found[0] if found else None
    except Exception:
        return None
