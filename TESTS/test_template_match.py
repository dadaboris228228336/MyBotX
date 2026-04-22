"""
Tests for OPENCV/cv_01_template_match.py
Validates: Requirements 2.2, 2.3, 2.4
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).parent.parent / "CORE"))
from processes.OPENCV import TemplateMatch


def _solid_image(h: int, w: int, color=(128, 128, 128)) -> np.ndarray:
    """Create a solid-color BGR image."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = color
    return img


def _make_pattern_file(tmp_path: Path, name: str, h: int = 10, w: int = 10,
                       color=(200, 100, 50)) -> Path:
    """Save a small pattern PNG and return its path."""
    pattern = _solid_image(h, w, color)
    path = tmp_path / f"{name}.png"
    cv2.imwrite(str(path), pattern)
    return path


# ── Unit tests ────────────────────────────────────────────────────────────────

class TestTemplateMatch:

    def test_find_returns_none_for_missing_pattern(self, tmp_path):
        """find() returns None when pattern file does not exist."""
        tm = TemplateMatch(tmp_path)
        screen = _solid_image(100, 100)
        result = tm.find(screen, "nonexistent")
        assert result is None

    def test_find_returns_coords_for_matching_pattern(self, tmp_path):
        """find() returns (cx, cy) when pattern is present in screenshot."""
        # Use a unique gradient pattern to avoid false matches on solid background
        ph, pw = 10, 10
        pattern = np.zeros((ph, pw, 3), dtype=np.uint8)
        for i in range(ph):
            for j in range(pw):
                pattern[i, j] = (i * 20 + 50, j * 20 + 50, 100)
        path = tmp_path / "btn.png"
        cv2.imwrite(str(path), pattern)

        # Black background with pattern placed at (30, 20)
        screen = np.zeros((100, 100, 3), dtype=np.uint8)
        screen[20:30, 30:40] = pattern

        tm = TemplateMatch(tmp_path)
        result = tm.find(screen, "btn", threshold=0.8)
        assert result is not None
        cx, cy = result
        assert 25 <= cx <= 45, f"cx={cx} out of expected range"
        assert 15 <= cy <= 35, f"cy={cy} out of expected range"

    def test_find_all_returns_empty_for_missing_pattern(self, tmp_path):
        """find_all() returns [] when pattern file does not exist."""
        tm = TemplateMatch(tmp_path)
        screen = _solid_image(100, 100)
        result = tm.find_all(screen, "nonexistent")
        assert result == []

    def test_find_all_deduplicates_nearby_points(self, tmp_path):
        """find_all() removes duplicate points within 20px."""
        color = (200, 100, 50)
        _make_pattern_file(tmp_path, "btn", 5, 5, color)
        screen = _solid_image(200, 200, (0, 0, 0))
        # Place two identical patterns far apart
        screen[10:15, 10:15] = color
        screen[100:105, 100:105] = color
        tm = TemplateMatch(tmp_path)
        results = tm.find_all(screen, "btn", threshold=0.9)
        # No two points should be within 20px of each other
        for i, p1 in enumerate(results):
            for j, p2 in enumerate(results):
                if i != j:
                    dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
                    assert dist >= 20, f"Duplicate points found: {p1}, {p2}"

    def test_find_returns_none_when_pattern_larger_than_screenshot(self, tmp_path):
        """find() returns None when pattern is larger than screenshot."""
        _make_pattern_file(tmp_path, "big", 200, 200)
        screen = _solid_image(50, 50)
        tm = TemplateMatch(tmp_path)
        result = tm.find(screen, "big")
        assert result is None


# ── Property test P4 ──────────────────────────────────────────────────────────

# Feature: processes-restructure, Property 4: find() / find_all() consistency
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@given(
    px=st.integers(min_value=5, max_value=50),
    py=st.integers(min_value=5, max_value=50),
)
def test_find_find_all_consistency(px, py):
    """
    Property 4: When find() returns (cx, cy), find_all() must contain
    at least one point within 20px of (cx, cy).
    Validates: Requirements 2.2, 2.3
    """
    import tempfile, os
    color = (200, 100, 50)
    bg_color = (10, 20, 30)
    ph, pw = 8, 8

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _make_pattern_file(tmp_path, "p", ph, pw, color)

        screen_h = py + ph + 20
        screen_w = px + pw + 20
        screen = _solid_image(screen_h, screen_w, bg_color)
        screen[py:py + ph, px:px + pw] = color

        tm = TemplateMatch(tmp_path)
        coords = tm.find(screen, "p", threshold=0.9)

        if coords is not None:
            cx, cy = coords
            all_pts = tm.find_all(screen, "p", threshold=0.9)
            assert any(
                abs(pt[0] - cx) < 20 and abs(pt[1] - cy) < 20
                for pt in all_pts
            ), f"find() returned {coords} but find_all() returned {all_pts}"


# Feature: processes-restructure, Property 5: find_all() deduplication invariant
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    points=st.lists(
        st.tuples(st.integers(0, 150), st.integers(0, 150)),
        min_size=0,
        max_size=15,
    )
)
def test_find_all_deduplication_invariant(points):
    """
    Property 5: No two points in find_all() result are within 20px of each other.
    Validates: Requirements 2.3
    """
    import tempfile
    color = (200, 100, 50)
    bg_color = (10, 20, 30)
    ph, pw = 5, 5

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _make_pattern_file(tmp_path, "d", ph, pw, color)

        screen = _solid_image(200, 200, bg_color)
        for (x, y) in points:
            x = min(x, 200 - pw)
            y = min(y, 200 - ph)
            screen[y:y + ph, x:x + pw] = color

        tm = TemplateMatch(tmp_path)
        results = tm.find_all(screen, "d", threshold=0.9)

        for i, p1 in enumerate(results):
            for j, p2 in enumerate(results):
                if i != j:
                    assert not (abs(p1[0] - p2[0]) < 20 and abs(p1[1] - p2[1]) < 20), (
                        f"Deduplication failed: {p1} and {p2} are within 20px"
                    )
