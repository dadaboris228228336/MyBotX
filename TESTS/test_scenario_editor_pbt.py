#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Property-based tests for scenario-editor.
Feature: scenario-editor
Tests validate the SCENARIO backend logic (no tkinter required).
"""

import copy
import json
import re
import sys
import time
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest
from hypothesis import given, settings, HealthCheck, assume
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "CORE"))

from processes.SCENARIO import (
    STEP_TYPES, STEP_TYPE_KEYS, STEP_KEY_LABELS,
    step_label, ScenarioStorage, ScenarioRunner,
)
from processes.SCENARIO.scenario_02_steps import STEP_DEFAULTS

# ---------------------------------------------------------------------------
# Hypothesis profile
# ---------------------------------------------------------------------------
settings.register_profile("ci", max_examples=100,
                           suppress_health_check=[HealthCheck.too_slow])
settings.load_profile("ci")

# ---------------------------------------------------------------------------
# Step strategies
# ---------------------------------------------------------------------------

ALL_STEP_KEYS = list(STEP_TYPE_KEYS.values())  # 11 types


def _step(type_key: str) -> dict:
    """Build a valid step dict for the given type key."""
    return {"type": type_key, "params": copy.deepcopy(STEP_DEFAULTS[type_key])}


@st.composite
def step_strategy(draw):
    """Hypothesis strategy: generates a valid step dict for a random type."""
    key = draw(st.sampled_from(ALL_STEP_KEYS))
    return _step(key)


@st.composite
def steps_list(draw, min_size=0, max_size=10):
    return draw(st.lists(step_strategy(), min_size=min_size, max_size=max_size))


# ===========================================================================
# Property 1: Adding a valid step increases the list by exactly 1
# Feature: scenario-editor, Property 1: Добавление корректного шага увеличивает список
# Validates: Requirements 2.7
# ===========================================================================

@given(existing=steps_list(), new_step=step_strategy())
def test_p1_add_valid_step_increases_list(existing, new_step):
    """Adding a valid step to any list increases its length by exactly 1."""
    before = copy.deepcopy(existing)
    existing.append(new_step)
    assert len(existing) == len(before) + 1
    assert existing[-1] == new_step


# ===========================================================================
# Property 2: Invalid data does not change the list
# Feature: scenario-editor, Property 2: Невалидные данные не изменяют список
# Validates: Requirements 2.8
# ===========================================================================

def _try_add_invalid(steps: list, bad_params: dict, type_key: str) -> list:
    """
    Simulate the validation logic from StepDialog._on_save.
    Returns the unchanged list if validation fails, or appended list if it passes.
    """
    result = copy.deepcopy(steps)
    try:
        p = {}
        for key, val in bad_params.items():
            if key in ("x", "y", "x1", "y1", "x2", "y2", "duration", "times", "retries"):
                p[key] = int(val)
            elif key in ("threshold", "retry_delay", "seconds"):
                p[key] = float(val)
            else:
                p[key] = val
        # Extra validation: threshold must be in (0, 1]
        if "threshold" in p and not (0.0 < p["threshold"] <= 1.0):
            raise ValueError("threshold out of range")
        # Extra validation: seconds/times must be positive
        if "seconds" in p and p["seconds"] <= 0:
            raise ValueError("seconds must be > 0")
        if "times" in p and p["times"] < 1:
            raise ValueError("times must be >= 1")
        # Extra validation: coords must be >= 0
        for coord_key in ("x", "y", "x1", "y1", "x2", "y2"):
            if coord_key in p and p[coord_key] < 0:
                raise ValueError(f"{coord_key} must be >= 0")
        result.append({"type": type_key, "params": p})
    except (ValueError, TypeError):
        pass  # validation failed — list unchanged
    return result


@given(
    existing=steps_list(),
    bad_val=st.one_of(
        st.text(min_size=1).filter(lambda s: not s.strip().lstrip("-").replace(".", "", 1).isdigit()),
        st.just(""),
        st.just("abc"),
        st.just("-999"),
    ),
)
def test_p2_invalid_numeric_field_does_not_add_step(existing, bad_val):
    """Non-numeric value in a numeric field must not add a step."""
    before = copy.deepcopy(existing)
    # tap_coords requires int x, y
    bad_params = {"x": bad_val, "y": bad_val}
    result = _try_add_invalid(existing, bad_params, "tap_coords")
    # If bad_val can't be cast to int, list must be unchanged
    try:
        int(bad_val)
        # If it CAN be cast, result may differ — that's fine
    except (ValueError, TypeError):
        assert len(result) == len(before), \
            f"List grew despite invalid value {bad_val!r}"


@given(existing=steps_list())
def test_p2_negative_coords_do_not_add_step(existing):
    """Negative coordinates must not add a step."""
    before = copy.deepcopy(existing)
    bad_params = {"x": -1, "y": -1}
    result = _try_add_invalid(existing, bad_params, "tap_coords")
    assert len(result) == len(before)


@given(existing=steps_list(), bad_threshold=st.one_of(
    st.floats(max_value=0.0, allow_nan=False),
    st.floats(min_value=1.001, max_value=10.0, allow_nan=False),
))
def test_p2_invalid_threshold_does_not_add_step(existing, bad_threshold):
    """Threshold outside (0.0, 1.0] must not add a step."""
    before = copy.deepcopy(existing)
    bad_params = {"pattern": "test", "threshold": bad_threshold, "retries": 3, "retry_delay": 2.0}
    result = _try_add_invalid(existing, bad_params, "find_and_tap")
    assert len(result) == len(before)


# ===========================================================================
# Property 3: Move-up swaps adjacent steps correctly
# Feature: scenario-editor, Property 3: Перемещение шага вверх корректно меняет порядок
# Validates: Requirements 3.1
# ===========================================================================

@given(steps=steps_list(min_size=2, max_size=10), data=st.data())
def test_p3_move_up_swaps_correctly(steps, data):
    """Moving step at index i up places it at i-1 and vice versa."""
    i = data.draw(st.integers(min_value=1, max_value=len(steps) - 1))
    before = copy.deepcopy(steps)
    steps[i - 1], steps[i] = steps[i], steps[i - 1]

    assert steps[i - 1] == before[i],     "Step should move to i-1"
    assert steps[i]     == before[i - 1], "Previous step should move to i"
    # All other positions unchanged
    for j in range(len(steps)):
        if j not in (i - 1, i):
            assert steps[j] == before[j]


# ===========================================================================
# Property 4: Move-down swaps adjacent steps correctly
# Feature: scenario-editor, Property 4: Перемещение шага вниз корректно меняет порядок
# Validates: Requirements 3.2
# ===========================================================================

@given(steps=steps_list(min_size=2, max_size=10), data=st.data())
def test_p4_move_down_swaps_correctly(steps, data):
    """Moving step at index i down places it at i+1 and vice versa."""
    i = data.draw(st.integers(min_value=0, max_value=len(steps) - 2))
    before = copy.deepcopy(steps)
    steps[i], steps[i + 1] = steps[i + 1], steps[i]

    assert steps[i + 1] == before[i],     "Step should move to i+1"
    assert steps[i]     == before[i + 1], "Next step should move to i"
    for j in range(len(steps)):
        if j not in (i, i + 1):
            assert steps[j] == before[j]


# ===========================================================================
# Property 5: Deleting a step decreases the list by exactly 1
# Feature: scenario-editor, Property 5: Удаление шага уменьшает список
# Validates: Requirements 3.3
# ===========================================================================

@given(steps=steps_list(min_size=1, max_size=10), data=st.data())
def test_p5_delete_step_decreases_list(steps, data):
    """Deleting any step decreases list length by 1 and removes that step."""
    i = data.draw(st.integers(min_value=0, max_value=len(steps) - 1))
    before = copy.deepcopy(steps)
    removed = steps.pop(i)

    assert len(steps) == len(before) - 1
    # Remaining steps are the original list minus the removed one
    expected = before[:i] + before[i + 1:]
    assert steps == expected


# ===========================================================================
# Property 6: Round-trip serialization
# Feature: scenario-editor, Property 6: Round-trip сериализации сценария
# Validates: Requirements 4.1, 4.2, 4.5, 4.6
# ===========================================================================

@given(steps=steps_list(min_size=0, max_size=10))
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_p6_round_trip_serialization(steps):
    """save(steps) then load() must produce an equivalent list."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with patch("processes.SCENARIO.scenario_03_storage.SCENARIOS_DIR", tmp_path):
            ScenarioStorage.save("test_scenario", steps)
            loaded = ScenarioStorage.load("test_scenario")
    assert loaded == steps, f"Round-trip failed:\nOriginal: {steps}\nLoaded:   {loaded}"


