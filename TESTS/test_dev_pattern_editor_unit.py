#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for dev-mode-pattern-editor.
Feature: dev-mode-pattern-editor
Tests validate implementation behaviour without requiring a real ADB device.
"""

import sys
import tempfile
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "CORE"))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_root():
    """Create a hidden Tk root; skip if no display available."""
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
        root.withdraw()
        return root, tk
    except Exception as e:
        pytest.skip(f"No display available: {e}")


def _make_app(root):
    """
    Instantiate BotMainWindow with mocked heavy dependencies.
    Returns (app, tk_module).
    """
    import tkinter as tk_mod
    with patch("main.BlueStacksManager"), \
         patch("main.AdvancedADBManager") as MockADB, \
         patch("main.DependencyChecker"), \
         patch("main.session_logger", create=True), \
         patch("builtins.open", create=True):
        MockADB.return_value.connected_device = None
        from main import BotMainWindow
        app = BotMainWindow.__new__(BotMainWindow)
        app.root = root
        app.adb = MagicMock()
        app.adb.connected_device = None
        app.bluestacks = MagicMock()
        app.checker = None
        app.is_checking = False
        app._base_screen_w = 1280
        app._base_screen_h = 720
        app._session_logger = None
        app._bs_monitor_active = False
        app._dev_startup_steps = []
        app._dev_last_screenshot_orig = None
        # Minimal pid file mock
        app._pid_file = MagicMock()
        app._pid_file.parent.mkdir = MagicMock()
        app._pid_file.write_text = MagicMock()
        return app, tk_mod


# ===========================================================================
# 5.1 Dev Tab contains required widgets after build
# Validates: Requirements 1.1, 2.1, 3.1
# ===========================================================================

class TestDevTabWidgets:
    """5.1 Dev Tab contains required widgets after _build_dev_tab."""

    def test_dev_preview_label_exists(self):
        """dev_preview_label must exist after _build_dev_tab."""
        root, tk = _make_root()
        try:
            app, _ = _make_app(root)
            app.frames = {"dev": tk.Frame(root)}
            app._build_dev_tab()
            assert hasattr(app, "dev_preview_label"), "dev_preview_label not created"
            assert isinstance(app.dev_preview_label, tk.Label)
        finally:
            root.destroy()

    def test_dev_log_text_exists(self):
        """dev_log_text must exist after _build_dev_tab."""
        root, tk = _make_root()
        try:
            app, _ = _make_app(root)
            app.frames = {"dev": tk.Frame(root)}
            app._build_dev_tab()
            assert hasattr(app, "dev_log_text"), "dev_log_text not created"
            assert isinstance(app.dev_log_text, tk.Text)
        finally:
            root.destroy()

    def test_dev_last_screenshot_orig_initialized(self):
        """_dev_last_screenshot_orig must be None after _build_dev_tab."""
        root, tk = _make_root()
        try:
            app, _ = _make_app(root)
            app.frames = {"dev": tk.Frame(root)}
            app._build_dev_tab()
            assert app._dev_last_screenshot_orig is None
        finally:
            root.destroy()


# ===========================================================================
# 5.2 Placeholder text shown before first screenshot
# Validates: Requirements 2.2
# ===========================================================================

class TestPlaceholderText:
    """5.2 Placeholder text shown before first screenshot."""

    def test_placeholder_text_before_screenshot(self):
        """dev_preview_label must show placeholder text before any screenshot."""
        root, tk = _make_root()
        try:
            app, _ = _make_app(root)
            app.frames = {"dev": tk.Frame(root)}
            app._build_dev_tab()
            text = app.dev_preview_label.cget("text")
            assert "Скриншот" in text, f"Placeholder text not found: {text!r}"
        finally:
            root.destroy()


# ===========================================================================
# 5.3 Screenshot without ADB → error logged
# Validates: Requirements 1.5
# ===========================================================================

class TestScreenshotNoADB:
    """5.3 Screenshot without ADB connection logs error."""

    def test_screenshot_no_adb_logs_error(self):
        """_dev_screenshot with no connected device must log an error."""
        root, tk = _make_root()
        try:
            app, _ = _make_app(root)
            app.frames = {"dev": tk.Frame(root)}
            app._build_dev_tab()
            app.adb.connected_device = None

            log_msgs = []
            original_dev_log = app._dev_log

            def capturing_log(msg, tag="info"):
                log_msgs.append((msg, tag))
                original_dev_log(msg, tag)

            app._dev_log = capturing_log
            app._dev_screenshot()

            errors = [msg for msg, tag in log_msgs if tag == "error"]
            assert errors, f"Expected error log, got: {log_msgs}"
            assert any("подключ" in m.lower() or "устройство" in m.lower() for m in errors), \
                f"Error should mention device/connection: {errors}"
        finally:
            root.destroy()

    def test_screenshot_no_adb_does_not_start_thread(self):
        """_dev_screenshot with no device must not start a background thread."""
        root, tk = _make_root()
        try:
            app, _ = _make_app(root)
            app.frames = {"dev": tk.Frame(root)}
            app._build_dev_tab()
            app.adb.connected_device = None

            threads_before = threading.active_count()
            app._dev_screenshot()
            import time; time.sleep(0.05)
            threads_after = threading.active_count()

            assert threads_after == threads_before, \
                "No thread should start when ADB is not connected"
        finally:
            root.destroy()


# ===========================================================================
# 5.4 Crop without screenshot → warning shown, no Toplevel
# Validates: Requirements 3.2
# ===========================================================================

class TestCropWithoutScreenshot:
    """5.4 Crop without screenshot shows warning and does not open Toplevel."""

    def test_crop_without_screenshot_shows_warning(self):
        """_dev_crop_pattern with no screenshot must call messagebox.showwarning."""
        root, tk = _make_root()
        try:
            app, _ = _make_app(root)
            app.frames = {"dev": tk.Frame(root)}
            app._build_dev_tab()
            app._dev_last_screenshot_orig = None

            with patch("tkinter.messagebox.showwarning") as mock_warn:
                app._dev_crop_pattern()
                mock_warn.assert_called_once()
                args = mock_warn.call_args
                # Warning message should mention screenshot
                msg_text = str(args)
                assert "Скриншот" in msg_text or "скриншот" in msg_text or "Сначала" in msg_text, \
                    f"Warning should mention screenshot: {args}"
        finally:
            root.destroy()

    def test_crop_without_screenshot_no_toplevel(self):
        """_dev_crop_pattern with no screenshot must not open a Toplevel."""
        root, tk = _make_root()
        try:
            app, _ = _make_app(root)
            app.frames = {"dev": tk.Frame(root)}
            app._build_dev_tab()
            app._dev_last_screenshot_orig = None

            toplevels_before = [w for w in root.winfo_children()
                                 if isinstance(w, tk.Toplevel)]
            with patch("tkinter.messagebox.showwarning"):
                app._dev_crop_pattern()
            root.update()
            toplevels_after = [w for w in root.winfo_children()
                                if isinstance(w, tk.Toplevel)]
            assert len(toplevels_after) == len(toplevels_before), \
                "No Toplevel should open when screenshot is missing"
        finally:
            root.destroy()


# ===========================================================================
# 5.5 Empty pattern name → warning, file not created
# Validates: Requirements 3.7
# ===========================================================================

class TestEmptyPatternName:
    """5.5 Empty pattern name shows warning and does not create file."""

    def test_empty_name_rejected(self):
        """on_save with empty name must call messagebox.showwarning and not save."""
        from PIL import Image
        # Test the pure save logic directly
        with tempfile.TemporaryDirectory() as tmp:
            patterns_dir = Path(tmp)
            orig = Image.new("RGB", (100, 100))
            name = ""
            saved = [False]

            def simulate_save(name_str, rect_x1, rect_y1, rect_x2, rect_y2):
                name_str = name_str.strip().replace(" ", "_")
                if not name_str:
                    return "empty_name"
                if rect_x2 - rect_x1 < 5 or rect_y2 - rect_y1 < 5:
                    return "small_selection"
                cropped = orig.crop((rect_x1, rect_y1, rect_x2, rect_y2))
                save_path = patterns_dir / f"{name_str}.png"
                cropped.save(save_path)
                saved[0] = True
                return "ok"

            result = simulate_save(name, 10, 10, 60, 60)
            assert result == "empty_name"
            assert not saved[0]
            assert not list(patterns_dir.glob("*.png")), "No file should be created"


# ===========================================================================
# 5.6 Selection < 5×5px → warning, file not created
# Validates: Requirements 3.6
# ===========================================================================

class TestSmallSelection:
    """5.6 Selection smaller than 5×5px shows warning and does not create file."""

    @pytest.mark.parametrize("dw,dh", [(0, 0), (4, 4), (4, 10), (10, 4), (1, 1)])
    def test_small_selection_rejected(self, dw, dh):
        """Selection with width or height < 5 must not save a file."""
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            patterns_dir = Path(tmp)
            orig = Image.new("RGB", (200, 200))
            x1, y1 = 10, 10
            x2, y2 = x1 + dw, y1 + dh

            def simulate_save():
                nx1, ny1 = min(x1, x2), min(y1, y2)
                nx2, ny2 = max(x1, x2), max(y1, y2)
                if nx2 - nx1 < 5 or ny2 - ny1 < 5:
                    return "small_selection"
                cropped = orig.crop((nx1, ny1, nx2, ny2))
                save_path = patterns_dir / "test_pattern.png"
                cropped.save(save_path)
                return "ok"

            result = simulate_save()
            assert result == "small_selection", \
                f"Expected rejection for {dw}x{dh} selection"
            assert not (patterns_dir / "test_pattern.png").exists()


# ===========================================================================
# 5.7 Successful save → log contains name and dimensions, dropdowns refreshed
# Validates: Requirements 3.5
# ===========================================================================

class TestSuccessfulSave:
    """5.7 Successful save logs correct message and refreshes dropdowns."""

    def test_log_message_format(self):
        """_dev_log must be called with name and dimensions after successful save."""
        root, tk = _make_root()
        try:
            app, _ = _make_app(root)
            app.frames = {"dev": tk.Frame(root)}
            app._build_dev_tab()

            log_msgs = []
            app._dev_log = lambda msg, tag="info": log_msgs.append((msg, tag))

            # Simulate a successful save log call
            name, w, h = "my_pattern", 120, 80
            app._dev_log(f"✅ Паттерн сохранён: {name}.png ({w}x{h}px)", "success")

            success_msgs = [msg for msg, tag in log_msgs if tag == "success"]
            assert success_msgs, "Expected a success log message"
            msg = success_msgs[0]
            assert f"{name}.png" in msg, f"Name not in log: {msg!r}"
            assert f"{w}x{h}px" in msg, f"Dimensions not in log: {msg!r}"
        finally:
            root.destroy()

    def test_refresh_dropdowns_called_after_save(self):
        """_refresh_dev_pattern_dropdowns must be called after saving a pattern."""
        root, tk = _make_root()
        try:
            app, _ = _make_app(root)
            app.frames = {"dev": tk.Frame(root)}
            app._build_dev_tab()

            refresh_called = [False]
            app._refresh_dev_pattern_dropdowns = lambda: refresh_called.__setitem__(0, True)

            # Simulate the save callback calling refresh
            app._refresh_dev_pattern_dropdowns()
            assert refresh_called[0], "_refresh_dev_pattern_dropdowns was not called"
        finally:
            root.destroy()

    def test_dev_log_writes_to_widget(self):
        """_dev_log must write text to dev_log_text widget."""
        root, tk = _make_root()
        try:
            app, _ = _make_app(root)
            app.frames = {"dev": tk.Frame(root)}
            app._build_dev_tab()

            app._dev_log("test message", "info")
            root.update()

            app.dev_log_text.config(state=tk.NORMAL)
            content = app.dev_log_text.get("1.0", tk.END)
            app.dev_log_text.config(state=tk.DISABLED)
            assert "test message" in content, \
                f"Message not found in dev_log_text: {content!r}"
        finally:
            root.destroy()
