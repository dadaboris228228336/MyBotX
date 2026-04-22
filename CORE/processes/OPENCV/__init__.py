"""
OPENCV — обработка изображений через OpenCV.
"""
from .cv_01_template_match import TemplateMatch
from .cv_02_image_utils import resize, to_grayscale, threshold, scale_up

__all__ = ["TemplateMatch", "resize", "to_grayscale", "threshold", "scale_up"]
