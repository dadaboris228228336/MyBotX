"""
Tests for BOT/bot_02_actions.py and SCENARIO/scenario_04_adb_actions.py
Validates: Requirements 4.3, 5.4, 7.1
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import numpy as np
import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).parent.parent / "CORE"))
from processes.BOT.bot_02_actions import BotActions


def _make_screen(h=100, w=100):
    return np.zeros((h, w, 3), dtype=np.uint8)


# ── Unit tests ────────────────────────────────────────────────────────────────

class TestBotActions:

    def _make_actions(self):
        with patch("processes.BOT.bot_02_actions._load_settings", return_value={}):
            return BotActions("emulator-5554")

    def test_find_and_tap_returns_false_when_capture_fails(self):
        """find_and_tap() returns False when capture() returns None."""
        ba = self._make_actions()
        ba.screenshot.capture = MagicMock(return_value=None)
        result = ba.find_and_tap("ATAKA")
        assert result is False

    def test_find_and_tap_returns_false_when_pattern_not_found(self):
        """find_and_tap() returns False when pattern not found."""
        ba = self._make_actions()
        ba.screenshot.capture = MagicMock(return_value=_make_screen())
        ba.finder.find = MagicMock(return_value=None)
        result = ba.find_and_tap("ATAKA")
        assert result is False

    def test_find_and_tap_returns_true_when_found_and_tapped(self):
        """find_and_tap() returns True when pattern found and tap succeeds."""
        ba = self._make_actions()
        ba.screenshot.capture = MagicMock(return_value=_make_screen())
        ba.finder.find = MagicMock(return_value=(50, 60))
        ba.tap.tap_and_wait = MagicMock(return_value=True)
        result = ba.find_and_tap("ATAKA")
        assert result is True
        ba.tap.tap_and_wait.assert_called_once_with(50, 60, 1.0)

    def test_collect_resources_returns_false_when_capture_fails(self):
        """collect_resources() returns False when capture() returns None."""
        ba = self._make_actions()
        ba.screenshot.capture = MagicMock(return_value=None)
        result = ba.collect_resources()
        assert result is False

    def test_start_attack_delegates_to_find_and_tap(self):
        """start_attack() calls find_and_tap with btn_attack."""
        ba = self._make_actions()
        ba.find_and_tap = MagicMock(return_value=True)
        result = ba.start_attack()
        assert result is True
        ba.find_and_tap.assert_called_once_with("btn_attack", wait_after=2.0)


class TestScenarioAdbActions:

    def test_do_find_and_tap_returns_false_for_missing_pattern(self, tmp_path):
        """do_find_and_tap() returns False when pattern file doesn't exist."""
        from processes.SCENARIO.scenario_04_adb_actions import do_find_and_tap
        # Patch PATTERNS_DIR to tmp_path (no pattern files there)
        with patch("processes.SCENARIO.scenario_04_adb_actions.PATTERNS_DIR", tmp_path):
            result = do_find_and_tap("emulator-5554", "nonexistent", 0.8, 1, 0.5)
        assert result is False


# ── Property test P6 ──────────────────────────────────────────────────────────

# Feature: processes-restructure, Property 6: BotActions.collect_resources taps every found point
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    points=st.lists(
        st.tuples(st.integers(0, 1280), st.integers(0, 720)),
        min_size=0,
        max_size=15,
    )
)
def test_collect_resources_taps_every_found_point(points):
    """
    Property 6: collect_resources() calls tap_and_wait exactly N times
    per pattern where find_all returns N points.
    Validates: Requirements 4.5
    """
    with patch("processes.BOT.bot_02_actions._load_settings", return_value={}):
        ba = BotActions("emulator-5554")

    ba.screenshot.capture = MagicMock(return_value=_make_screen())
    ba.finder.find_all = MagicMock(return_value=points)
    ba.tap.tap_and_wait = MagicMock(return_value=True)

    ba.collect_resources()

    # 3 patterns × len(points) taps expected
    expected_calls = len(points) * 3
    assert ba.tap.tap_and_wait.call_count == expected_calls, (
        f"Expected {expected_calls} taps for {len(points)} points × 3 patterns, "
        f"got {ba.tap.tap_and_wait.call_count}"
    )
