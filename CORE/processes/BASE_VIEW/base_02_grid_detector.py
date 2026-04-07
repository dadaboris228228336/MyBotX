"""
Grid_Detector — обнаружение изометрической сетки базы Clash of Clans.

Алгоритм:
  1. Конвертация в grayscale → Canny edge detection.
  2. cv2.HoughLinesP для поиска линий.
  3. Фильтрация по углу: 26–30° (правые диагонали) и 150–154° (левые диагонали).
  4. Кластеризация линий по направлению.
  5. Вычисление пересечений → Grid_Center как медиана пересечений.
  6. Если найдено менее 4 линий → вернуть None.

Входные данные:  numpy array BGR (скриншот BlueStacks).
Выходные данные:
  detect_grid        → (cx, cy, confidence) или None
  detect_grid_diamond → dict с ключами top/bottom/left/right/center/confidence или None
  visualize          → новый numpy array (НЕ мутирует оригинал)
"""

import numpy as np
from typing import Optional

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

# Минимальное количество линий для обнаружения сетки
_MIN_LINES = 4

# Параметры Canny
_CANNY_LOW = 50
_CANNY_HIGH = 150

# Параметры HoughLinesP
_HOUGH_RHO = 1
_HOUGH_THETA = np.pi / 180
_HOUGH_THRESHOLD = 50
_HOUGH_MIN_LINE_LEN = 40
_HOUGH_MAX_LINE_GAP = 10

# Цвета для визуализации (BGR)
_COLOR_RIGHT = (0, 255, 0)    # зелёный — правые диагонали (~27°)
_COLOR_LEFT  = (255, 0, 0)    # синий — левые диагонали (~153°)
_COLOR_CENTER = (0, 0, 255)   # красный — центр
_COLOR_DIAMOND = (0, 255, 255) # жёлтый — ромб


def _line_angle_deg(x1: int, y1: int, x2: int, y2: int) -> float:
    """Возвращает угол линии в градусах [0, 180)."""
    dx = x2 - x1
    dy = y2 - y1
    angle = np.degrees(np.arctan2(dy, dx)) % 180
    return float(angle)


def _line_intersection(l1, l2):
    """
    Вычисляет точку пересечения двух линий, заданных парами точек.
    l1 = (x1, y1, x2, y2), l2 = (x3, y3, x4, y4).
    Возвращает (x, y) или None если линии параллельны.
    """
    x1, y1, x2, y2 = l1
    x3, y3, x4, y4 = l2

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)
    return (x, y)


