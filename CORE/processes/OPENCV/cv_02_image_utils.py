#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🖼️ OPENCV/cv_02_image_utils.py
Утилиты для обработки изображений через OpenCV.
Используется модулями OCR и OPENCV для препроцессинга.
"""

import cv2
import numpy as np


def resize(img: np.ndarray, width: int, height: int) -> np.ndarray:
    """Масштабирует изображение до заданного размера."""
    return cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)


def to_grayscale(img: np.ndarray) -> np.ndarray:
    """Конвертирует BGR изображение в оттенки серого."""
    if len(img.shape) == 2:
        return img  # уже grayscale
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def threshold(img: np.ndarray, thresh_val: int = 0, max_val: int = 255) -> np.ndarray:
    """
    Применяет бинарный порог Otsu к grayscale изображению.
    thresh_val=0 означает автоматический выбор порога (Otsu).
    """
    gray = to_grayscale(img)
    _, result = cv2.threshold(gray, thresh_val, max_val, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return result


def scale_up(img: np.ndarray, min_dim: int = 32, factor: int = 2) -> np.ndarray:
    """
    Увеличивает изображение в factor раз если любая сторона меньше min_dim.
    Улучшает точность OCR на мелком тексте.
    """
    h, w = img.shape[:2]
    if h < min_dim or w < min_dim:
        return cv2.resize(img, (w * factor, h * factor), interpolation=cv2.INTER_CUBIC)
    return img
