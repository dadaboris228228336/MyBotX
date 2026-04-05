#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCENARIO/scenario_02_steps.py
Определения типов шагов: названия, ключи, параметры по умолчанию.
"""

STEP_TYPES = [
    "Найти паттерн и нажать",
    "Нажать по координатам",
    "Свайп",
    "Отдалить (pinch out)",
    "Приблизить (pinch in)",
    "Кнопка HOME",
    "Кнопка BACK",
    "Ввод текста",
    "Запустить приложение",
    "Закрыть приложение",
    "Подождать",
]

STEP_TYPE_KEYS = {
    "Найти паттерн и нажать": "find_and_tap",
    "Нажать по координатам":  "tap_coords",
    "Свайп":                  "swipe",
    "Отдалить (pinch out)":   "pinch_out",
    "Приблизить (pinch in)":  "pinch_in",
    "Кнопка HOME":            "key_home",
    "Кнопка BACK":            "key_back",
    "Ввод текста":            "input_text",
    "Запустить приложение":   "launch_app",
    "Закрыть приложение":     "stop_app",
    "Подождать":              "wait",
}

STEP_KEY_LABELS = {v: k for k, v in STEP_TYPE_KEYS.items()}

# Параметры по умолчанию для каждого типа шага
STEP_DEFAULTS = {
    "find_and_tap": {"pattern": "", "threshold": 0.8, "retries": 3, "retry_delay": 2.0},
    "tap_coords":   {"x": 540, "y": 960},
    "swipe":        {"x1": 300, "y1": 960, "x2": 780, "y2": 960, "duration": 300},
    "pinch_out":    {"times": 3},
    "pinch_in":     {"times": 3},
    "key_home":     {},
    "key_back":     {},
    "input_text":   {"text": ""},
    "launch_app":   {"package": "com.supercell.clashofclans"},
    "stop_app":     {"package": "com.supercell.clashofclans"},
    "wait":         {"seconds": 2.0},
}


def step_label(step: dict) -> str:
    """Возвращает читаемое описание шага для отображения в списке."""
    t = step.get("type", "")
    p = step.get("params", {})
    label = STEP_KEY_LABELS.get(t, t)

    if t == "find_and_tap":
        return f"{label}: {p.get('pattern', '?')} (x{p.get('retries', 1)})"
    elif t == "tap_coords":
        return f"{label}: ({p.get('x')}, {p.get('y')})"
    elif t == "swipe":
        return f"{label}: ({p.get('x1')},{p.get('y1')})→({p.get('x2')},{p.get('y2')})"
    elif t in ("pinch_out", "pinch_in"):
        return f"{label} x{p.get('times', 1)}"
    elif t in ("launch_app", "stop_app"):
        pkg = p.get("package", "")
        return f"{label}: {pkg.split('.')[-1]}"
    elif t == "input_text":
        return f"{label}: {str(p.get('text', ''))[:20]}"
    elif t == "wait":
        return f"{label}: {p.get('seconds')}с"
    return label
