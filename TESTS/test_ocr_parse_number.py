"""
Tests for OCR/ocr_02_parse_number.py
Validates: Requirements 3.4, 3.5, 3.6, 3.7, 3.8
"""

import sys
from pathlib import Path

import pytest
from hypothesis import given, settings, HealthCheck, assume
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).parent.parent / "CORE"))
from processes.OCR import parse_number


# ── Unit tests ────────────────────────────────────────────────────────────────

class TestParseNumber:

    def test_plain_integer(self):
        assert parse_number("500") == 500

    def test_k_suffix(self):
        assert parse_number("500K") == 500_000

    def test_m_suffix(self):
        assert parse_number("1.5M") == 1_500_000

    def test_b_suffix(self):
        assert parse_number("2B") == 2_000_000_000

    def test_letter_o_as_zero(self):
        assert parse_number("O") == 0

    def test_unrecognised_returns_none(self):
        assert parse_number("abc") is None

    def test_empty_returns_none(self):
        assert parse_number("") is None

    def test_lowercase_k(self):
        assert parse_number("100k") == 100_000

    def test_lowercase_m(self):
        assert parse_number("2m") == 2_000_000

    def test_zero(self):
        assert parse_number("0") == 0

    def test_with_comma_separator(self):
        assert parse_number("1,000") == 1000

    def test_decimal_k(self):
        assert parse_number("2.5K") == 2500


# ── Property test P2 ──────────────────────────────────────────────────────────

SUFFIX_MULTIPLIERS = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}


# Feature: processes-restructure, Property 2: parse_number suffix scaling
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    n=st.floats(min_value=0.1, max_value=999.0, allow_nan=False, allow_infinity=False),
    suffix=st.sampled_from(["K", "M", "B"]),
)
def test_parse_number_suffix_scaling(n, suffix):
    """
    Property 2: parse_number(f"{n}{suffix}") == round(n * multiplier).
    Validates: Requirements 3.5, 3.6, 3.7
    """
    multiplier = SUFFIX_MULTIPLIERS[suffix]
    text = f"{n}{suffix}"
    result = parse_number(text)
    expected = int(n * multiplier)
    assert result is not None, f"parse_number({text!r}) returned None"
    # Allow ±1 rounding tolerance due to float precision
    assert abs(result - expected) <= 1, (
        f"parse_number({text!r}) = {result}, expected ~{expected}"
    )
