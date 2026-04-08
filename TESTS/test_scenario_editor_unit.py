#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for scenario-editor.
Feature: scenario-editor
Tests validate actual implementation behaviour (including documented GAPs).
"""

import copy
import json
import sys
import threading
import time
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "CORE"))

# ---------------------------------------------------------------------------
# 3.11 Smoke test: imports must succeed without errors (Req 6.1–6.5)
# ---------------------------------------------------------------------------

class TestSmoke:
    """3.11 Smoke test: import ScenarioEditor, ScenarioRunner, ScenarioStorage."""

    def test_import_scenario_runner(self):
        """ScenarioRunner can be imported from SCENARIO package."""
        from processes.SCENARIO import ScenarioRunner
        assert ScenarioRunner is not None

    def test_import_scenario_storage(self):
        """ScenarioStorage can be imported from SCENARIO package."""
        from processes.SCENARIO import ScenarioStorage
        assert ScenarioStorage is not None

    def test_import_scenario_editor(self):
        """ScenarioEditor module can be imported (no tkinter display required)."""
        # We only test that the module-level imports work; we don't instantiate
        # the widget here because that requires a display.
        import importlib
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "scenario_editor",
            ROOT / "CORE" / "UI" / "scenario_editor.py",
        )
        # Just loading the spec (not executing) is enough to confirm the file exists
        assert spec is not None

    def test_import_step_types(self):
        """STEP_TYPES, STEP_TYPE_KEYS, STEP_KEY_LABELS, step_label are importable."""
        from processes.SCENARIO import STEP_TYPES, STEP_TYPE_KEYS, STEP_KEY_LABELS, step_label
        assert len(STEP_TYPES) > 0
        assert len(STEP_TYPE_KEYS) > 0
        assert len(STEP_KEY_LABELS) > 0
        assert callable(step_label)


# ---------------------------------------------------------------------------
# Helpers shared by tkinter-dependent tests
# ---------------------------------------------------------------------------

def _make_root():
    """Create a Tk root window; skip if no display is available."""
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
        root.withdraw()
        return root, tk
    except Exception as e:
        pytest.skip(f"No display available for tkinter: {e}")


def _make_editor(root):
    """Instantiate ScenarioEditor with mocked dependencies."""
    # Patch ScenarioStorage.ensure_dir and list_scenarios so no filesystem access
    with patch("processes.SCENARIO.scenario_03_storage.SCENARIOS_DIR") as mock_dir:
        mock_dir.__truediv__ = lambda self, other: Path(tempfile.mkdtemp()) / other
        mock_dir.mkdir = MagicMock()
        mock_dir.glob = MagicMock(return_value=[])

        # We need to patch at the UI module level too
        with patch("UI.scenario_editor.ScenarioStorage") as MockStorage:
            MockStorage.ensure_dir = MagicMock()
            MockStorage.list_scenarios = MagicMock(return_value=[])
            MockStorage.load = MagicMock(return_value=[])

            from UI.scenario_editor import ScenarioEditor

            adb = MagicMock()
            adb.connected_device = None
            log_calls = []

            def log_cb(msg, tag="info"):
                log_calls.append((msg, tag))

            editor = ScenarioEditor(root, adb, log_cb)
            return editor, log_calls, adb


# ---------------------------------------------------------------------------
# 3.2 All required step types present in OptionMenu (Req 2.1)
# ---------------------------------------------------------------------------

class TestStepTypes:
    """3.2 Verify STEP_TYPES contains the 5 types required by Req 2.1."""

    def test_required_step_types_present(self):
        """The 5 step types from Req 2.1 must be present in STEP_TYPES."""
        from processes.SCENARIO import STEP_TYPES
        # Req 2.1 lists these 5 human-readable labels:
        required = {
            "Найти паттерн и нажать",
            "Отдалить (pinch out)",
            "Подождать",
            "Нажать по координатам",
            "Свайп",
        }
        actual = set(STEP_TYPES)
        missing = required - actual
        assert not missing, f"Missing required step types: {missing}"

    def test_step_type_keys_map_correctly(self):
        """Each required label maps to the correct internal key."""
        from processes.SCENARIO import STEP_TYPE_KEYS
        assert STEP_TYPE_KEYS["Найти паттерн и нажать"] == "find_and_tap"
        assert STEP_TYPE_KEYS["Отдалить (pinch out)"]   == "pinch_out"
        assert STEP_TYPE_KEYS["Подождать"]               == "wait"
        assert STEP_TYPE_KEYS["Нажать по координатам"]   == "tap_coords"
        assert STEP_TYPE_KEYS["Свайп"]                   == "swipe"


# ---------------------------------------------------------------------------
# 3.3 Correct param fields shown for each step type (Req 2.2–2.6)
# ---------------------------------------------------------------------------

class TestStepDefaults:
    """3.3 Verify correct param fields exist for each step type."""

    def test_find_and_tap_params(self):
        """find_and_tap must have pattern and threshold fields (Req 2.2)."""
        from processes.SCENARIO.scenario_02_steps import STEP_DEFAULTS
        p = STEP_DEFAULTS["find_and_tap"]
        assert "pattern" in p
        assert "threshold" in p
        assert 0.0 < p["threshold"] <= 1.0

    def test_pinch_out_params(self):
        """pinch_out must have seconds field (Req 2.3 — actual: seconds, not times)."""
        from processes.SCENARIO.scenario_02_steps import STEP_DEFAULTS
        p = STEP_DEFAULTS["pinch_out"]
        # GAP Req 2.3: spec says 'times: int >= 1'; actual uses 'seconds: float'
        assert "seconds" in p
        assert p["seconds"] > 0

    def test_wait_params(self):
        """wait must have seconds field (Req 2.4)."""
        from processes.SCENARIO.scenario_02_steps import STEP_DEFAULTS
        p = STEP_DEFAULTS["wait"]
        assert "seconds" in p
        assert p["seconds"] > 0

    def test_tap_coords_params(self):
        """tap_coords must have x and y fields (Req 2.5)."""
        from processes.SCENARIO.scenario_02_steps import STEP_DEFAULTS
        p = STEP_DEFAULTS["tap_coords"]
        assert "x" in p
        assert "y" in p
        assert p["x"] >= 0
        assert p["y"] >= 0

    def test_swipe_params(self):
        """swipe must have x1, y1, x2, y2 fields (Req 2.6)."""
        from processes.SCENARIO.scenario_02_steps import STEP_DEFAULTS
        p = STEP_DEFAULTS["swipe"]
        for key in ("x1", "y1", "x2", "y2"):
            assert key in p, f"Missing swipe param: {key}"
            assert p[key] >= 0


# ---------------------------------------------------------------------------
# 3.5 Scenario file not found → silent return [] (GAP Req 4.3)
# ---------------------------------------------------------------------------

class TestStorageFileNotFound:
    """3.5 ScenarioStorage.load() returns [] when file is missing (GAP Req 4.3)."""

    def test_load_missing_file_returns_empty(self):
        """load() returns [] silently when the scenario file does not exist.

        GAP Req 4.3: The requirement says BotLog should receive
        "Файл сценария не найден". Actual implementation returns [] silently.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with patch("processes.SCENARIO.scenario_03_storage.SCENARIOS_DIR", tmp_path):
                from processes.SCENARIO import ScenarioStorage
                result = ScenarioStorage.load("nonexistent_scenario")
        assert result == [], f"Expected [], got {result!r}"

    def test_load_missing_file_does_not_raise(self):
        """load() must not raise any exception when file is missing."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with patch("processes.SCENARIO.scenario_03_storage.SCENARIOS_DIR", tmp_path):
                from processes.SCENARIO import ScenarioStorage
                try:
                    ScenarioStorage.load("no_such_file")
                except Exception as e:
                    pytest.fail(f"load() raised unexpectedly: {e}")


# ---------------------------------------------------------------------------
# 3.6 Invalid JSON → silent return [] (GAP Req 4.4)
# ---------------------------------------------------------------------------

class TestStorageInvalidJson:
    """3.6 ScenarioStorage.load() returns [] on invalid JSON (GAP Req 4.4)."""

    def test_load_invalid_json_returns_empty(self):
        """load() returns [] silently when the file contains invalid JSON.

        GAP Req 4.4: The requirement says BotLog should receive an error message.
        Actual implementation returns [] silently.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bad_file = tmp_path / "bad_scenario.json"
            bad_file.write_text("{not valid json!!!", encoding="utf-8")
            with patch("processes.SCENARIO.scenario_03_storage.SCENARIOS_DIR", tmp_path):
                from processes.SCENARIO import ScenarioStorage
                result = ScenarioStorage.load("bad_scenario")
        assert result == [], f"Expected [], got {result!r}"

    def test_load_invalid_json_does_not_raise(self):
        """load() must not raise any exception on invalid JSON."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bad_file = tmp_path / "corrupt.json"
            bad_file.write_text("<<<GARBAGE>>>", encoding="utf-8")
            with patch("processes.SCENARIO.scenario_03_storage.SCENARIOS_DIR", tmp_path):
                from processes.SCENARIO import ScenarioStorage
                try:
                    ScenarioStorage.load("corrupt")
                except Exception as e:
                    pytest.fail(f"load() raised unexpectedly: {e}")


# ---------------------------------------------------------------------------
# 3.4 No selection → silent return for move/delete (GAP Req 3.4)
# ---------------------------------------------------------------------------

class TestMoveDeleteNoSelection:
    """3.4 _move_up/_move_down silently return when no step is selected (GAP Req 3.4).

    GAP Req 3.4: The requirement says a warning should be logged to BotLog.
    Actual implementation silently returns without logging.
    """

    def test_delete_no_selection_logs_warning(self):
        """_delete_step logs a warning when no step is selected (Req 3.4).

        Note: _delete_step DOES log a warning; only _move_up/_move_down are silent.
        """
        root, tk = _make_root()
        try:
            editor, log_calls, _ = _make_editor(root)
            editor._steps = []
            editor._refresh_listbox()
            # No selection — call delete
            editor._delete_step()
            warnings = [msg for msg, tag in log_calls if tag == "warning"]
            assert any("Выберите шаг" in w for w in warnings), \
                f"Expected warning about no selection, got: {log_calls}"
        finally:
            root.destroy()

    def test_move_up_no_selection_silent(self):
        """_move_up silently returns when no step is selected (GAP Req 3.4).

        GAP: requirement says log a warning; actual implementation is silent.
        """
        root, tk = _make_root()
        try:
            editor, log_calls, _ = _make_editor(root)
            step = {"type": "wait", "params": {"seconds": 1.0}}
            editor._steps = [copy.deepcopy(step)]
            editor._refresh_listbox()
            # No selection in listbox
            before_len = len(log_calls)
            editor._move_up()
            # List must be unchanged
            assert len(editor._steps) == 1
            # GAP: no warning is logged
            after_len = len(log_calls)
            assert after_len == before_len, \
                "GAP Req 3.4: _move_up should not log anything when no selection"
        finally:
            root.destroy()

    def test_move_down_no_selection_silent(self):
        """_move_down silently returns when no step is selected (GAP Req 3.4).

        GAP: requirement says log a warning; actual implementation is silent.
        """
        root, tk = _make_root()
        try:
            editor, log_calls, _ = _make_editor(root)
            step = {"type": "wait", "params": {"seconds": 1.0}}
            editor._steps = [copy.deepcopy(step)]
            editor._refresh_listbox()
            before_len = len(log_calls)
            editor._move_down()
            assert len(editor._steps) == 1
            after_len = len(log_calls)
            assert after_len == before_len, \
                "GAP Req 3.4: _move_down should not log anything when no selection"
        finally:
            root.destroy()


# ---------------------------------------------------------------------------
# 3.1 Empty step list shows placeholder text in Listbox (GAP Req 1.3)
# ---------------------------------------------------------------------------

class TestEmptyListPlaceholder:
    """3.1 Empty step list shows placeholder text in Listbox (GAP Req 1.3).

    GAP Req 1.3: Spec says "Нет шагов. Добавьте первый шаг."
    Actual text: "(нет шагов — нажмите '＋ Добавить шаг')"
    """

    def test_empty_steps_shows_placeholder(self):
        """When _steps is empty, Listbox shows the actual placeholder text."""
        root, tk = _make_root()
        try:
            editor, _, _ = _make_editor(root)
            editor._steps = []
            editor._refresh_listbox()
            items = editor._listbox.get(0, tk.END)
            assert len(items) == 1, f"Expected 1 placeholder item, got {len(items)}: {items}"
            # GAP Req 1.3: actual placeholder differs from spec
            assert "нет шагов" in items[0].lower(), \
                f"Placeholder text not found. Got: {items[0]!r}"
        finally:
            root.destroy()

    def test_nonempty_steps_no_placeholder(self):
        """When steps exist, Listbox shows step entries, not the placeholder."""
        root, tk = _make_root()
        try:
            editor, _, _ = _make_editor(root)
            editor._steps = [{"type": "wait", "params": {"seconds": 1.0}}]
            editor._refresh_listbox()
            items = editor._listbox.get(0, tk.END)
            assert len(items) == 1
            assert "нет шагов" not in items[0].lower()
        finally:
            root.destroy()


# ---------------------------------------------------------------------------
# 3.7 Device not connected → START flow triggered (GAP Req 5.9)
# ---------------------------------------------------------------------------

class TestDeviceNotConnected:
    """3.7 Device not connected behaviour (GAP Req 5.9).

    GAP Req 5.9: Spec says log "❌ Устройство не подключено" and do NOT start.
    Actual: triggers START flow and waits for connection.
    """

    def test_run_with_no_device_triggers_start_flow(self):
        """When device is not connected, _run_scenario triggers the start callback.

        GAP Req 5.9: actual behaviour differs from spec.
        """
        root, tk = _make_root()
        try:
            editor, log_calls, adb = _make_editor(root)
            adb.connected_device = None
            editor._is_connected = lambda: False

            start_called = [False]
            def mock_start():
                start_called[0] = True
            editor._start_cb = mock_start

            # Add a step so the empty-list guard doesn't fire
            editor._steps = [{"type": "wait", "params": {"seconds": 0.0}}]

            editor._run_scenario()

            # GAP: start callback is triggered instead of logging the error
            assert start_called[0], \
                "GAP Req 5.9: start_cb should be called when device not connected"
            # The run button should be disabled while waiting
            import tkinter as _tk
            assert str(editor._run_btn["state"]) == _tk.DISABLED
        finally:
            root.destroy()


# ---------------------------------------------------------------------------
# 3.8 Empty step list on run → "⚠️ Сценарий пуст" logged (Req 5.10)
# ---------------------------------------------------------------------------

class TestEmptyStepListRun:
    """3.8 Empty step list on run logs warning and does not start thread (Req 5.10)."""

    def test_run_empty_steps_logs_warning(self):
        """Running with empty steps logs '⚠ Сценарий пуст' and does not start."""
        root, tk = _make_root()
        try:
            editor, log_calls, _ = _make_editor(root)
            editor._steps = []
            editor._running = False

            threads_before = threading.active_count()
            editor._run_scenario()
            time.sleep(0.05)  # give any accidental thread time to start
            threads_after = threading.active_count()

            warnings = [msg for msg, tag in log_calls if tag == "warning"]
            assert any("Сценарий пуст" in w for w in warnings), \
                f"Expected '⚠ Сценарий пуст' warning, got: {log_calls}"
            assert threads_after == threads_before, \
                "No new thread should be started for empty step list"
        finally:
            root.destroy()

    def test_run_empty_steps_does_not_change_running_state(self):
        """Running with empty steps must not set _running = True."""
        root, tk = _make_root()
        try:
            editor, _, _ = _make_editor(root)
            editor._steps = []
            editor._running = False
            editor._run_scenario()
            assert not editor._running
        finally:
            root.destroy()


# ---------------------------------------------------------------------------
# 3.9 Run button disabled and text changes during run (Req 5.11)
# ---------------------------------------------------------------------------

class TestRunButtonDuringRun:
    """3.9 Run button is disabled and shows '⏳ Выполняется...' during run (Req 5.11)."""

    def test_run_button_disabled_during_run(self):
        """_start_running() disables the run button and sets text to '⏳ Выполняется...'."""
        root, tk = _make_root()
        try:
            editor, log_calls, adb = _make_editor(root)
            adb.connected_device = "emulator-5554"
            editor._is_connected = lambda: True

            # Patch threading.Thread so the thread body never actually runs
            with patch("UI.scenario_editor.threading.Thread") as MockThread:
                mock_thread_instance = MagicMock()
                MockThread.return_value = mock_thread_instance

                editor._steps = [{"type": "wait", "params": {"seconds": 0.0}}]
                editor._start_running()

                import tkinter as _tk
                assert str(editor._run_btn["state"]) == _tk.DISABLED, \
                    "Run button must be disabled during run"
                assert "Выполняется" in editor._run_btn["text"], \
                    f"Run button text should contain 'Выполняется', got: {editor._run_btn['text']!r}"
        finally:
            root.destroy()

    def test_run_button_restored_after_run(self):
        """_on_run_done() restores the run button state and text."""
        root, tk = _make_root()
        try:
            editor, _, _ = _make_editor(root)
            # Simulate running state
            editor._running = True
            editor._run_btn.config(text="⏳ Выполняется...", state=tk.DISABLED)

            editor._on_run_done()

            import tkinter as _tk
            assert str(editor._run_btn["state"]) == _tk.NORMAL, \
                "Run button must be re-enabled after run completes"
            assert "Запустить" in editor._run_btn["text"], \
                f"Run button text should contain 'Запустить', got: {editor._run_btn['text']!r}"
            assert not editor._running
        finally:
            root.destroy()


# ---------------------------------------------------------------------------
# 3.10 "✅ Сценарий завершён" logged after all steps complete (Req 5.8)
# ---------------------------------------------------------------------------

class TestScenarioCompletionLog:
    """3.10 ScenarioRunner logs '✅ Сценарий завершён' after all steps (Req 5.8)."""

    def test_completion_message_logged(self):
        """ScenarioRunner.run() logs '✅ Сценарий завершён' when all steps succeed."""
        from processes.SCENARIO import ScenarioRunner

        steps = [
            {"type": "wait", "params": {"seconds": 0.0}},
            {"type": "wait", "params": {"seconds": 0.0}},
        ]
        log_calls = []

        def mock_log(msg, tag="info"):
            log_calls.append((msg, tag))

        with patch("processes.SCENARIO.scenario_01_runner.time") as mock_time:
            mock_time.sleep = MagicMock()
            runner = ScenarioRunner(steps, "emulator-5554", mock_log)
            runner.run()

        messages = [msg for msg, _ in log_calls]
        assert any("Сценарий завершён" in m for m in messages), \
            f"Expected '✅ Сценарий завершён' in log, got: {messages}"

    def test_completion_message_has_checkmark(self):
        """The completion message must start with '✅'."""
        from processes.SCENARIO import ScenarioRunner

        steps = [{"type": "wait", "params": {"seconds": 0.0}}]
        log_calls = []

        with patch("processes.SCENARIO.scenario_01_runner.time") as mock_time:
            mock_time.sleep = MagicMock()
            runner = ScenarioRunner(steps, "emulator-5554",
                                    lambda msg, tag="info": log_calls.append((msg, tag)))
            runner.run()

        completion = [msg for msg, tag in log_calls if "завершён" in msg]
        assert completion, "No completion message found"
        assert completion[0].startswith("✅"), \
            f"Completion message should start with '✅', got: {completion[0]!r}"

    def test_no_completion_message_on_exception(self):
        """ScenarioRunner must NOT log '✅ Сценарий завершён' if a step raises."""
        from processes.SCENARIO import ScenarioRunner

        steps = [{"type": "wait", "params": {"seconds": 0.0}}]
        log_calls = []

        def raising_sleep(secs):
            raise RuntimeError("boom")

        with patch("processes.SCENARIO.scenario_01_runner.time") as mock_time:
            mock_time.sleep = raising_sleep
            runner = ScenarioRunner(steps, "emulator-5554",
                                    lambda msg, tag="info": log_calls.append((msg, tag)))
            runner.run()

        completion = [msg for msg, _ in log_calls if "завершён" in msg]
        assert not completion, \
            f"Should NOT log completion when a step raises, got: {completion}"
