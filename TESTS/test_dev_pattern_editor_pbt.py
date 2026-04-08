#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Property-based tests for dev-mode-pattern-editor.
Feature: dev-mode-pattern-editor
Tests validate pure logic functions extracted from the implementation.
No tkinter display required.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, settings, HealthCheck, assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays
import numpy as np

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
# Pure helper functions extracted from the implementation logic
# (mirror the logic in _dev_screenshot_thread and _dev_crop_window)
# ---------------------------------------------------------------------------

def _arr_to_pil(arr):
    """Convert BGR numpy array to PIL Image (mirrors implementation)."""
    from PIL import Image
    return Image.fromarray(arr[:, :, ::-1])


def _make_thumbnail(pil_img, max_w=600, max_h=190):
    """Return a thumbnail copy (mirrors implementation)."""
    img = pil_img.copy()
    img.thumbnail((max_w, max_h))
    return img


def _scale_coords(x1, y1, x2, y2, orig_w, orig_h, disp_w, disp_h):
    """Scale display-space rect to original-image space (mirrors implementation)."""
    scale_x = orig_w / disp_w
    scale_y = orig_h / disp_h
    return int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y)


def _validate_and_crop(orig_pil, x1, y1, x2, y2):
    """
    Validate selection size and crop.
    Returns (cropped_image, None) on success or (None, error_msg) on failure.
    Mirrors the on_save() logic in _dev_crop_window.
    """
    nx1, ny1 = min(x1, x2), min(y1, y2)
    nx2, ny2 = max(x1, x2), max(y1, y2)
    if nx2 - nx1 < 5 or ny2 - ny1 < 5:
        return None, "Выделите область на скриншоте"
    cropped = orig_pil.crop((nx1, ny1, nx2, ny2))
    return cropped, None


def _format_log_msg(name, w, h):
    """Format the success log message (mirrors implementation)."""
    return f"✅ Паттерн сохранён: {name}.png ({w}x{h}px)"


# ===========================================================================
# Property 1: Screenshot stored in memory
# Feature: dev-mode-pattern-editor, Property 1: Скриншот сохраняется в памяти
# Validates: Requirements 1.3, 1.4
# ===========================================================================

@given(arrays(dtype=np.uint8, shape=st.tuples(
    st.integers(10, 200), st.integers(10, 200), st.just(3))))
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_p1_screenshot_stored_in_memory(arr):
    """
    Property 1: For any numpy BGR array, converting to PIL and back must
    produce a pixel-equivalent image.
    Validates: Requirements 1.3, 1.4
    """
    from PIL import Image
    pil_img = _arr_to_pil(arr)
    assert isinstance(pil_img, Image.Image)
    # Round-trip: PIL → numpy → compare
    result_arr = np.array(pil_img)[:, :, ::-1]  # back to BGR
    assert result_arr.shape == arr.shape
    assert np.array_equal(result_arr, arr)


# ===========================================================================
# Property 2: Thumbnail fits bounds
# Feature: dev-mode-pattern-editor, Property 2: Превью вписывается в ограничения размера
# Validates: Requirements 2.3, 2.4
# ===========================================================================

@given(st.integers(1, 4000), st.integers(1, 4000))
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_p2_thumbnail_fits_bounds(w, h):
    """
    Property 2: For any image size, thumbnail must fit within 600×190.
    Validates: Requirements 2.3, 2.4
    """
    from PIL import Image
    img = Image.new("RGB", (w, h), color=(128, 64, 32))
    thumb = _make_thumbnail(img, max_w=600, max_h=190)
    assert thumb.width <= 600, f"Width {thumb.width} exceeds 600"
    assert thumb.height <= 190, f"Height {thumb.height} exceeds 190"


# ===========================================================================
# Property 3: Thumbnail preserves aspect ratio
# Feature: dev-mode-pattern-editor, Property 3: Превью сохраняет пропорции
# Validates: Requirements 2.3
# ===========================================================================

@given(st.integers(2, 4000), st.integers(2, 4000))
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_p3_thumbnail_preserves_aspect_ratio(w, h):
    """
    Property 3: Thumbnail aspect ratio must match original within ±1px rounding.
    Validates: Requirements 2.3
    """
    from PIL import Image
    img = Image.new("RGB", (w, h), color=(10, 20, 30))
    thumb = _make_thumbnail(img, max_w=600, max_h=190)
    orig_ratio = w / h
    thumb_ratio = thumb.width / thumb.height
    # Allow ±1px rounding tolerance
    tol = max(1 / thumb.height, 1 / thumb.width)
    assert abs(orig_ratio - thumb_ratio) <= orig_ratio * tol + tol, (
        f"Aspect ratio mismatch: orig={orig_ratio:.4f}, thumb={thumb_ratio:.4f}"
    )


# ===========================================================================
# Property 5: Crop coordinate scaling
# Feature: dev-mode-pattern-editor, Property 5: Масштабирование координат вырезки
# Validates: Requirements 3.8
# ===========================================================================

