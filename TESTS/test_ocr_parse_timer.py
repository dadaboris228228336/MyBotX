"""
Tests for OCR/ocr_03_parse_timer.py
Validates: Requirements 3.9, 3.10, 3.11, 3.12
"""

import sys
from pathlib import Path

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).parent.parent / "CORE"))
from processes.OCR import parse_timer


# ── Unit tests ────────────────────────────────────────────────────────────────

class TestParseTimer:

    def test_hhmmss_format(self):
        assert parse_timer("01:30:00") == 5400

    def test_mmss_format(self):
        assert parse_timer("05:30") == 330

    def test_natural_hm(self):
        assert parse_timer("1h 30m") == 5400

    def test_natural_hms(self):
        assert parse_timer("2h 15m 3s") == 8103

    def test_garbage_returns_none(self):
        assert parse_timer("garbage") is None

    def test_empty_returns_none(self):
        assert parse_timer("") is None

    def test_seconds_only(self):
        assert parse_timer("45s") == 45

    def test_minutes_only(self):
        assert parse_timer("10m") == 600

    def test_hours_only(self):
        assert parse_timer("2h") == 7200

    def test_zero_time(self):
        assert parse_timer("0h 0m 0s") == 0

    def test_hhmmss_zero(self):
        assert parse_timer("00:00:00") == 0

    def test_ocr_o_substitution(self):
        """O (letter) should be treated as 0 in timer strings."""
        # "O1:3O" → "01:30" → 90 seconds
        result = parse_timer("O1:3O")
        assert result == 90


# ── Property test P3 ──────────────────────────────────────────────────────────

# Feature: processes-restructure, Property 3: parse_timer round-trip
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    h=st.integers(min_value=0, max_value=23),
    m=st.integers(min_value=0, max_value=59),
    s=st.integers(min_value=0, max_value=59),
)
def test_parse_timer_round_trip_hhmmss(h, m, s):
    """
    Property 3a: parse_timer("HH:MM:SS") == h*3600 + m*60 + s.
    Validates: Requirements 3.10
    """
    text = f"{h:02d}:{m:02d}:{s:02d}"
    expected = h * 3600 + m * 60 + s
    result = parse_timer(text)
    assert result == expected, f"parse_timer({text!r}) = {result}, expected {expected}"


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    h=st.integers(min_value=0, max_value=23),
    m=st.integers(min_value=0, max_value=59),
    s=st.integers(min_value=0, max_value=59),
)
def test_parse_timer_round_trip_natural(h, m, s):
    """
    Property 3b: parse_timer("Xh Ym Zs") == h*3600 + m*60 + s.
    Validates: Requirements 3.11
    """
    parts = []
    if h > 0:
        parts.append(f"{h}h")
    if m > 0:
        parts.append(f"{m}m")
    if s > 0:
        parts.append(f"{s}s")
    if not parts:
        parts = ["0s"]
    text = " ".join(parts)
    expected = h * 3600 + m * 60 + s
    result = parse_timer(text)
    assert result == expected, f"parse_timer({text!r}) = {result}, expected {expected}"
