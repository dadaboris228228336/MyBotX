#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 UI/theme.py - Геймерская цветовая схема и шрифты MyBotX
"""

THEME = {
    # Фоны
    "bg_main":        "#0d0d0d",   # Основной фон (почти чёрный)
    "bg_panel":       "#1a1a2e",   # Фон панелей (тёмно-синий)
    "bg_card":        "#16213e",   # Фон карточек
    "bg_input":       "#0f3460",   # Фон полей ввода/логов

    # Акценты
    "accent_green":   "#00ff88",   # Зелёный акцент (успех, СТАРТ)
    "accent_blue":    "#00d4ff",   # Синий акцент (инфо)
    "accent_red":     "#ff4757",   # Красный (ошибка)
    "accent_orange":  "#ffa502",   # Оранжевый (предупреждение)
    "accent_purple":  "#a855f7",   # Фиолетовый (заголовки)

    # Текст
    "text_primary":   "#e0e0e0",   # Основной текст
    "text_secondary": "#888888",   # Второстепенный текст
    "text_disabled":  "#444444",   # Отключённый текст

    # Кнопки
    "btn_start_bg":   "#00ff88",   # Фон кнопки СТАРТ
    "btn_start_fg":   "#0d0d0d",   # Текст кнопки СТАРТ
    "btn_normal_bg":  "#1a1a2e",   # Фон обычной кнопки
    "btn_normal_fg":  "#00d4ff",   # Текст обычной кнопки
    "btn_hover_bg":   "#0f3460",   # Фон при наведении

    # Шрифты
    "font_title":     ("Consolas", 22, "bold"),
    "font_header":    ("Consolas", 12, "bold"),
    "font_normal":    ("Consolas", 10),
    "font_small":     ("Consolas", 9),
    "font_log":       ("Consolas", 9),

    # Размеры
    "border_radius":  8,
    "padding":        10,
}
