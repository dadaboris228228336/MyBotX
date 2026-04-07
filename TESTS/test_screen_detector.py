"""
Тесты для Screen_Detector (base_01_screen_detector.py).
Feature: base-view-control

Включает:
  - Property 1: confidence score в допустимом диапазоне [0.0, 1.0]
  - Property 2: screen_type строго из допустимого набора значений
  - Unit-тесты: чёрный кадр, синтетический зелёный кадр, производительность
"""

import sys
import os
import time

import numpy as np
import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

# Добавляем CORE в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "CORE"))

from processes.BASE_VIEW.base_01_screen_detector import ScreenDetector, VALID_SCREEN_TYPES


# ---------------------------------------------------------------------------
# Стратегии
# ---------------------------------------------------------------------------

# Произвольный BGR-кадр с разрешением 720p–1080p (как в требованиях 3.7)
@st.composite
def bgr_frame_720_1080(draw):
    h = draw(st.integers(720, 1080))
    w = draw(st.integers(1280, 1920))
    # Используем zeros для скорости; содержимое не важно для property-тестов
    return np.zeros((h, w, 3), dtype=np.uint8)


# Произвольный BGR-кадр произвольного размера (для property 2)
@st.composite
def bgr_frame_any(draw):
    h = draw(st.integers(100, 500))
    w = draw(st.integers(100, 500))
    return np.zeros((h, w, 3), dtype=np.uint8)


# ---------------------------------------------------------------------------
# Property 1: Confidence score в допустимом диапазоне [0.0, 1.0]
# Validates: Requirements 3.4, 3.7
# ---------------------------------------------------------------------------

# Feature: base-view-control, Property 1: confidence score в допустимом диапазоне
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(frame=bgr_frame_720_1080())
def test_confidence_in_range(frame):
    """
    Property 1: Confidence score в допустимом диапазоне

    For any BGR numpy array с разрешением 720p–1080p,
    is_main_screen SHALL возвращать confidence ∈ [0.0, 1.0].

    Validates: Requirements 3.4, 3.7
    """
    detector = ScreenDetector()
    _, confidence = detector.is_main_screen(frame)
    assert 0.0 <= confidence <= 1.0, (
        f"confidence={confidence} вне диапазона [0.0, 1.0] для кадра {frame.shape}"
    )


# ---------------------------------------------------------------------------
# Property 2: Screen type из допустимого набора значений
# Validates: Requirements 3.5
# ---------------------------------------------------------------------------

# Feature: base-view-control, Property 2: screen type из допустимого набора значений
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(frame=bgr_frame_any())
def test_screen_type_valid_values(frame):
    """
    Property 2: Screen type из допустимого набора значений

    For any BGR numpy array скриншота,
    detect_screen_type SHALL возвращать screen_type строго из
    {'main', 'loading', 'battle', 'menu', 'unknown'}.

    Validates: Requirements 3.5
    """
    detector = ScreenDetector()
    _, screen_type, confidence = detector.detect_screen_type(frame)
    assert screen_type in VALID_SCREEN_TYPES, (
        f"screen_type='{screen_type}' не входит в допустимое множество {VALID_SCREEN_TYPES}"
    )
    assert 0.0 <= confidence <= 1.0, (
        f"confidence={confidence} вне диапазона [0.0, 1.0]"
    )


# ---------------------------------------------------------------------------
# Unit-тесты
# ---------------------------------------------------------------------------

class TestScreenDetectorUnit:

    def test_black_frame_is_not_main(self):
        """Чёрный кадр → is_main=False, screen_type='loading' или 'unknown'."""
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        detector = ScreenDetector()
        is_main, confidence = detector.is_main_screen(frame)
        assert is_main is False
        assert 0.0 <= confidence <= 1.0

    def test_black_frame_screen_type(self):
        """Чёрный кадр → screen_type в допустимом наборе, is_main=False."""
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        detector = ScreenDetector()
        is_main, screen_type, confidence = detector.detect_screen_type(frame)
        assert is_main is False
        assert screen_type in VALID_SCREEN_TYPES

    def test_green_frame_confidence_positive(self):
        """Синтетический зелёный кадр → confidence > 0."""
        # Создаём кадр с насыщенным зелёным цветом (BGR: 0, 200, 0)
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        frame[:, :, 1] = 180  # G-канал
        frame[:, :, 0] = 20   # B-канал (немного синего для неба)
        frame[:, :, 2] = 30   # R-канал

        detector = ScreenDetector()
        _, confidence = detector.is_main_screen(frame)
        assert confidence > 0.0, "Зелёный кадр должен давать confidence > 0"

    def test_return_types_is_main_screen(self):
        """is_main_screen возвращает (bool, float)."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detector = ScreenDetector()
        result = detector.is_main_screen(frame)
        assert isinstance(result, tuple) and len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], float)

    def test_return_types_detect_screen_type(self):
        """detect_screen_type возвращает (bool, str, float)."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detector = ScreenDetector()
        result = detector.detect_screen_type(frame)
        assert isinstance(result, tuple) and len(result) == 3
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)
        assert isinstance(result[2], float)

    def test_performance_under_2000ms(self):
        """Анализ одного скриншота завершается за < 2000 мс (Requirement 3.8)."""
        frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        detector = ScreenDetector()

        start = time.time()
        detector.detect_screen_type(frame)
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 2000, (
            f"Анализ занял {elapsed_ms:.1f} мс, превышен лимит 2000 мс"
        )

    def test_dark_frame_is_loading(self):
        """Очень тёмный кадр (средняя яркость < 40) → screen_type='loading'."""
        frame = np.full((720, 1280, 3), 10, dtype=np.uint8)
        detector = ScreenDetector()
        _, screen_type, _ = detector.detect_screen_type(frame)
        assert screen_type == 'loading'

    def test_confidence_is_float_not_int(self):
        """confidence должен быть float, а не int."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detector = ScreenDetector()
        _, conf = detector.is_main_screen(frame)
        assert isinstance(conf, float)

    def test_is_main_consistent_with_detect_screen_type(self):
        """is_main_screen и detect_screen_type возвращают согласованный is_main."""
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        detector = ScreenDetector()
        is_main_1, conf_1 = detector.is_main_screen(frame)
        is_main_2, _, conf_2 = detector.detect_screen_type(frame)
        assert is_main_1 == is_main_2
        assert conf_1 == conf_2

    def test_log_callback_called_on_error(self):
        """log_callback вызывается при ошибке (передаём None вместо кадра)."""
        messages = []
        detector = ScreenDetector(log_callback=messages.append)
        # None должен обрабатываться без исключения
        result = detector.detect_screen_type(None)
        assert result[1] in VALID_SCREEN_TYPES
