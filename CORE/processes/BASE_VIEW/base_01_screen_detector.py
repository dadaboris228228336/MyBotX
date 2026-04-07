"""
Screen_Detector — определение типа экрана Clash of Clans по скриншоту.

Алгоритм:
  1. HSV-гистограмма: анализ доли зелёного (трава) и синего (небо) пикселей.
  2. Детектирование признаков боя: красные полосы HP (насыщенный красный в HSV).
  3. Детектирование экрана загрузки: тёмный кадр (средняя яркость < порога).

Входные данные:  numpy array BGR (скриншот BlueStacks).
Выходные данные: (is_main: bool, confidence: float 0.0–1.0)
                 (is_main: bool, screen_type: str, confidence: float)
"""

import numpy as np

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

# Допустимые типы экрана
VALID_SCREEN_TYPES = frozenset({'main', 'loading', 'battle', 'menu', 'unknown'})

# HSV-диапазоны (OpenCV: H 0-179, S 0-255, V 0-255)
_GREEN_LOWER = np.array([35, 40, 40],  dtype=np.uint8)
_GREEN_UPPER = np.array([85, 255, 255], dtype=np.uint8)

_BLUE_LOWER  = np.array([90, 40, 80],  dtype=np.uint8)
_BLUE_UPPER  = np.array([130, 255, 255], dtype=np.uint8)

# Красный в HSV — два диапазона (оттенок оборачивается через 0)
_RED_LOWER1  = np.array([0,  120, 70],  dtype=np.uint8)
_RED_UPPER1  = np.array([10, 255, 255], dtype=np.uint8)
_RED_LOWER2  = np.array([160, 120, 70], dtype=np.uint8)
_RED_UPPER2  = np.array([179, 255, 255], dtype=np.uint8)

# Пороги классификации
_MAIN_GREEN_THRESHOLD  = 0.08   # доля зелёных пикселей для главного экрана
_MAIN_BLUE_THRESHOLD   = 0.05   # доля синих пикселей для главного экрана
_LOADING_DARK_THRESHOLD = 40    # средняя яркость (V-канал) для экрана загрузки
_BATTLE_RED_THRESHOLD  = 0.01   # доля красных пикселей для боя


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Ограничивает значение в диапазоне [lo, hi]."""
    return max(lo, min(hi, value))


class ScreenDetector:
    """
    Классификатор экрана Clash of Clans по скриншоту.

    Методы:
        is_main_screen(frame)    → (bool, float)
        detect_screen_type(frame) → (bool, str, float)
    """

    def __init__(self, log_callback=None):
        self.log = log_callback or (lambda msg: None)

    # ------------------------------------------------------------------
    # Публичный API
    # ------------------------------------------------------------------

    def is_main_screen(self, frame: np.ndarray) -> tuple:
        """
        Определяет, является ли скриншот главным экраном CoC.

        Args:
            frame: numpy array BGR скриншота.

        Returns:
            (is_main: bool, confidence: float)  confidence ∈ [0.0, 1.0]
        """
        is_main, _, confidence = self.detect_screen_type(frame)
        return is_main, confidence

    def detect_screen_type(self, frame: np.ndarray) -> tuple:
        """
        Расширенная классификация экрана.

        Args:
            frame: numpy array BGR скриншота.

        Returns:
            (is_main: bool, screen_type: str, confidence: float)
            screen_type строго из {'main', 'loading', 'battle', 'menu', 'unknown'}
        """
        try:
            result = self._classify(frame)
        except Exception as e:
            self.log(f"[ScreenDetector] Ошибка классификации: {e}")
            result = (False, 'unknown', 0.0)

        # Гарантируем корректность типов
        is_main, screen_type, confidence = result
        screen_type = screen_type if screen_type in VALID_SCREEN_TYPES else 'unknown'
        confidence = _clamp(float(confidence))
        return bool(is_main), screen_type, confidence

    # ------------------------------------------------------------------
    # Внутренняя логика
    # ------------------------------------------------------------------

    def _classify(self, frame: np.ndarray) -> tuple:
        """Основная логика классификации."""
        if not _CV2_AVAILABLE:
            return self._classify_no_cv2(frame)

        import cv2

        if frame is None or frame.size == 0:
            return False, 'unknown', 0.0

        # Приводим к uint8 BGR если нужно
        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)

        # Убеждаемся что 3 канала
        if frame.ndim == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif frame.shape[2] == 4:
            frame = frame[:, :, :3]

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        total_pixels = hsv.shape[0] * hsv.shape[1]

        if total_pixels == 0:
            return False, 'unknown', 0.0

        # --- Экран загрузки: тёмный кадр ---
        mean_v = float(np.mean(hsv[:, :, 2]))
        if mean_v < _LOADING_DARK_THRESHOLD:
            confidence = _clamp(1.0 - mean_v / _LOADING_DARK_THRESHOLD)
            return False, 'loading', confidence

        # --- Признаки боя: красные HP-полосы ---
        red_mask1 = cv2.inRange(hsv, _RED_LOWER1, _RED_UPPER1)
        red_mask2 = cv2.inRange(hsv, _RED_LOWER2, _RED_UPPER2)
        red_ratio = float(cv2.countNonZero(red_mask1 | red_mask2)) / total_pixels
        if red_ratio >= _BATTLE_RED_THRESHOLD:
            confidence = _clamp(red_ratio / 0.05)
            return False, 'battle', confidence

        # --- Главный экран: зелёный + синий ---
        green_mask = cv2.inRange(hsv, _GREEN_LOWER, _GREEN_UPPER)
        blue_mask  = cv2.inRange(hsv, _BLUE_LOWER,  _BLUE_UPPER)
        green_ratio = float(cv2.countNonZero(green_mask)) / total_pixels
        blue_ratio  = float(cv2.countNonZero(blue_mask))  / total_pixels

        if green_ratio >= _MAIN_GREEN_THRESHOLD and blue_ratio >= _MAIN_BLUE_THRESHOLD:
            # Confidence: насколько уверенно выше порогов
            g_score = _clamp(green_ratio / 0.30)
            b_score = _clamp(blue_ratio  / 0.20)
            confidence = _clamp((g_score + b_score) / 2.0)
            return True, 'main', confidence

        if green_ratio >= _MAIN_GREEN_THRESHOLD:
            confidence = _clamp(green_ratio / 0.30 * 0.6)
            return False, 'menu', confidence

        return False, 'unknown', 0.0

    def _classify_no_cv2(self, frame: np.ndarray) -> tuple:
        """Упрощённая классификация без OpenCV (только numpy)."""
        if frame is None or frame.size == 0:
            return False, 'unknown', 0.0

        if frame.ndim < 3 or frame.shape[2] < 3:
            return False, 'unknown', 0.0

        arr = frame.astype(np.float32)
        b, g, r = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        total = frame.shape[0] * frame.shape[1]

        # Тёмный кадр → загрузка
        mean_brightness = float(np.mean((r + g + b) / 3.0))
        if mean_brightness < _LOADING_DARK_THRESHOLD:
            return False, 'loading', _clamp(1.0 - mean_brightness / _LOADING_DARK_THRESHOLD)

        # Зелёный: G > R и G > B
        green_pixels = np.sum((g > r * 1.2) & (g > b * 1.2) & (g > 60))
        green_ratio = float(green_pixels) / total

        if green_ratio >= _MAIN_GREEN_THRESHOLD:
            confidence = _clamp(green_ratio / 0.30 * 0.8)
            return True, 'main', confidence

        return False, 'unknown', 0.0
