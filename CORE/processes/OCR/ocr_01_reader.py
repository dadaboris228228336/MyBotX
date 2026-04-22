#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔤 OCR/ocr_01_reader.py
Единственная ответственность: распознавание текста через easyocr.
Не импортирует cv2, subprocess или ADB-модули.
"""

import numpy as np


class OCRReader:
    """Распознавание текста на изображении через easyocr."""

    def __init__(self, log_callback=None, gpu: bool = False):
        self.log = log_callback or print
        self._reader = None
        self._gpu = gpu
        self._init_reader()

    def _init_reader(self):
        """Инициализирует easyocr reader один раз."""
        try:
            import easyocr
            self._reader = easyocr.Reader(['en'], gpu=self._gpu, verbose=False)
            self.log("✅ OCR reader инициализирован")
        except ImportError:
            raise ImportError(
                "easyocr не установлен. Выполните: pip install easyocr"
            )
        except Exception as e:
            self.log(f"❌ Ошибка инициализации OCR: {e}")
            self._reader = None

    def read_text(self, img: np.ndarray) -> list[str]:
        """
        Распознаёт текст на изображении.

        Args:
            img: BGR numpy array (регион скриншота)

        Returns:
            список распознанных строк
        """
        if self._reader is None:
            self.log("❌ OCR reader не инициализирован")
            return []

        try:
            # easyocr ожидает RGB
            rgb = img[:, :, ::-1] if len(img.shape) == 3 else img
            results = self._reader.readtext(rgb, detail=1)
            texts = [text for (_, text, conf) in results if conf > 0.0]
            self.log(f"🔤 OCR распознал: {texts}")
            return texts
        except Exception as e:
            self.log(f"❌ Ошибка OCR: {e}")
            return []

    def read_text_with_confidence(self, img: np.ndarray) -> list[tuple]:
        """
        Распознаёт текст с оценкой уверенности.

        Returns:
            список (text, confidence) кортежей
        """
        if self._reader is None:
            return []
        try:
            rgb = img[:, :, ::-1] if len(img.shape) == 3 else img
            results = self._reader.readtext(rgb, detail=1)
            return [(text, conf) for (_, text, conf) in results]
        except Exception as e:
            self.log(f"❌ Ошибка OCR: {e}")
            return []
