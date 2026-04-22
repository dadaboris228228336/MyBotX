#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Property-based tests for PID manager logic.
Feature: smart-launcher-pid

Tests simulate the bat-file PID logic in Python and verify invariants
using hypothesis.

Validates: Requirements R1, R2, R3, R5
"""

import os
import sys
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

# ---------------------------------------------------------------------------
# Hypothesis profile
# ---------------------------------------------------------------------------
settings.register_profile("ci", max_examples=100,
                           suppress_health_check=[HealthCheck.too_slow])
settings.load_profile("ci")

# ---------------------------------------------------------------------------
# Python mirror of the bat-file PID logic (R3, R4)
#
# The bat logic:
#   if pid_file exists:
#       read OLD_PID
#       if process OLD_PID is alive: taskkill /PID OLD_PID /F
#       del pid_file
# ---------------------------------------------------------------------------

def bat_logic(pid_file: Path, is_process_alive_fn, taskkill_fn) -> None:
    """
    Python mirror of MyBotX_1.0.bat PID-based shutdown block.

    Args:
        pid_file: path to mybotx.pid
        is_process_alive_fn: callable(pid: int) -> bool
        taskkill_fn: callable(pid: int) -> None  (records the kill call)
    """
    if not pid_file.exists():
        return  # no previous instance

    content = pid_file.read_text(encoding="utf-8").strip()
    if not content:
        pid_file.unlink(missing_ok=True)
        return

    try:
        old_pid = int(content)
    except ValueError:
        # Non-numeric content — treat as stale, just delete
        pid_file.unlink(missing_ok=True)
        return

    if is_process_alive_fn(old_pid):
        taskkill_fn(old_pid)

    pid_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Python mirror of PID write/delete logic from BotMainWindow
# ---------------------------------------------------------------------------

def _write_pid(pid_file: Path) -> None:
    """Mirror of BotMainWindow.__init__ PID-write logic (R1)."""
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(os.getpid()), encoding="utf-8")


def _delete_pid(pid_file: Path) -> None:
    """Mirror of BotMainWindow._on_close_user PID-delete logic (R2)."""
    try:
        if pid_file.exists():
            pid_file.unlink()
    except Exception:
        pass


# ===========================================================================
# P1 — Targeted kill by PID
# Validates: Requirements R3, R5
#
# ∀ pid X: if mybotx.pid contains X and process X exists →
#     bat-logic calls taskkill /PID X /F and ONLY that PID
# ===========================================================================

@given(pid=st.integers(min_value=1, max_value=99999))
def test_p1_targeted_kill_calls_only_given_pid(pid):
    """
    **Validates: Requirements R3, R5**

    For any numeric PID X where the process is alive, bat-logic calls
    taskkill exactly once with that PID and no other PID.
    """
    killed_pids = []

    def is_alive(p):
        return p == pid  # only our target is alive

    def taskkill(p):
        killed_pids.append(p)

    with tempfile.TemporaryDirectory() as tmp:
        pid_file = Path(tmp) / "mybotx.pid"
        pid_file.write_text(str(pid), encoding="utf-8")

        bat_logic(pid_file, is_alive, taskkill)

    assert killed_pids == [pid], (
        f"Expected taskkill called once with PID {pid}, got: {killed_pids}"
    )


# ===========================================================================
# P2 — Safe launch: no taskkill when pid file absent or PID non-existent
# Validates: Requirements R3, R2
#
# ∀ state: if mybotx.pid absent or contains non-existent PID →
#     bat-logic calls no taskkill at all
# ===========================================================================

@given(st.just(None))  # parametrize: file absent
def test_p2_no_taskkill_when_pid_file_absent(_):
    """
    **Validates: Requirements R3, R2**

    When mybotx.pid does not exist, bat-logic calls no taskkill.
    """
    killed_pids = []

    def is_alive(p):
        return False

    def taskkill(p):
        killed_pids.append(p)

    with tempfile.TemporaryDirectory() as tmp:
        pid_file = Path(tmp) / "mybotx.pid"
        # File intentionally NOT created
        bat_logic(pid_file, is_alive, taskkill)

    assert killed_pids == [], f"Expected no taskkill, got: {killed_pids}"


@given(pid=st.integers(min_value=1, max_value=99999))
def test_p2_no_taskkill_when_pid_not_alive(pid):
    """
    **Validates: Requirements R3, R2**

    When mybotx.pid contains a PID that is not alive (stale), bat-logic
    calls no taskkill.
    """
    killed_pids = []

    def is_alive(p):
        return False  # process is dead / stale

    def taskkill(p):
        killed_pids.append(p)

    with tempfile.TemporaryDirectory() as tmp:
        pid_file = Path(tmp) / "mybotx.pid"
        pid_file.write_text(str(pid), encoding="utf-8")

        bat_logic(pid_file, is_alive, taskkill)

    assert killed_pids == [], (
        f"Expected no taskkill for dead PID {pid}, got: {killed_pids}"
    )


@given(garbage=st.text(min_size=1).filter(
    lambda s: not s.strip().lstrip("-").isdigit() and s.strip() != ""
))
def test_p2_no_taskkill_for_non_numeric_pid_content(garbage):
    """
    **Validates: Requirements R3, R2**

    When mybotx.pid contains non-numeric garbage, bat-logic calls no taskkill.
    """
    killed_pids = []

    def is_alive(p):
        return True  # would kill if called

    def taskkill(p):
        killed_pids.append(p)

    with tempfile.TemporaryDirectory() as tmp:
        pid_file = Path(tmp) / "mybotx.pid"
        pid_file.write_text(garbage, encoding="utf-8")

        bat_logic(pid_file, is_alive, taskkill)

    assert killed_pids == [], (
        f"Expected no taskkill for garbage content {garbage!r}, got: {killed_pids}"
    )


# ===========================================================================
# P3 — File absent after normal close
# Validates: Requirement R2
#
# ∀ PID file content: after _on_close_user() logic, file does not exist
# ===========================================================================

@given(content=st.one_of(
    st.integers(min_value=1, max_value=99999).map(str),
    st.text(min_size=0, max_size=20),
))
def test_p3_file_absent_after_close(content):
    """
    **Validates: Requirements R2**

    For any PID file content, after _on_close_user logic runs,
    mybotx.pid does not exist.
    """
    with tempfile.TemporaryDirectory() as tmp:
        pid_file = Path(tmp) / "temp" / "mybotx.pid"
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(content, encoding="utf-8")

        assert pid_file.exists(), "Pre-condition: file should exist before close"
        _delete_pid(pid_file)
        assert not pid_file.exists(), (
            f"mybotx.pid should not exist after close (content was: {content!r})"
        )


# ===========================================================================
# P4 — File created and valid after GUI start
# Validates: Requirement R1
#
# ∀ GUI start: after __init__ PID logic, mybotx.pid exists and contains
#     the current process PID as an integer
# ===========================================================================

@given(st.just(None))  # single-shot property, no interesting variation needed
def test_p4_file_created_and_valid_after_init(_):
    """
    **Validates: Requirements R1**

    After the PID-write logic (mirroring BotMainWindow.__init__) runs,
    mybotx.pid exists and contains the current process PID as an integer.
    """
    with tempfile.TemporaryDirectory() as tmp:
        pid_file = Path(tmp) / "temp" / "mybotx.pid"

        _write_pid(pid_file)

        assert pid_file.exists(), "mybotx.pid should exist after init"
        content = pid_file.read_text(encoding="utf-8")
        assert content.isdigit(), f"PID file content should be numeric, got: {content!r}"
        assert int(content) == os.getpid(), (
            f"PID in file ({content}) should match os.getpid() ({os.getpid()})"
        )
        # No surrounding whitespace
        assert content == content.strip(), "PID file should have no surrounding whitespace"
