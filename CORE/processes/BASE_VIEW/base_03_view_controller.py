"""
View_Controller — управление видом базы Clash of Clans через ADB.

Функционал:
  - zoom_in / zoom_out / zoom_max_out через ADB pinch-жесты
  - center_on_point(cx, cy) через ADB swipe
  - find_and_center(screenshot_provider): полная операция центрирования

Вспомогательные функции (модульного уровня):
  - compute_pinch_coords(cx, cy, step_px) → (p1, p2)
  - compute_centering_vector(gcx, gcy, scx, scy) → (dx, dy)

Все операции с ADB обёрнуты в try/except. Таймаут операции — 35 сек.
"""

import subprocess
import time
import threading
from pathlib import Path
from typing import Optional, Callable, Tuple


def _get_adb_path() -> str:
    local_adb = Path(__file__).parent.parent.parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    return str(local_adb) if local_adb.exists() else "adb"


# ---------------------------------------------------------------------------
# Вспомогательные функции (модульного уровня)
# ---------------------------------------------------------------------------

def compute_pinch_coords(cx: int, cy: int, step_px: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    Вычисляет координаты двух точек pinch-жеста.

    Точки расположены симметрично относительно центра (cx, cy)
    по горизонтали на расстоянии step_px от центра.

    Args:
        cx:      X-координата центра жеста
        cy:      Y-координата центра жеста
        step_px: расстояние от центра до каждой точки (в пикселях)

    Returns:
        (p1, p2) — два кортежа (x, y):
            p1 = (cx - step_px, cy)
            p2 = (cx + step_px, cy)
    """
    p1 = (cx - step_px, cy)
    p2 = (cx + step_px, cy)
    return p1, p2


def compute_centering_vector(gcx: int, gcy: int, scx: int, scy: int) -> Tuple[int, int]:
    """
    Вычисляет вектор смещения для центрирования.

    Возвращает разницу между центром экрана и центром сетки,
    то есть на сколько пикселей нужно сдвинуть вид.

    Args:
        gcx: X-координата центра сетки (Grid_Center)
        gcy: Y-координата центра сетки (Grid_Center)
        scx: X-координата центра экрана (Screen_Center)
        scy: Y-координата центра экрана (Screen_Center)

    Returns:
        (dx, dy) = (scx - gcx, scy - gcy)
    """
    return (scx - gcx, scy - gcy)


# ---------------------------------------------------------------------------
# Класс ViewController
# ---------------------------------------------------------------------------

class ViewController:
    """
    Управление видом базы CoC через ADB.

    Args:
        device_serial: серийный номер ADB-устройства
        screen_w:      ширина экрана BlueStacks в пикселях
        screen_h:      высота экрана BlueStacks в пикселях
        constants:     словарь констант из base_constants.json
        log_callback:  функция логирования (опционально)
    """

    def __init__(
        self,
        device_serial: str,
        screen_w: int,
        screen_h: int,
        constants: dict,
        log_callback: Optional[Callable] = None,
    ):
        self.device = device_serial
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.constants = constants or {}
        self.log = log_callback or (lambda msg: None)

        zoom_cfg = self.constants.get("zoom", {})
        self._pinch_step_px   = int(zoom_cfg.get("pinch_step_px", 150))
        self._pinch_duration  = int(zoom_cfg.get("pinch_duration_ms", 400))
        self._max_out_steps   = int(zoom_cfg.get("max_out_steps", 5))

        centering_cfg = self.constants.get("centering", {})
        self._center_tolerance = int(centering_cfg.get("center_tolerance_px", 20))
        self._edge_margin      = int(centering_cfg.get("edge_margin_px", 20))
        self._max_corrections  = int(centering_cfg.get("max_correction_attempts", 3))

        self._operation_timeout = 35.0  # секунды

    # ------------------------------------------------------------------
    # Публичный API — зум
    # ------------------------------------------------------------------

    def zoom_in(self) -> bool:
        """Приближение через Ctrl + scroll вверх."""
        try:
            from processes.SCENARIO.scenario_04_adb_actions import do_pinch
            do_pinch(self.device, zoom_in=True, seconds=1.0, log=self.log)
            self.log("🔍 Приближение выполнено")
            return True
        except Exception as e:
            self.log(f"❌ Ошибка приближения: {e}", )
            return False

    def zoom_out(self) -> bool:
        """Отдаление через Ctrl + scroll вниз."""
        try:
            from processes.SCENARIO.scenario_04_adb_actions import do_pinch
            do_pinch(self.device, zoom_in=False, seconds=1.0, log=self.log)
            self.log("🔎 Отдаление выполнено")
            return True
        except Exception as e:
            self.log(f"❌ Ошибка отдаления: {e}")
            return False

    def zoom_max_out(self) -> bool:
        """Максимальное отдаление."""
        self.log(f"🔎 Максимальное отдаление ({self._max_out_steps} шагов)...")
        try:
            from processes.SCENARIO.scenario_04_adb_actions import do_pinch
            do_pinch(self.device, zoom_in=False, seconds=self._max_out_steps * 0.8, log=self.log)
            return True
        except Exception as e:
            self.log(f"❌ Ошибка отдаления: {e}")
            return False

    # ------------------------------------------------------------------
    # Публичный API — центрирование
    # ------------------------------------------------------------------

    def center_on_point(self, cx: int, cy: int) -> bool:
        """
        Смещает вид так, чтобы точка (cx, cy) оказалась в центре экрана.

        Выполняет ADB swipe: от центра экрана к точке (cx, cy),
        что визуально перемещает содержимое в обратном направлении.

        Args:
            cx: X-координата целевой точки
            cy: Y-координата целевой точки

        Returns:
            True если swipe выполнен успешно.
        """
        scx, scy = self.screen_w // 2, self.screen_h // 2
        dx, dy = compute_centering_vector(cx, cy, scx, scy)

        if abs(dx) <= self._center_tolerance and abs(dy) <= self._center_tolerance:
            self.log("✅ База уже центрирована")
            return True

        # Swipe: начало в центре экрана, конец смещён на вектор
        x1, y1 = scx, scy
        x2, y2 = scx + dx, scy + dy

        try:
            result = subprocess.run(
                [_get_adb_path(), "-s", self.device, "shell", "input", "swipe",
                 str(x1), str(y1), str(x2), str(y2), "300"],
                capture_output=True, timeout=10,
            )
            if result.returncode == 0:
                self.log(f"🎯 Центрирование: свайп ({x1},{y1}) → ({x2},{y2})")
                return True
            else:
                self.log(f"❌ Ошибка свайпа, код: {result.returncode}")
                return False
        except Exception as e:
            self.log(f"❌ Исключение при свайпе: {e}")
            return False

    def find_and_center(self, screenshot_provider: Callable) -> bool:
        """
        Полная операция: отдал → скриншот → проверка экрана →
        обнаружение сетки → проверка границ → центрирование → повторный скриншот.

        Args:
            screenshot_provider: callable() → np.ndarray | None

        Returns:
            True если операция завершена успешно.
        """
        start_time = time.time()

        def _elapsed() -> float:
            return time.time() - start_time

        def _timeout() -> bool:
            if _elapsed() > self._operation_timeout:
                self.log("⏱ Таймаут операции (35 сек)")
                return True
            return False

        # Импортируем детекторы здесь, чтобы не создавать циклических зависимостей
        try:
            from processes.BASE_VIEW.base_01_screen_detector import ScreenDetector
            from processes.BASE_VIEW.base_02_grid_detector import GridDetector
        except ImportError:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
            from CORE.processes.BASE_VIEW.base_01_screen_detector import ScreenDetector
            from CORE.processes.BASE_VIEW.base_02_grid_detector import GridDetector

        screen_detector = ScreenDetector(log_callback=self.log)
        grid_detector   = GridDetector(self.constants, log_callback=self.log)

        # Шаг 1: максимальное отдаление
        self.log("🔎 Шаг 1: максимальное отдаление...")
        if _timeout():
            return False
        self.zoom_max_out()
        time.sleep(0.5)

        # Шаг 2: скриншот
        self.log("📸 Шаг 2: получение скриншота...")
        if _timeout():
            return False
        frame = screenshot_provider()
        if frame is None:
            self.log("❌ Скриншот вернул None, операция прервана")
            return False

        # Шаг 3: проверка главного экрана
        self.log("🔍 Шаг 3: проверка главного экрана...")
        if _timeout():
            return False
        is_main, screen_type, confidence = screen_detector.detect_screen_type(frame)
        if not is_main:
            self.log(f"⚠ Возможно не главный экран (тип='{screen_type}', confidence={confidence:.2f}), продолжаем...")
        else:
            self.log(f"✅ Главный экран подтверждён (confidence={confidence:.2f})")

        # Шаг 4: обнаружение сетки
        self.log("🔍 Шаг 4: обнаружение сетки базы...")
        if _timeout():
            return False
        grid_result = grid_detector.detect_grid_diamond(frame)
        if grid_result is None:
            self.log("⚠ Сетка не обнаружена, операция прервана")
            return False
        self.log(f"✅ Сетка найдена, центр: {grid_result['center']}, confidence={grid_result['confidence']:.2f}")

        # Шаг 5: проверка границ ромба
        self.log("🔍 Шаг 5: проверка границ ромба...")
        if _timeout():
            return False
        for attempt in range(self._max_corrections):
            if _timeout():
                return False
            out_of_bounds = self._check_diamond_bounds(grid_result)
            if not out_of_bounds:
                break
            self.log(f"⚠ Угол ромба выходит за границы, корректировка {attempt + 1}...")
            gcx, gcy = grid_result["center"]
            self.center_on_point(gcx, gcy)
            time.sleep(0.5)
            frame = screenshot_provider()
            if frame is None:
                self.log("❌ Скриншот вернул None при корректировке")
                return False
            grid_result = grid_detector.detect_grid_diamond(frame)
            if grid_result is None:
                self.log("⚠ Сетка потеряна при корректировке")
                return False

        # Шаг 6: центрирование
        self.log("🎯 Шаг 6: центрирование вида...")
        if _timeout():
            return False
        gcx, gcy = grid_result["center"]
        self.center_on_point(gcx, gcy)
        time.sleep(0.5)

        # Шаг 7: повторный скриншот
        self.log("📸 Шаг 7: повторный скриншот...")
        if _timeout():
            return False
        final_frame = screenshot_provider()
        if final_frame is None:
            self.log("⚠ Повторный скриншот вернул None")
        else:
            self.log("✅ Операция центрирования завершена успешно")

        return True

    # ------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------

    def _check_diamond_bounds(self, grid_result: dict) -> bool:
        """
        Проверяет, что все 4 угла ромба находятся внутри экрана с отступом.

        Returns:
            True если хотя бы один угол выходит за границы (нужна корректировка).
        """
        margin = self._edge_margin
        for key in ("top", "bottom", "left", "right"):
            pt = grid_result.get(key)
            if pt is None:
                continue
            x, y = pt
            if (x < margin or x >= self.screen_w - margin or
                    y < margin or y >= self.screen_h - margin):
                return True
        return False

    def _run_pinch(
        self,
        x1_start: int, y1_start: int, x1_end: int, y1_end: int,
        x2_start: int, y2_start: int, x2_end: int, y2_end: int,
    ) -> bool:
        """
        Выполняет pinch-жест через два последовательных ADB swipe.

        Стандартный `adb shell input swipe` не поддерживает мультитач,
        поэтому выполняем два swipe с минимальной задержкой.
        """
        dur = str(self._pinch_duration)
        adb = _get_adb_path()

        try:
            r1 = subprocess.run(
                [adb, "-s", self.device, "shell", "input", "swipe",
                 str(x1_start), str(y1_start), str(x1_end), str(y1_end), dur],
                capture_output=True, timeout=10,
            )
            r2 = subprocess.run(
                [adb, "-s", self.device, "shell", "input", "swipe",
                 str(x2_start), str(y2_start), str(x2_end), str(y2_end), dur],
                capture_output=True, timeout=10,
            )
            if r1.returncode != 0:
                self.log(f"❌ Pinch swipe 1 ошибка, код: {r1.returncode}")
                return False
            if r2.returncode != 0:
                self.log(f"❌ Pinch swipe 2 ошибка, код: {r2.returncode}")
                return False
            return True
        except Exception as e:
            self.log(f"❌ Исключение при pinch: {e}")
            return False