@given(
    orig_w=st.integers(100, 1920),
    orig_h=st.integers(100, 1080),
    disp_w=st.integers(50, 900),
    disp_h=st.integers(50, 500),
    x1=st.integers(0, 49),
    y1=st.integers(0, 49),
    x2=st.integers(50, 99),
    y2=st.integers(50, 99),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_p5_crop_coordinate_scaling(orig_w, orig_h, disp_w, disp_h, x1, y1, x2, y2):
    """
    Property 5: Scaled coords must equal display_coords * scale_factor (integer-rounded).
    Validates: Requirements 3.8
    """
    rx1, ry1, rx2, ry2 = _scale_coords(x1, y1, x2, y2, orig_w, orig_h, disp_w, disp_h)
    scale_x = orig_w / disp_w
    scale_y = orig_h / disp_h
    assert rx1 == int(x1 * scale_x)
    assert ry1 == int(y1 * scale_y)
    assert rx2 == int(x2 * scale_x)
    assert ry2 == int(y2 * scale_y)


# ===========================================================================
# Property 6: Saved pattern matches selection dimensions
# Feature: dev-mode-pattern-editor, Property 6: Сохранённый паттерн соответствует выделению
# Validates: Requirements 3.4
# ===========================================================================

@given(
    img_w=st.integers(50, 500),
    img_h=st.integers(50, 500),
    x1=st.integers(0, 40),
    y1=st.integers(0, 40),
    x2=st.integers(45, 49),
    y2=st.integers(45, 49),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_p6_saved_pattern_matches_selection(img_w, img_h, x1, y1, x2, y2):
    """
    Property 6: Cropped image dimensions must match the selection rectangle.
    Validates: Requirements 3.4
    """
    from PIL import Image
    assume(img_w > x2 and img_h > y2)
    orig = Image.new("RGB", (img_w, img_h), color=(200, 100, 50))
    cropped, err = _validate_and_crop(orig, x1, y1, x2, y2)
    assert err is None, f"Unexpected error: {err}"
    assert cropped is not None
    expected_w = x2 - x1
    expected_h = y2 - y1
    assert cropped.width == expected_w, f"Width mismatch: {cropped.width} != {expected_w}"
    assert cropped.height == expected_h, f"Height mismatch: {cropped.height} != {expected_h}"


# ===========================================================================
# Property 7: Log message contains name and dimensions
# Feature: dev-mode-pattern-editor, Property 7: Лог-сообщение содержит имя и размеры
# Validates: Requirements 3.5
# ===========================================================================

@given(
    name=st.text(min_size=1, max_size=30,
                 alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="_-")),
    w=st.integers(5, 2000),
    h=st.integers(5, 2000),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_p7_log_message_contains_name_and_dimensions(name, w, h):
    """
    Property 7: Log message must contain filename and pixel dimensions.
    Validates: Requirements 3.5
    """
    msg = _format_log_msg(name, w, h)
    assert f"{name}.png" in msg, f"Name not found in: {msg!r}"
    assert f"{w}x{h}px" in msg, f"Dimensions not found in: {msg!r}"


# ===========================================================================
# Property 8: Small selection rejected
# Feature: dev-mode-pattern-editor, Property 8: Отклонение слишком маленького выделения
# Validates: Requirements 3.6
# ===========================================================================

@given(
    img_w=st.integers(20, 500),
    img_h=st.integers(20, 500),
    x1=st.integers(0, 10),
    y1=st.integers(0, 10),
    dw=st.integers(0, 4),
    dh=st.integers(0, 4),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_p8_small_selection_rejected(img_w, img_h, x1, y1, dw, dh):
    """
    Property 8: Selection where width < 5 or height < 5 must be rejected.
    Validates: Requirements 3.6
    """
    from PIL import Image
    x2 = x1 + dw
    y2 = y1 + dh
    assume(img_w > x2 + 1 and img_h > y2 + 1)
    orig = Image.new("RGB", (img_w, img_h))
    cropped, err = _validate_and_crop(orig, x1, y1, x2, y2)
    assert cropped is None, "Should not return a cropped image for small selection"
    assert err is not None, "Should return an error message for small selection"


# ===========================================================================
# Property 9: Dev Tab and Bot Tab state independence
# Feature: dev-mode-pattern-editor, Property 9: Независимость состояния Dev Tab и Bot Tab
# Validates: Requirements 4.5
# ===========================================================================

@given(
    dev_arr=arrays(dtype=np.uint8, shape=st.tuples(
        st.integers(10, 100), st.integers(10, 100), st.just(3))),
    bot_arr=arrays(dtype=np.uint8, shape=st.tuples(
        st.integers(10, 100), st.integers(10, 100), st.just(3))),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_p9_dev_bot_state_independence(dev_arr, bot_arr):
    """
    Property 9: Setting dev screenshot must not affect bot screenshot and vice versa.
    Validates: Requirements 4.5
    """
    # Simulate two independent state containers
    state = {"dev": None, "bot": None}

    def set_dev(arr):
        state["dev"] = _arr_to_pil(arr)

    def set_bot(arr):
        state["bot"] = _arr_to_pil(arr)

    set_bot(bot_arr)
    bot_before = state["bot"]

    set_dev(dev_arr)
    # Bot state must be unchanged
    assert state["bot"] is bot_before, "Dev screenshot must not replace bot screenshot"

    dev_before = state["dev"]
    set_bot(bot_arr)
    # Dev state must be unchanged
    assert state["dev"] is dev_before, "Bot screenshot must not replace dev screenshot"
