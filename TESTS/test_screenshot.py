"""
Tests for SCREENSHOT/screenshot_01_capture.py
Validates: Requirements 1.2, 1.3, 1.4
"""

import io
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent / "CORE"))
from processes.SCREENSHOT import ScreenshotCapture, BotScreenshot


def _make_png_bytes(width: int = 10, height: int = 10) -> bytes:
    """Create minimal valid PNG bytes."""
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── Unit tests ────────────────────────────────────────────────────────────────

class TestScreenshotCapture:

    def test_capture_returns_none_on_nonzero_exit(self):
        """capture() returns None when ADB exits non-zero."""
        sc = ScreenshotCapture("emulator-5554")
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = b"error"
        with patch("subprocess.run", return_value=mock_result):
            result = sc.capture()
        assert result is None

    def test_capture_returns_none_on_exception(self):
        """capture() returns None when subprocess raises."""
        sc = ScreenshotCapture("emulator-5554")
        with patch("subprocess.run", side_effect=Exception("ADB not found")):
            result = sc.capture()
        assert result is None

    def test_capture_returns_bgr_array_for_valid_png(self):
        """capture() returns BGR ndarray for valid PNG bytes."""
        sc = ScreenshotCapture("emulator-5554")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = _make_png_bytes(20, 15)
        with patch("subprocess.run", return_value=mock_result):
            result = sc.capture()
        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape == (15, 20, 3)

    def test_capture_and_save_returns_false_when_capture_fails(self, tmp_path):
        """capture_and_save() returns False when capture() returns None."""
        sc = ScreenshotCapture("emulator-5554")
        with patch("subprocess.run", side_effect=Exception("fail")):
            result = sc.capture_and_save(str(tmp_path / "out.png"))
        assert result is False

    def test_capture_and_save_returns_true_on_success(self, tmp_path):
        """capture_and_save() saves file and returns True."""
        sc = ScreenshotCapture("emulator-5554")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = _make_png_bytes()
        out = tmp_path / "out.png"
        with patch("subprocess.run", return_value=mock_result):
            result = sc.capture_and_save(str(out))
        assert result is True
        assert out.exists()

    def test_botscreenshot_alias(self):
        """BotScreenshot is an alias for ScreenshotCapture."""
        assert BotScreenshot is ScreenshotCapture


# ── Property test P1 ──────────────────────────────────────────────────────────

# Feature: processes-restructure, Property 1: Screenshot capture never raises — returns ndarray or None
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    returncode=st.integers(min_value=-10, max_value=10),
    use_exception=st.booleans(),
)
def test_capture_never_raises(returncode, use_exception):
    """
    Property 1: For any ADB response, capture() never raises — returns ndarray or None.
    Validates: Requirements 1.2, 1.3, 1.4
    """
    sc = ScreenshotCapture("emulator-5554")

    if use_exception:
        with patch("subprocess.run", side_effect=OSError("mocked")):
            result = sc.capture()
    else:
        mock_result = MagicMock()
        mock_result.returncode = returncode
        mock_result.stdout = _make_png_bytes() if returncode == 0 else b""
        mock_result.stderr = b""
        with patch("subprocess.run", return_value=mock_result):
            result = sc.capture()

    # Must never raise — result is ndarray or None
    assert result is None or isinstance(result, np.ndarray)
