#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👆 BOT/bot_03_tap.py
Логика: Нажатие на экран BlueStacks по координатам через ADB input tap.
        Также поддерживает свайп и долгое нажатие.
"""

import subprocess
import time
from pathlib import Path


def _get_adb_path() -> str:
    local_adb = Path(__file__).parent.parent.parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    return str(local_adb) if local_adb.exists() else "adb"


class BotTap:
    """Нажатие на экран через ADB"""

    def __init__(self, device_serial: str, log_callback=None):
        self.device = device_serial
        self.log = log_callback or print

    def tap(self, x: int, y: int) -> bool:
        """Одиночное нажатие по координатам"""
        try:
            result = subprocess.run(
                [_get_adb_path(), "-s", self.device, "shell", "input", "tap", str(x), str(y)],
                capture_output=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                self.log(f"👆 Нажатие: ({x}, {y})")
                return True
            return False
        except Exception as e:
            self.log(f"❌ Ошибка нажатия: {e}")
            return False

    def tap_pattern(self, coords: tuple) -> bool:
        """Нажатие по координатам из find_pattern"""
        if coords is None:
            return False
        return self.tap(coords[0], coords[1])

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> bool:
        """Свайп от (x1,y1) до (x2,y2)"""
        try:
            result = subprocess.run(
                [_get_adb_path(), "-s", self.device, "shell", "input", "swipe",
                 str(x1), str(y1), str(x2), str(y2), str(duration_ms)],
                capture_output=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.log(f"👆 Свайп: ({x1},{y1}) → ({x2},{y2})")
            return result.returncode == 0
        except Exception as e:
            self.log(f"❌ Ошибка свайпа: {e}")
            return False

    def long_tap(self, x: int, y: int, duration_ms: int = 1000) -> bool:
        """Долгое нажатие"""
        return self.swipe(x, y, x, y, duration_ms)

    def tap_and_wait(self, x: int, y: int, wait_sec: float = 1.0) -> bool:
        """Нажатие с ожиданием после"""
        result = self.tap(x, y)
        time.sleep(wait_sec)
        return result