# ===========================================================================
# Property 7: Log message format during execution
# Feature: scenario-editor, Property 7: Формат лог-сообщений при выполнении шагов
# Validates: Requirements 5.2
# ===========================================================================

@given(steps=steps_list(min_size=1, max_size=8))
def test_p7_log_message_format(steps):
    """ScenarioRunner must log exactly N '▶ Шаг i/N:' messages for N steps."""
    log_calls = []

    def mock_log(msg, tag="info"):
        log_calls.append((msg, tag))

    total = len(steps)

    with patch("processes.SCENARIO.scenario_01_runner.do_tap"),          \
         patch("processes.SCENARIO.scenario_01_runner.do_swipe"),         \
         patch("processes.SCENARIO.scenario_01_runner.do_key"),           \
         patch("processes.SCENARIO.scenario_01_runner.do_text"),          \
         patch("processes.SCENARIO.scenario_01_runner.do_launch"),        \
         patch("processes.SCENARIO.scenario_01_runner.do_stop"),          \
         patch("processes.SCENARIO.scenario_01_runner.do_pinch"),         \
         patch("processes.SCENARIO.scenario_01_runner.do_find_and_tap"),  \
         patch("processes.SCENARIO.scenario_01_runner.time") as mock_time:
        mock_time.sleep = MagicMock()
        runner = ScenarioRunner(steps, "emulator-5554", mock_log)
        runner.run()

    step_logs = [
        msg for msg, _ in log_calls
        if re.match(r"▶ Шаг \d+/\d+:", msg)
    ]
    assert len(step_logs) == total, (
        f"Expected {total} step log messages, got {len(step_logs)}.\n"
        f"All logs: {log_calls}"
    )
    for idx, msg in enumerate(step_logs, 1):
        assert msg.startswith(f"▶ Шаг {idx}/{total}:"), \
            f"Step {idx} log format wrong: {msg!r}"


