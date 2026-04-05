#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI/tabs/tab_about.py — Вкладка О ПРОГРАММЕ"""

import tkinter as tk
from ..theme import THEME
from ..widgets import create_label, create_separator


def build(app):
    frame = app.frames["about"]

    center = tk.Frame(frame, bg=THEME["bg_main"])
    center.place(relx=0.5, rely=0.5, anchor="center")

    create_label(center, "⚡ MyBotX", style="title", bg=THEME["bg_main"]).pack(pady=(0, 4))
    create_label(center, "v3.0.0", style="header", bg=THEME["bg_main"]).pack()
    create_separator(center).pack(fill=tk.X, pady=16)

    for label, value in [
        ("Игра",     "Clash of Clans"),
        ("Эмулятор", "BlueStacks 5"),
        ("Язык",     "Python 3.10+"),
        ("Лицензия", "MIT"),
        ("Автор",    "Mihasa"),
    ]:
        row = tk.Frame(center, bg=THEME["bg_main"])
        row.pack(fill=tk.X, pady=3)
        create_label(row, f"{label}:", style="dim",
                     bg=THEME["bg_main"], width=12, anchor="e").pack(side=tk.LEFT)
        create_label(row, value, style="normal",
                     bg=THEME["bg_main"]).pack(side=tk.LEFT, padx=8)
