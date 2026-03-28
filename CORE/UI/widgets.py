#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 UI/widgets.py - Переиспользуемые виджеты в геймерском стиле
"""

import tkinter as tk
from .theme import THEME


def create_button(parent, text, command, style="normal", width=20):
    """Создать кнопку в геймерском стиле"""
    if style == "start":
        bg = THEME["btn_start_bg"]
        fg = THEME["btn_start_fg"]
        font = THEME["font_header"]
    elif style == "danger":
        bg = THEME["accent_red"]
        fg = THEME["text_primary"]
        font = THEME["font_normal"]
    else:
        bg = THEME["btn_normal_bg"]
        fg = THEME["accent_blue"]
        font = THEME["font_normal"]

    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        font=font,
        relief=tk.FLAT,
        cursor="hand2",
        width=width,
        pady=8,
        activebackground=THEME["btn_hover_bg"],
        activeforeground=fg,
        bd=0,
    )

    # Эффект при наведении
    def on_enter(e):
        btn.config(bg=THEME["btn_hover_bg"] if style != "start" else "#00cc70")

    def on_leave(e):
        btn.config(bg=bg)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn


def create_label(parent, text, style="normal", **kwargs):
    """Создать метку в геймерском стиле"""
    colors = {
        "title":   (THEME["accent_purple"], THEME["font_title"]),
        "header":  (THEME["accent_blue"],   THEME["font_header"]),
        "success": (THEME["accent_green"],  THEME["font_normal"]),
        "error":   (THEME["accent_red"],    THEME["font_normal"]),
        "warning": (THEME["accent_orange"], THEME["font_normal"]),
        "normal":  (THEME["text_primary"],  THEME["font_normal"]),
        "dim":     (THEME["text_secondary"],THEME["font_small"]),
    }
    fg, font = colors.get(style, colors["normal"])

    return tk.Label(
        parent,
        text=text,
        fg=fg,
        bg=kwargs.pop("bg", THEME["bg_panel"]),
        font=font,
        **kwargs
    )


def create_frame(parent, bg=None):
    """Создать фрейм в геймерском стиле"""
    return tk.Frame(
        parent,
        bg=bg or THEME["bg_panel"],
        bd=0,
    )


def create_separator(parent):
    """Горизонтальный разделитель"""
    return tk.Frame(
        parent,
        bg=THEME["accent_blue"],
        height=1,
    )
