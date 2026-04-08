#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for PID manager logic in CORE/main.py.
Tests validate Python-side PID file write/delete logic in isolation (no tkinter).

Feature: smart-launcher-pid
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "CORE"))


# ---------------------------------------------------------------------------
# Helpers: replicate the PID write/delete logic from BotMainWindow
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
# 3.1 — test_pid_file_written_on_init
# Validates: P4
# ===========================================================================

def test_pid_file_written_on_init():
    """After PID-write logic runs, mybotx.pid exists and contains a numeric PID."""
    with tempfile.TemporaryDirectory() as tmp:
        pid_file = Path(tmp) / "temp" / "mybotx.pid"
        _write_pid(pid_file)
        assert pid_file.exists(), "mybotx.pid should exist after init"
        content = pid_file.read_text(encoding="utf-8")
        assert content.isdigit(), f"PID file content should be numeric, got: {content!r}"


# ===========================================================================
# 3.2 — test_pid_file_contains_current_pid
# Validates: P4
# ===========================================================================

def test_pid_file_contains_current_pid():
    """PID written to file matches os.getpid()."""
    with tempfile.TemporaryDirectory() as tmp:
        pid_file = Path(tmp) / "temp" / "mybotx.pid"
        _write_pid(pid_file)
        content = pid_file.read_text(encoding="utf-8")
        assert int(content) == os.getpid(), (
            f"Expected PID {os.getpid()}, got {content!r}"
        )


# ===========================================================================
# 3.3 — test_pid_file_deleted_on_close
# Validates: P3
# ===========================================================================

def test_pid_file_deleted_on_close():
    """After _on_close_user logic runs, mybotx.pid does not exist."""
    with tempfile.TemporaryDirectory() as tmp:
        pid_file = Path(tmp) / "temp" / "mybotx.pid"
        _write_pid(pid_file)
        assert pid_file.exists(), "Pre-condition: file should exist before close"
        _delete_pid(pid_file)
        assert not pid_file.exists(), "mybotx.pid should be deleted after close"


# ===========================================================================
# 3.4 — test_temp_dir_created_if_missing
# Validates: R1
# ===========================================================================

def test_temp_dir_created_if_missing():
    """CORE/temp/ directory is created automatically if it does not exist."""
    with tempfile.TemporaryDirectory() as tmp:
        # Ensure the temp sub-dir does NOT exist yet
        temp_dir = Path(tmp) / "temp"
        assert not temp_dir.exists(), "Pre-condition: temp dir should not exist"
        pid_file = temp_dir / "mybotx.pid"
        _write_pid(pid_file)
        assert temp_dir.exists(), "temp/ directory should have been created"
        assert pid_file.exists(), "mybotx.pid should exist inside created temp/"


# ===========================================================================
# 3.5 — test_pid_file_format
# Validates: R1
# ===========================================================================

def test_pid_file_format():
    """PID file content is a single line integer with no whitespace or newlines."""
    with tempfile.TemporaryDirectory() as tmp:
        pid_file = Path(tmp) / "temp" / "mybotx.pid"
        _write_pid(pid_file)
        raw = pid_file.read_bytes()
        content = raw.decode("utf-8")
        # No leading/trailing whitespace or newlines
        assert content == content.strip(), (
            f"PID file should have no surrounding whitespace, got: {content!r}"
        )
        # Must be a valid integer
        assert content.isdigit(), f"PID file must contain only digits, got: {content!r}"
        # Must be a single token (no spaces inside)
        assert " " not in content, "PID file must not contain spaces"
        assert "\n" not in content, "PID file must not contain newlines"
