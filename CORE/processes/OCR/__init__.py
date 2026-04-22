"""
OCR — распознавание текста через easyocr + парсинг чисел и таймеров.
"""
from .ocr_01_reader import OCRReader
from .ocr_02_parse_number import parse_number
from .ocr_03_parse_timer import parse_timer

__all__ = ["OCRReader", "parse_number", "parse_timer"]