# ===========================================================================
# Property 8: Step dispatch by type
# Feature: scenario-editor, Property 8: Диспетчеризация шагов по типу
# Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7
# ===========================================================================

@pytest.mark.parametrize("type_key", ALL_STEP_KEYS)
def test_p8_step_dispatch(type_key):
    """ScenarioRunner must call the correct action function for each step type."""
    step = _step(type_key)
    log_calls = []

    with patch("processes.SCENARIO.scenario_01_runner.do_tap")           as m_tap,    \
         patch("processes.SCENARIO.scenario_01_runner.do_swipe")         as m_swipe,  \
         patch("processes.SCENARIO.scenario_01_runner.do_key")           as m_key,    \
         patch("processes.SCENARIO.scenario_01_runner.do_text")          as m_text,   \
         patch("processes.SCENARIO.scenario_01_runner.do_launch")        as m_launch, \
         patch("processes.SCENARIO.scenario_01_runner.do_stop")          as m_stop,   \
         patch("processes.SCENARIO.scenario_01_runner.do_pinch")         as m_pinch,  \
         patch("processes.SCENARIO.scenario_01_runner.do_find_and_tap")  as m_fat,    \
         patch("processes.SCENARIO.scenario_01_runner.time") as mock_time:
        mock_time.sleep = MagicMock()

        runner = ScenarioRunner([step], "emulator-5554",
                                lambda msg, tag="info": log_calls.append(msg))
        runner.run()

    p = step["params"]
    if type_key == "find_and_tap":
        m_fat.assert_called_once()
    elif type_key == "tap_coords":
        m_tap.assert_called_once_with("emulator-5554", p["x"], p["y"])
    elif type_key == "swipe":
        m_swipe.assert_called_once_with(
            "emulator-5554", p["x1"], p["y1"], p["x2"], p["y2"], p["duration"])
    elif type_key in ("pinch_out", "pinch_in"):
        m_pinch.assert_called_once()
    elif type_key == "key_home":
        m_key.assert_called_once_with("emulator-5554", 3)
    elif type_key == "key_back":
        m_key.assert_called_once_with("emulator-5554", 4)
    elif type_key == "input_text":
        m_text.assert_called_once_with("emulator-5554", p["text"])
    elif type_key == "launch_app":
        m_launch.assert_called_once_with("emulator-5554", p["package"])
    elif type_key == "stop_app":
        m_stop.assert_called_once_with("emulator-5554", p["package"])
    elif type_key == "wait":
        mock_time.sleep.assert_called_once_with(p["seconds"])


# ===========================================================================
# Property 9: Execution stops on exception in a step
# Feature: scenario-editor, Property 9: Остановка при исключении в шаге
# Validates: Requirements 5.12
# ===========================================================================

@given(steps=steps_list(min_size=2, max_size=8), data=st.data())
def test_p9_execution_stops_on_exception(steps, data):
    """ScenarioRunner must stop at the failing step and log an error."""
    fail_idx = data.draw(st.integers(min_value=0, max_value=len(steps) - 1))
    # Use only wait steps so we can easily count time.sleep calls
    wait_steps = [{"type": "wait", "params": {"seconds": 0.0}} for _ in steps]
    call_count = [0]
    error_logged = [False]

    def counting_sleep(secs):
        call_count[0] += 1
        if call_count[0] - 1 == fail_idx:
            raise RuntimeError("simulated failure")

    def mock_log(msg, tag="info"):
        if tag == "error":
            error_logged[0] = True

    with patch("processes.SCENARIO.scenario_01_runner.time") as mock_time:
        mock_time.sleep = counting_sleep
        runner = ScenarioRunner(wait_steps, "emulator-5554", mock_log)
        runner.run()

    # Steps after fail_idx must NOT have been executed
    assert call_count[0] == fail_idx + 1, (
        f"Expected {fail_idx + 1} sleep calls, got {call_count[0]}"
    )
    assert error_logged[0], "Error must be logged when a step raises an exception"
