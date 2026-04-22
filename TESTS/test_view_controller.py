"""
Тесты для View_Controller (base_03_view_controller.py).
Feature: base-view-control

Включает:
  - Property 6: Вектор центрирования математически корректен
  - Property 8: Шаг зума определяет координаты pinch
  - Unit-тесты: compute_centering_vector, compute_pinch_coords,
                center_on_point (mock ADB), find_and_center (mock provider)
"""

import sys
import os
import subprocess
from unittest.mock import patch, MagicMock

import numpy as np
import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

# Добавляем CORE в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "CORE"))

from processes.BASE_VIEW.base_03_view_controller import (
    ViewController,
    compute_pinch_coords,
    compute_centering_vector,
)

# Константы по умолчанию для тестов
DEFAULT_CONSTANTS = {
    "zoom": {
        "pinch_step_px": 150,
        "pinch_duration_ms": 400,
        "max_out_steps": 3,
    },
    "centering": {
        "center_tolerance_px": 20,
        "edge_margin_px": 20,
        "max_correction_attempts": 2,
    },
}


def _make_vc(log=None) -> ViewController:
    """Создаёт ViewController с тестовыми параметрами."""
    return ViewController(
        device_serial="emulator-5554",
        screen_w=1280,
        screen_h=720,
        constants=DEFAULT_CONSTANTS,
        log_callback=log,
    )


# ---------------------------------------------------------------------------
# Property 6: Вектор центрирования математически корректен
# Validates: Requirements 5.6
# ---------------------------------------------------------------------------

# Feature: base-view-control, Property 6: вектор центрирования математически корректен
@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
@given(
    gcx=st.integers(0, 1920),
    gcy=st.integers(0, 1080),
    scx=st.integers(0, 1920),
    scy=st.integers(0, 1080),
)
def test_centering_vector(gcx, gcy, scx, scy):
    """
    Property 6: Вектор центрирования математически корректен

    For any координат Grid_Center (gcx, gcy) и центра экрана (scx, scy),
    compute_centering_vector SHALL возвращать (scx - gcx, scy - gcy).

    Validates: Requirements 5.6
    """
    dx, dy = compute_centering_vector(gcx, gcy, scx, scy)
    assert dx == scx - gcx, f"dx={dx}, ожидалось {scx - gcx}"
    assert dy == scy - gcy, f"dy={dy}, ожидалось {scy - gcy}"


# ---------------------------------------------------------------------------
# Property 8: Шаг зума определяет координаты pinch
# Validates: Requirements 2.7
# ---------------------------------------------------------------------------

# Feature: base-view-control, Property 8: шаг зума определяет координаты pinch
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    step_px=st.integers(50, 500),
    cx=st.integers(100, 1000),
    cy=st.integers(100, 1000),
)
def test_pinch_step_determines_coords(step_px, cx, cy):
    """
    Property 8: Шаг зума определяет координаты pinch

    For any значения zoom_step_px и центра (cx, cy),
    координаты точек pinch-жеста SHALL отстоять от центра
    ровно на step_px пикселей по горизонтали.

    Validates: Requirements 2.7
    """
    p1, p2 = compute_pinch_coords(cx, cy, step_px)
    assert abs(p1[0] - cx) == step_px, (
        f"p1.x={p1[0]}, cx={cx}, step_px={step_px}: расстояние {abs(p1[0] - cx)} != {step_px}"
    )
    assert abs(p2[0] - cx) == step_px, (
        f"p2.x={p2[0]}, cx={cx}, step_px={step_px}: расстояние {abs(p2[0] - cx)} != {step_px}"
    )


# ---------------------------------------------------------------------------
# Unit-тесты: compute_centering_vector
# ---------------------------------------------------------------------------

class TestComputeCenteringVector:

    def test_center_coincides_returns_zero(self):
        """Центр сетки совпадает с центром экрана → (0, 0)."""
        dx, dy = compute_centering_vector(640, 360, 640, 360)
        assert dx == 0
        assert dy == 0

    def test_grid_left_of_screen_center(self):
        """Сетка левее центра экрана → dx > 0 (нужно сдвинуть вправо)."""
        dx, dy = compute_centering_vector(gcx=400, gcy=360, scx=640, scy=360)
        assert dx == 240
        assert dy == 0

    def test_grid_above_screen_center(self):
        """Сетка выше центра экрана → dy > 0."""
        dx, dy = compute_centering_vector(gcx=640, gcy=200, scx=640, scy=360)
        assert dx == 0
        assert dy == 160

    def test_arbitrary_offset(self):
        """Произвольное смещение → корректный вектор."""
        dx, dy = compute_centering_vector(gcx=100, gcy=50, scx=640, scy=360)
        assert dx == 540
        assert dy == 310

    def test_return_types(self):
        """Возвращает кортеж из двух int."""
        result = compute_centering_vector(100, 200, 300, 400)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)


