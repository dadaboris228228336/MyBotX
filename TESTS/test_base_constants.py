"""
Property-Based Tests for BASE_VIEW constants helper.
Feature: base-view-control

Uses hypothesis for property-based testing.
Minimum 100 iterations per property test.
"""

import sys
import os

# Добавляем CORE в путь для импорта модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "CORE"))

import tempfile
import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from processes.BASE_VIEW.base_00_constants import load_constants, save_constants


# ---------------------------------------------------------------------------
# Стратегии генерации данных
# ---------------------------------------------------------------------------

# Генерация простых числовых значений (int и float), совместимых с JSON
_json_int = st.integers(min_value=0, max_value=10_000)
_json_float = st.floats(
    min_value=0.0,
    max_value=10_000.0,
    allow_nan=False,
    allow_infinity=False,
).map(lambda x: round(x, 6))

_json_scalar = st.one_of(_json_int, _json_float)

# Плоский словарь с числовыми значениями (имитирует секции base_constants.json)
_flat_dict_strategy = st.dictionaries(
    keys=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="_"),
        min_size=1,
        max_size=20,
    ),
    values=_json_scalar,
    min_size=1,
    max_size=10,
)


# ---------------------------------------------------------------------------
# Property 7: Round trip констант базы через JSON
# Validates: Requirements 7.3, 8.5
# ---------------------------------------------------------------------------

# Feature: base-view-control, Property 7: Round trip констант базы через JSON
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(constants=_flat_dict_strategy)
def test_constants_round_trip(constants):
    """
    Property 7: Round trip констант базы через JSON

    For any dictionary with numeric values, saving to base_constants.json
    and then loading it back SHALL return a dictionary equal to the original.

    Validates: Requirements 7.3, 8.5
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "base_constants.json")
        save_constants(constants, path)
        loaded = load_constants(path)
        assert loaded == constants, (
            f"Round trip failed: original={constants}, loaded={loaded}"
        )


# ---------------------------------------------------------------------------
# Unit-тесты load_constants / save_constants
# ---------------------------------------------------------------------------

def test_load_constants_missing_file():
    """load_constants возвращает пустой словарь если файл не существует."""
    result = load_constants("/nonexistent/path/base_constants.json")
    assert result == {}


def test_load_constants_invalid_json(tmp_path):
    """load_constants возвращает пустой словарь при невалидном JSON."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not a json {{{", encoding="utf-8")
    result = load_constants(str(bad_file))
    assert result == {}


def test_save_and_load_real_constants(tmp_path):
    """Сохранение и загрузка реальной структуры base_constants.json."""
    data = {
        "base": {
            "grid_width_cells": 44,
            "grid_height_cells": 44,
            "isometric_angle_right": 27.0,
            "isometric_angle_left": 153.0,
            "angle_tolerance": 3.0,
        },
        "zoom": {
            "pinch_step_px": 150,
            "pinch_duration_ms": 400,
            "max_out_steps": 5,
        },
    }
    path = str(tmp_path / "base_constants.json")
    result = save_constants(data, path)
    assert result is True
    loaded = load_constants(path)
    assert loaded == data


def test_save_constants_returns_true(tmp_path):
    """save_constants возвращает True при успешной записи."""
    path = str(tmp_path / "test.json")
    assert save_constants({"key": 1}, path) is True


def test_load_real_config_file():
    """Загрузка реального CONFIG/base_constants.json из проекта."""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "CONFIG", "base_constants.json"
    )
    data = load_constants(config_path)
    assert "base" in data
    assert "zoom" in data
    assert "centering" in data
    assert "buildings" in data
    assert data["base"]["grid_width_cells"] == 44
    assert data["base"]["grid_height_cells"] == 44
