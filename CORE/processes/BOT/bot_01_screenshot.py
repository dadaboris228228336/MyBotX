#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📸 BOT/bot_01_screenshot.py
Логика: Делает скриншот экрана BlueStacks через ADB и возвращает его как numpy array.
"""

import subprocess
import numpy as np
from pathlib import Path
from PIL import Image
import io


def _get_adb_path() -> str:
    local_adb = Path(__file__).parent.parent.parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    return str(local_adb) if local_adb.exists() else "adb"


class BotScreenshot:
    """Скриншот экрана BlueStacks через ADB"""

    def __init__(self, device_serial: str, log_callback=None):
        self.device = device_serial
        self.log = log_callback or print

    def capture(self) -> np.ndarray | None:
        """
        Делает скриншот через ADB screencap.
        Возвращает numpy array (BGR для OpenCV) или None при ошибке.
        """
        try:
            result = subprocess.run(
                [_get_adb_path(), "-s", self.device, "exec-out", "screencap", "-p"],
                capture_output=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode != 0:
                self.log(f"❌ Ошибка скриншота: {result.stderr}")
                return None

            # PNG bytes → PIL Image → numpy array
            img = Image.open(io.BytesIO(result.stdout)).convert("RGB")
            arr = np.array(img)

            # RGB → BGR (для OpenCV)
            return arr[:, :, ::-1]

        except Exception as e:
            self.log(f"❌ Исключение при скриншоте: {e}")
            return None

    def capture_and_save(self, path: str) -> bool:
        """Делает скриншот и сохраняет в файл (для отладки)"""
        arr = self.capture()
        if arr is None:
            return False
        try:
            img = Image.fromarray(arr[:, :, ::-1])  # BGR → RGB
            img.save(path)
            self.log(f"✅ Скриншот сохранён: {path}")
            return True
        except Exception as e:
            self.log(f"❌ Ошибка сохранения: {e}")
            return False