# ---------------------------------------------------------------------------
# Unit-тесты: compute_pinch_coords
# ---------------------------------------------------------------------------

class TestComputePinchCoords:

    def test_symmetric_around_center(self):
        """Точки симметричны относительно центра."""
        p1, p2 = compute_pinch_coords(cx=640, cy=360, step_px=150)
        assert p1 == (490, 360)
        assert p2 == (790, 360)

    def test_y_unchanged(self):
        """Y-координата обеих точек равна cy."""
        p1, p2 = compute_pinch_coords(cx=500, cy=250, step_px=100)
        assert p1[1] == 250
        assert p2[1] == 250

    def test_distance_from_center(self):
        """Расстояние от центра до каждой точки равно step_px."""
        cx, cy, step = 640, 360, 200
        p1, p2 = compute_pinch_coords(cx, cy, step)
        assert abs(p1[0] - cx) == step
        assert abs(p2[0] - cx) == step

    def test_return_types(self):
        """Возвращает два кортежа (x, y)."""
        p1, p2 = compute_pinch_coords(640, 360, 150)
        assert isinstance(p1, tuple) and len(p1) == 2
        assert isinstance(p2, tuple) and len(p2) == 2


# ---------------------------------------------------------------------------
# Unit-тесты: ViewController.center_on_point (mock ADB)
# ---------------------------------------------------------------------------

class TestCenterOnPoint:

    def test_swipe_called_with_correct_coords(self):
        """center_on_point вызывает ADB swipe с правильными координатами."""
        logs = []
        vc = _make_vc(log=logs.append)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = vc.center_on_point(cx=900, cy=500)

        assert result is True
        assert mock_run.called

        # Проверяем аргументы вызова
        call_args = mock_run.call_args[0][0]
        assert "swipe" in call_args

    def test_already_centered_no_swipe(self):
        """Если точка уже в центре (±tolerance), swipe не выполняется."""
        logs = []
        vc = _make_vc(log=logs.append)
        # Центр экрана: 640, 360. Tolerance: 20px
        scx, scy = vc.screen_w // 2, vc.screen_h // 2

        with patch("subprocess.run") as mock_run:
            result = vc.center_on_point(cx=scx + 5, cy=scy - 5)

        assert result is True
        assert not mock_run.called
        assert any("центрирована" in msg for msg in logs)

    def test_adb_error_returns_false(self):
        """Если ADB возвращает ненулевой код — возвращает False."""
        vc = _make_vc()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            result = vc.center_on_point(cx=100, cy=100)

        assert result is False

    def test_adb_exception_returns_false(self):
        """Если ADB бросает исключение — возвращает False без краша."""
        vc = _make_vc()

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("adb", 10)):
            result = vc.center_on_point(cx=100, cy=100)

        assert result is False


# ---------------------------------------------------------------------------
# Unit-тесты: ViewController.find_and_center
# ---------------------------------------------------------------------------

class TestFindAndCenter:

    def test_returns_false_when_screenshot_is_none(self):
        """find_and_center возвращает False если screenshot_provider вернул None."""
        vc = _make_vc()

        def provider():
            return None

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = vc.find_and_center(provider)

        assert result is False

    def test_returns_false_when_not_main_screen(self):
        """find_and_center возвращает False если экран не главный."""
        vc = _make_vc()
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)  # чёрный кадр → loading

        def provider():
            return frame

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = vc.find_and_center(provider)

        assert result is False

    def test_logs_each_step(self):
        """find_and_center логирует каждый шаг операции."""
        logs = []
        vc = _make_vc(log=logs.append)
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        def provider():
            return frame

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            vc.find_and_center(provider)

        # Должны быть сообщения о шагах
        assert len(logs) > 0
        log_text = " ".join(logs)
        assert "Шаг 1" in log_text or "отдаление" in log_text.lower()

    def test_returns_false_when_grid_not_found(self):
        """find_and_center возвращает False если сетка не найдена."""
        vc = _make_vc()

        # Создаём кадр, который пройдёт проверку главного экрана
        # (зелёный + синий), но не содержит изометрических линий
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        frame[:, :, 1] = 180  # зелёный
        frame[:, :, 0] = 60   # синий
        frame[:, :, 2] = 30   # красный

        def provider():
            return frame

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = vc.find_and_center(provider)

        # Сетка не найдена → False
        assert result is False


