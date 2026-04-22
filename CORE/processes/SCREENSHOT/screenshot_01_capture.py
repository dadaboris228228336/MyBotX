#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📸 SCREENSHOT/screenshot_01_capture.py
Единственная ответственность: захват экрана BlueStacks через ADB screencap.
Не импортирует cv2, easyocr или модули нажатий.
"""

import subprocess
import numpy as np
from pathlib import Path
from PIL import Image
import io


def _get_adb_path() -> str:
    local_adb = (
        Path(__file__).parent.parent.parent.parent
        / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    )
    return str(local_adb) if local_adb.exists() else "adb"


class ScreenshotCapture:
    """Захват экрана BlueStacks через ADB screencap → BGR numpy array."""

    def __init__(self, device_serial: str, log_callback=None):
        self.device = device_serial
        self.log = log_callback or print

    def capture(self) -> np.ndarray | None:
        """
        Делает скриншот через ADB exec-out screencap -p.
        Возвращает BGR numpy array или None при любой ошибке.
        Никогда не пробрасывает исключения наружу.
        """
        try:
            result = subprocess.run(
                [_get_adb_path(), "-s", self.device, "exec-out", "screencap", "-p"],
                capture_output=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode != 0:
                self.log(f"❌ Ошибка скриншота (код {result.returncode}): {result.stderr}")
                return None

            img = Image.open(io.BytesIO(result.stdout)).convert("RGB")
            arr = np.array(img)
            return arr[:, :, ::-1]  # RGB → BGR

        except Exception as e:
            self.log(f"❌ Исключение при скриншоте: {e}")
            return None

    def capture_and_save(self, path: str) -> bool:
        """Делает скриншот и сохраняет в файл. Возвращает False при любой ошибке."""
        arr = self.capture()
        if arr is None:
            return False
        try:
            img = Image.fromarray(arr[:, :, ::-1])  # BGR → RGB
            img.save(path)
            self.log(f"✅ Скриншот сохранён: {path}")
            return True
        except Exception as e:
            self.log(f"❌ Ошибка сохранения скриншота: {e}")
            return False