class GridDetector:
    """
    Детектор изометрической сетки базы Clash of Clans.

    Args:
        constants: словарь констант из base_constants.json
        log_callback: функция логирования (опционально)

    Методы:
        detect_grid(frame)         → (cx, cy, confidence) или None
        detect_grid_diamond(frame) → dict или None
        visualize(frame, result)   → новый numpy array
    """

    def __init__(self, constants: dict, log_callback=None):
        self.constants = constants or {}
        self.log = log_callback or (lambda msg: None)

        base = self.constants.get("base", {})
        self._angle_right = float(base.get("isometric_angle_right", 27.0))
        self._angle_left  = float(base.get("isometric_angle_left", 153.0))
        self._angle_tol   = float(base.get("angle_tolerance", 3.0))

    # ------------------------------------------------------------------
    # Публичный API
    # ------------------------------------------------------------------

    def detect_grid(self, frame: np.ndarray) -> Optional[tuple]:
        """
        Обнаруживает изометрическую сетку базы CoC.

        Args:
            frame: numpy array BGR скриншота.

        Returns:
            (cx, cy, confidence) где cx ∈ [0, width), cy ∈ [0, height),
            confidence ∈ [0.0, 1.0], или None если сетка не найдена.
        """
        try:
            return self._detect(frame)
        except Exception as e:
            self.log(f"[GridDetector] Ошибка detect_grid: {e}")
            return None

    def detect_grid_diamond(self, frame: np.ndarray) -> Optional[dict]:
        """
        Возвращает 4 угловые точки ромба сетки.

        Args:
            frame: numpy array BGR скриншота.

        Returns:
            {'top': (x,y), 'bottom': (x,y), 'left': (x,y), 'right': (x,y),
             'center': (cx, cy), 'confidence': float}
            или None если сетка не найдена.
        """
        try:
            return self._detect_diamond(frame)
        except Exception as e:
            self.log(f"[GridDetector] Ошибка detect_grid_diamond: {e}")
            return None

    def visualize(self, frame: np.ndarray, result) -> np.ndarray:
        """
        Рисует линии сетки и центр на копии кадра для превью.

        НЕ мутирует исходный кадр — работает на копии.

        Args:
            frame:  исходный numpy array BGR.
            result: результат detect_grid (кортеж) или detect_grid_diamond (dict).

        Returns:
            Новый numpy array с нанесённой визуализацией.
        """
        output = frame.copy()
        if not _CV2_AVAILABLE or result is None:
            return output

        try:
            import cv2

            if isinstance(result, dict):
                cx, cy = result.get("center", (None, None))
                if cx is not None:
                    cv2.circle(output, (int(cx), int(cy)), 8, _COLOR_CENTER, -1)
                    cv2.circle(output, (int(cx), int(cy)), 12, _COLOR_CENTER, 2)
                for key, color in [("top", _COLOR_DIAMOND), ("bottom", _COLOR_DIAMOND),
                                    ("left", _COLOR_DIAMOND), ("right", _COLOR_DIAMOND)]:
                    pt = result.get(key)
                    if pt is not None:
                        cv2.circle(output, (int(pt[0]), int(pt[1])), 6, color, -1)
                # Рисуем ромб
                pts_order = ["top", "right", "bottom", "left"]
                pts = [result.get(k) for k in pts_order if result.get(k) is not None]
                if len(pts) == 4:
                    pts_arr = np.array([[int(p[0]), int(p[1])] for p in pts], dtype=np.int32)
                    cv2.polylines(output, [pts_arr], isClosed=True, color=_COLOR_DIAMOND, thickness=2)

            elif isinstance(result, tuple) and len(result) == 3:
                cx, cy, _ = result
                cv2.circle(output, (int(cx), int(cy)), 8, _COLOR_CENTER, -1)
                cv2.circle(output, (int(cx), int(cy)), 12, _COLOR_CENTER, 2)

        except Exception as e:
            self.log(f"[GridDetector] Ошибка visualize: {e}")

        return output

    # ------------------------------------------------------------------
    # Внутренняя логика
    # ------------------------------------------------------------------

    def _prepare_frame(self, frame: np.ndarray):
        """Подготавливает кадр: проверка, конвертация в grayscale."""
        if not _CV2_AVAILABLE:
            return None
        import cv2

        if frame is None or frame.size == 0:
            return None

        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)

        if frame.ndim == 2:
            gray = frame
        elif frame.ndim == 3 and frame.shape[2] == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        elif frame.ndim == 3 and frame.shape[2] == 4:
            gray = cv2.cvtColor(frame[:, :, :3], cv2.COLOR_BGR2GRAY)
        else:
            return None

        return gray

    def _filter_lines(self, lines, height: int, width: int) -> tuple:
        """
        Фильтрует линии по углу: 26–30° (правые) и 150–154° (левые).

        Returns:
            (right_lines, left_lines) — два списка линий.
        """
        right_lines = []
        left_lines  = []

        r_lo = self._angle_right - self._angle_tol
        r_hi = self._angle_right + self._angle_tol
        l_lo = self._angle_left  - self._angle_tol
        l_hi = self._angle_left  + self._angle_tol

        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = _line_angle_deg(x1, y1, x2, y2)
            if r_lo <= angle <= r_hi:
                right_lines.append((x1, y1, x2, y2))
            elif l_lo <= angle <= l_hi:
                left_lines.append((x1, y1, x2, y2))

        return right_lines, left_lines

    def _compute_intersections(self, right_lines, left_lines, height: int, width: int) -> list:
        """Вычисляет пересечения правых и левых линий, фильтруя по границам кадра."""
        intersections = []
        for rl in right_lines:
            for ll in left_lines:
                pt = _line_intersection(rl, ll)
                if pt is not None:
                    x, y = pt
                    if 0 <= x < width and 0 <= y < height:
                        intersections.append((x, y))
        return intersections

    def _detect(self, frame: np.ndarray) -> Optional[tuple]:
        """Основная логика обнаружения сетки."""
        import cv2

        gray = self._prepare_frame(frame)
        if gray is None:
            self.log("[GridDetector] Не удалось подготовить кадр")
            return None

        height, width = gray.shape

        # Canny
        edges = cv2.Canny(gray, _CANNY_LOW, _CANNY_HIGH)

        # HoughLinesP
        lines = cv2.HoughLinesP(
            edges,
            rho=_HOUGH_RHO,
            theta=_HOUGH_THETA,
            threshold=_HOUGH_THRESHOLD,
            minLineLength=_HOUGH_MIN_LINE_LEN,
            maxLineGap=_HOUGH_MAX_LINE_GAP,
        )

        if lines is None:
            self.log("[GridDetector] HoughLinesP не нашёл линий")
            return None

        right_lines, left_lines = self._filter_lines(lines, height, width)
        total_lines = len(right_lines) + len(left_lines)

        if total_lines < _MIN_LINES:
            self.log(f"[GridDetector] Найдено {total_lines} линий, нужно минимум {_MIN_LINES}")
            return None

        # Нужны хотя бы по одной линии каждого типа для пересечений
        if len(right_lines) == 0 or len(left_lines) == 0:
            self.log("[GridDetector] Нет линий одного из направлений")
            return None

        intersections = self._compute_intersections(right_lines, left_lines, height, width)

        if not intersections:
            self.log("[GridDetector] Нет пересечений в границах кадра")
            return None

        xs = [p[0] for p in intersections]
        ys = [p[1] for p in intersections]
        cx = int(np.median(xs))
        cy = int(np.median(ys))

        # Clamp в границы кадра
        cx = max(0, min(cx, width - 1))
        cy = max(0, min(cy, height - 1))

        # Confidence: нормализуем по количеству линий (насыщение при 20+)
        confidence = float(min(total_lines / 20.0, 1.0))

        return (cx, cy, confidence)

    def _detect_diamond(self, frame: np.ndarray) -> Optional[dict]:
        """Обнаруживает ромб сетки и возвращает 4 угловые точки."""
        import cv2

        gray = self._prepare_frame(frame)
        if gray is None:
            return None

        height, width = gray.shape

        edges = cv2.Canny(gray, _CANNY_LOW, _CANNY_HIGH)
        lines = cv2.HoughLinesP(
            edges,
            rho=_HOUGH_RHO,
            theta=_HOUGH_THETA,
            threshold=_HOUGH_THRESHOLD,
            minLineLength=_HOUGH_MIN_LINE_LEN,
            maxLineGap=_HOUGH_MAX_LINE_GAP,
        )

        if lines is None:
            return None

        right_lines, left_lines = self._filter_lines(lines, height, width)
        total_lines = len(right_lines) + len(left_lines)

        if total_lines < _MIN_LINES or len(right_lines) == 0 or len(left_lines) == 0:
            return None

        intersections = self._compute_intersections(right_lines, left_lines, height, width)
        if not intersections:
            return None

        xs = np.array([p[0] for p in intersections])
        ys = np.array([p[1] for p in intersections])

        cx = int(np.median(xs))
        cy = int(np.median(ys))
        cx = max(0, min(cx, width - 1))
        cy = max(0, min(cy, height - 1))

        # Угловые точки ромба: крайние пересечения по каждому направлению
        top    = intersections[int(np.argmin(ys))]
        bottom = intersections[int(np.argmax(ys))]
        left   = intersections[int(np.argmin(xs))]
        right  = intersections[int(np.argmax(xs))]

        confidence = float(min(total_lines / 20.0, 1.0))

        return {
            "top":        (int(top[0]),    int(top[1])),
            "bottom":     (int(bottom[0]), int(bottom[1])),
            "left":       (int(left[0]),   int(left[1])),
            "right":      (int(right[0]),  int(right[1])),
            "center":     (cx, cy),
            "confidence": confidence,
        }