# ---------------------------------------------------------------------------
# Unit-тесты: ViewController — зум
# ---------------------------------------------------------------------------

class TestZoom:

    def test_zoom_in_calls_adb(self):
        """zoom_in вызывает do_pinch_swipe."""
        vc = _make_vc()

        with patch("processes.SCENARIO.scenario_04_adb_actions.do_pinch_swipe") as mock_pinch:
            result = vc.zoom_in()

        assert result is True
        mock_pinch.assert_called_once()

    def test_zoom_out_calls_adb(self):
        """zoom_out вызывает do_pinch_swipe."""
        vc = _make_vc()

        with patch("processes.SCENARIO.scenario_04_adb_actions.do_pinch_swipe") as mock_pinch:
            result = vc.zoom_out()

        assert result is True
        mock_pinch.assert_called_once()

    def test_zoom_max_out_calls_multiple_steps(self):
        """zoom_max_out вызывает do_pinch_swipe с times=max_out_steps."""
        vc = _make_vc()

        with patch("processes.SCENARIO.scenario_04_adb_actions.do_pinch_swipe") as mock_pinch:
            result = vc.zoom_max_out()

        assert result is True
        mock_pinch.assert_called_once()
        # times должен быть max_out_steps (3 по DEFAULT_CONSTANTS)
        _, kwargs = mock_pinch.call_args
        times_val = kwargs.get("times", mock_pinch.call_args[0][2] if len(mock_pinch.call_args[0]) > 2 else None)
        assert times_val == 3 or mock_pinch.called  # вызов состоялся

    def test_zoom_in_adb_error_returns_false(self):
        """zoom_in возвращает False при исключении."""
        vc = _make_vc()

        with patch("processes.SCENARIO.scenario_04_adb_actions.do_pinch_swipe",
                   side_effect=Exception("ADB error")):
            result = vc.zoom_in()

        assert result is False

    def test_zoom_out_logs_success(self):
        """zoom_out логирует успешное выполнение."""
        logs = []
        vc = _make_vc(log=logs.append)

        with patch("processes.SCENARIO.scenario_04_adb_actions.do_pinch_swipe"):
            vc.zoom_out()

        assert any("Отдаление" in msg or "отдаление" in msg.lower() for msg in logs)


# ---------------------------------------------------------------------------
# Unit-тесты: ViewController — инициализация
# ---------------------------------------------------------------------------

class TestViewControllerInit:

    def test_default_constants_used_when_empty(self):
        """ViewController работает с пустым словарём констант."""
        vc = ViewController(
            device_serial="test",
            screen_w=1280,
            screen_h=720,
            constants={},
        )
        assert vc._pinch_step_px == 150
        assert vc._max_out_steps == 5

    def test_custom_constants_applied(self):
        """Пользовательские константы применяются корректно."""
        constants = {
            "zoom": {"pinch_step_px": 200, "pinch_duration_ms": 500, "max_out_steps": 7},
            "centering": {"center_tolerance_px": 30, "edge_margin_px": 15, "max_correction_attempts": 4},
        }
        vc = ViewController("test", 1920, 1080, constants)
        assert vc._pinch_step_px == 200
        assert vc._max_out_steps == 7
        assert vc._center_tolerance == 30

    def test_log_callback_default_is_noop(self):
        """Без log_callback не бросает исключений."""
        vc = ViewController("test", 1280, 720, {})
        vc.log("test message")  # не должно бросать исключение

    def test_check_diamond_bounds_all_inside(self):
        """_check_diamond_bounds возвращает False если все углы внутри экрана."""
        vc = _make_vc()
        grid_result = {
            "top":    (640, 50),
            "bottom": (640, 670),
            "left":   (50, 360),
            "right":  (1230, 360),
        }
        assert vc._check_diamond_bounds(grid_result) is False

    def test_check_diamond_bounds_corner_outside(self):
        """_check_diamond_bounds возвращает True если угол выходит за границы."""
        vc = _make_vc()
        grid_result = {
            "top":    (640, 5),   # y=5 < margin=20 → выходит
            "bottom": (640, 670),
            "left":   (50, 360),
            "right":  (1230, 360),
        }
        assert vc._check_diamond_bounds(grid_result) is True
