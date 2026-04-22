"""
SCREENSHOT — захват экрана через ADB screencap.
"""
from .screenshot_01_capture import ScreenshotCapture

# Алиас для обратной совместимости с main.py и старым кодом
BotScreenshot = ScreenshotCapture

__all__ = ["ScreenshotCapture", "BotScreenshot"]
