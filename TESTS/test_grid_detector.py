"""
Тесты для Grid_Detector (base_02_grid_detector.py).
Feature: base-view-control

Включает:
  - Property 3: Grid_Detector возвращает корректный тип результата
  - Property 4: Кадр без изометрических линий → None
  - Property 5: Визуализация не мутирует исходный кадр
  - Unit-тесты: синтетические изображения, пустой кадр, производительность
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

from processes.BASE_VIEW.base_02_grid_detector import GridDetector

# Константы по умолчанию для тестов
DEFAULT_CONSTANTS = {
    "base": {
        "grid_width_cells": 44,
        "grid_height_cells": 44,
        "isometric_angle_right": 27.0,
        "isometric_angle_left": 153.0,
        "angle_tolerance": 3.0,
    }
}

# Результат-заглушка для visualize
_MOCK_RESULT = {"top": (50, 10), "bottom": (50, 90), "left": (10, 50),
                "right": (90, 50), "center": (50, 50), "confidence": 0.5}


# ---------------------------------------------------------------------------
# Стратегии
# ---------------------------------------------------------------------------

@st.composite
def bgr_frame_720_1080(draw):
    """Произвольный BGR-кадр 720p–1080p (нулевой для скорости)."""
    h = draw(st.integers(720, 1080))
    w = draw(st.integers(1280, 1920))
    return np.zeros((h, w, 3), dtype=np.uint8)


@st.composite
def bgr_frame_any(draw):
    """Произвольный BGR-кадр произвольного размера (нулевой для скорости)."""
    h = draw(st.integers(100, 500))
    w = draw(st.integers(100, 500))
    # Используем случайное заполнение через integers для разнообразия
    fill = draw(st.integers(0, 255))
    return np.full((h, w, 3), fill, dtype=np.uint8)


# ---------------------------------------------------------------------------
# Property 3: Grid_Detector возвращает корректный тип результата
# Validates: Requirements 4.1, 4.5
# ---------------------------------------------------------------------------

# Feature: base-view-control, Property 3: Grid_Detector возвращает корректный тип результата
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(frame=bgr_frame_720_1080())
def test_grid_result_valid(frame):
    """
    Property 3: Grid_Detector возвращает корректный тип результата

    For any BGR numpy array с разрешением 720p–1080p,
    detect_grid SHALL возвращать либо None, либо кортеж (cx, cy, confidence)
    где cx ∈ [0, width), cy ∈ [0, height), confidence ∈ [0.0, 1.0].

    Validates: Requirements 4.1, 4.5
    """
    height, width = frame.shape[:2]
    detector = GridDetector(DEFAULT_CONSTANTS)
    result = detector.detect_grid(frame)

    if result is not None:
        assert isinstance(result, tuple), f"Ожидался tuple, получен {type(result)}"
        assert len(result) == 3, f"Ожидался кортеж из 3 элементов, получен {len(result)}"
        cx, cy, confidence = result
        assert 0 <= cx < width,  f"cx={cx} вне диапазона [0, {width})"
        assert 0 <= cy < height, f"cy={cy} вне диапазона [0, {height})"
        assert 0.0 <= confidence <= 1.0, f"confidence={confidence} вне [0.0, 1.0]"


# ---------------------------------------------------------------------------
# Property 4: Кадр без изометрических линий → None
# Validates: Requirements 4.6
# ---------------------------------------------------------------------------

# Feature: base-view-control, Property 4: кадр без изометрических линий → None
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    h=st.integers(100, 500),
    w=st.integers(100, 500),
    fill_value=st.integers(0, 255),
)
def test_grid_none_on_uniform_frame(h, w, fill_value):
    """
    Property 4: Кадр без изометрических линий → None

    For any однородного кадра (без структурных линий),
    detect_grid SHALL возвращать None.

    Validates: Requirements 4.6
    """
    frame = np.full((h, w, 3), fill_value, dtype=np.uint8)
    detector = GridDetector(DEFAULT_CONSTANTS)
    result = detector.detect_grid(frame)
    assert result is None, (
        f"Ожидался None для однородного кадра {h}x{w} fill={fill_value}, "
        f"получен {result}"
    )


# ---------------------------------------------------------------------------
# Property 5: Визуализация не мутирует исходный кадр
# Validates: Requirements 4.9
# ---------------------------------------------------------------------------

# Feature: base-view-control, Property 5: визуализация не мутирует исходный кадр
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(frame=bgr_frame_any())
def test_visualize_no_mutation(frame):
    """
    Property 5: Визуализация не мутирует исходный кадр

    For any BGR numpy array скриншота,
    visualize SHALL не изменять содержимое исходного массива frame.

    Validates: Requirements 4.9
    """
    original = frame.copy()
    detector = GridDetector(DEFAULT_CONSTANTS)
    output = detector.visualize(frame, _MOCK_RESULT)

    assert np.array_equal(frame, original), (
        "visualize мутировала исходный кадр!"
    )
    assert output is not frame, "visualize вернула тот же объект, а не копию"


# ---------------------------------------------------------------------------
# Unit-тесты
# ---------------------------------------------------------------------------

class TestGridDetectorUnit:

    def _make_isometric_frame(self, height=600, width=800):
        """
        Создаёт синтетическое изображение с нарисованными изометрическими линиями.
        Рисует несколько линий под углом ~27° и ~153°, ограниченных размером кадра.
        """
        try:
            import cv2
        except ImportError:
            pytest.skip("cv2 не доступен")

        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Рисуем линии под углом ~27° (правые диагонали)
        # Для угла 27°: dy/dx = tan(27°) ≈ 0.5095
        # Ограничиваем длину линии чтобы она помещалась в кадр
        tan27 = np.tan(np.radians(27.0))
        seg_len = 200  # длина сегмента в пикселях
        dx = int(seg_len * np.cos(np.radians(27.0)))
        dy = int(seg_len * np.sin(np.radians(27.0)))

        for y_start in range(50, height - dy - 10, 60):
            for x_start in range(50, width - dx - 10, 120):
                x1, y1 = x_start, y_start
                x2, y2 = x_start + dx, y_start + dy
                cv2.line(frame, (x1, y1), (x2, y2), (200, 200, 200), 2)

        # Рисуем линии под углом ~153° (левые диагонали)
        # Угол 153° = 180° - 27°: dx отрицательный
        dx2 = int(seg_len * np.cos(np.radians(153.0)))  # отрицательный
        dy2 = int(seg_len * np.sin(np.radians(153.0)))  # положительный

        for y_start in range(50, height - dy2 - 10, 60):
            for x_start in range(-dx2 + 10, width - 10, 120):
                x1, y1 = x_start, y_start
                x2, y2 = x_start + dx2, y_start + dy2
                if 0 <= x2 < width and 0 <= y2 < height:
                    cv2.line(frame, (x1, y1), (x2, y2), (200, 200, 200), 2)

        return frame

    def test_detect_grid_on_isometric_frame(self):
        """Синтетическое изображение с изометрическими линиями → сетка найдена."""
        try:
            import cv2
        except ImportError:
            pytest.skip("cv2 не доступен")

        frame = self._make_isometric_frame()
        detector = GridDetector(DEFAULT_CONSTANTS)
        result = detector.detect_grid(frame)

        assert result is not None, "Сетка должна быть найдена на синтетическом изображении"
        cx, cy, confidence = result
        assert 0 <= cx < frame.shape[1]
        assert 0 <= cy < frame.shape[0]
        assert 0.0 <= confidence <= 1.0

    def test_detect_grid_empty_frame_returns_none(self):
        """Пустой (чёрный) кадр → None."""
        frame = np.zeros((400, 600, 3), dtype=np.uint8)
        detector = GridDetector(DEFAULT_CONSTANTS)
        result = detector.detect_grid(frame)
        assert result is None

    def test_detect_grid_none_input(self):
        """None на входе → None без исключения."""
        detector = GridDetector(DEFAULT_CONSTANTS)
        result = detector.detect_grid(None)
        assert result is None

    def test_detect_grid_diamond_on_isometric_frame(self):
        """Синтетическое изображение → detect_grid_diamond возвращает dict с нужными ключами."""
        try:
            import cv2
        except ImportError:
            pytest.skip("cv2 не доступен")

        frame = self._make_isometric_frame()
        detector = GridDetector(DEFAULT_CONSTANTS)
        result = detector.detect_grid_diamond(frame)

        if result is not None:
            for key in ("top", "bottom", "left", "right", "center", "confidence"):
                assert key in result, f"Ключ '{key}' отсутствует в результате"
            assert 0.0 <= result["confidence"] <= 1.0

    def test_detect_grid_diamond_empty_frame(self):
        """Пустой кадр → detect_grid_diamond возвращает None."""
        frame = np.zeros((400, 600, 3), dtype=np.uint8)
        detector = GridDetector(DEFAULT_CONSTANTS)
        result = detector.detect_grid_diamond(frame)
        assert result is None

    def test_visualize_returns_new_array(self):
        """visualize возвращает новый массив, не тот же объект."""
        frame = np.zeros((200, 300, 3), dtype=np.uint8)
        detector = GridDetector(DEFAULT_CONSTANTS)
        output = detector.visualize(frame, _MOCK_RESULT)
        assert output is not frame

    def test_visualize_with_none_result(self):
        """visualize с result=None возвращает копию кадра без исключений."""
        frame = np.zeros((200, 300, 3), dtype=np.uint8)
        detector = GridDetector(DEFAULT_CONSTANTS)
        output = detector.visualize(frame, None)
        assert output is not None
        assert output.shape == frame.shape
        assert np.array_equal(output, frame)

    def test_visualize_with_tuple_result(self):
        """visualize с кортежем (cx, cy, conf) работает без исключений."""
        frame = np.zeros((200, 300, 3), dtype=np.uint8)
        detector = GridDetector(DEFAULT_CONSTANTS)
        output = detector.visualize(frame, (150, 100, 0.8))
        assert output is not None
        assert output.shape == frame.shape

    def test_detect_grid_result_types(self):
        """detect_grid возвращает кортеж с правильными типами."""
        try:
            import cv2
        except ImportError:
            pytest.skip("cv2 не доступен")

        frame = self._make_isometric_frame()
        detector = GridDetector(DEFAULT_CONSTANTS)
        result = detector.detect_grid(frame)

        if result is not None:
            cx, cy, confidence = result
            assert isinstance(cx, int), f"cx должен быть int, получен {type(cx)}"
            assert isinstance(cy, int), f"cy должен быть int, получен {type(cy)}"
            assert isinstance(confidence, float), f"confidence должен быть float, получен {type(confidence)}"

    def test_log_callback_called(self):
        """log_callback вызывается при отсутствии линий."""
        messages = []
        frame = np.zeros((200, 300, 3), dtype=np.uint8)
        detector = GridDetector(DEFAULT_CONSTANTS, log_callback=messages.append)
        detector.detect_grid(frame)
        # Должно быть хотя бы одно сообщение в лог
        assert len(messages) > 0

    def test_performance_under_3000ms(self):
        """Анализ одного скриншота завершается за < 3000 мс (Requirement 4.8)."""
        try:
            import cv2
        except ImportError:
            pytest.skip("cv2 не доступен")

        frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        detector = GridDetector(DEFAULT_CONSTANTS)

        start = time.time()
        detector.detect_grid(frame)
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 3000, (
            f"Анализ занял {elapsed_ms:.1f} мс, превышен лимит 3000 мс"
        )

    def test_empty_constants(self):
        """GridDetector работает с пустым словарём констант (использует defaults)."""
        frame = np.zeros((200, 300, 3), dtype=np.uint8)
        detector = GridDetector({})
        result = detector.detect_grid(frame)
        assert result is None  # пустой кадр → None

    def test_uniform_white_frame_returns_none(self):
        """Белый однородный кадр → None."""
        frame = np.full((300, 400, 3), 255, dtype=np.uint8)
        detector = GridDetector(DEFAULT_CONSTANTS)
        result = detector.detect_grid(frame)
        assert result is None
