"""
Import smoke tests for processes-restructure.
Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 7.6, 7.7
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "CORE"))


def test_screenshot_module_imports():
    from processes.SCREENSHOT import ScreenshotCapture
    assert ScreenshotCapture is not None


def test_screenshot_botscreenshot_alias():
    from processes.SCREENSHOT import BotScreenshot, ScreenshotCapture
    assert BotScreenshot is ScreenshotCapture


def test_opencv_module_imports():
    from processes.OPENCV import TemplateMatch
    assert TemplateMatch is not None


def test_opencv_utils_import():
    from processes.OPENCV import resize, to_grayscale, threshold, scale_up
    assert all(callable(f) for f in [resize, to_grayscale, threshold, scale_up])


def test_ocr_module_imports():
    from processes.OCR import parse_number, parse_timer
    assert callable(parse_number)
    assert callable(parse_timer)


def test_bot_module_imports():
    from processes.BOT import BotTap, BotActions
    assert BotTap is not None
    assert BotActions is not None


def test_bot_actions_from_new_path():
    from processes.BOT.bot_02_actions import BotActions
    assert BotActions is not None


def test_bot_tap_from_new_path():
    from processes.BOT.bot_01_tap import BotTap
    assert BotTap is not None


def test_processes_init_exports_all_new_modules():
    import processes
    assert hasattr(processes, "ScreenshotCapture")
    assert hasattr(processes, "TemplateMatch")
    assert hasattr(processes, "parse_number")
    assert hasattr(processes, "parse_timer")
    assert hasattr(processes, "BotTap")
    assert hasattr(processes, "BotActions")


def test_old_bot_files_removed():
    """Old bot_01_screenshot.py and bot_02_find_pattern.py must not exist."""
    old1 = Path(__file__).parent.parent / "CORE/processes/BOT/bot_01_screenshot.py"
    old2 = Path(__file__).parent.parent / "CORE/processes/BOT/bot_02_find_pattern.py"
    assert not old1.exists(), "bot_01_screenshot.py should have been deleted"
    assert not old2.exists(), "bot_02_find_pattern.py should have been deleted"
