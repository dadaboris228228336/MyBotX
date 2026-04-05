#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI/tabs/tab_main.py — Вкладка ОСНОВНОЕ"""

import tkinter as tk
from ..theme import THEME
from ..widgets import create_button, create_label


def build(app):
    """Строит вкладку ОСНОВНОЕ. app = BotMainWindow."""
    frame = app.frames["main"]

    center = tk.Frame(frame, bg=THEME["bg_main"])
    center.place(relx=0.5, rely=0.5, anchor="center")

    create_label(center, "⚡ MyBotX", style="title", bg=THEME["bg_main"]).pack(pady=(0, 5))
    create_label(center, "Clash of Clans Automation Bot", style="dim",
                 bg=THEME["bg_main"]).pack(pady=(0, 30))

    app.start_btn = create_button(
        center, text="▶   СТАРТ",
        command=app.on_start_bot, style="start", width=25
    )
    app.start_btn.pack(pady=10, ipady=6)

    app.statusbar = create_label(
        center, text="Готов к запуску", style="dim", bg=THEME["bg_main"]
    )
    app.statusbar.pack(pady=(15, 0))

    # Статистика внизу
    stats = tk.Frame(frame, bg=THEME["bg_panel"])
    stats.pack(side=tk.BOTTOM, fill=tk.X)

    app.stats_labels = {}
    for text, val in [("BlueStacks", "—"), ("ADB", "—"), ("Игра", "—")]:
        col = tk.Frame(stats, bg=THEME["bg_panel"])
        col.pack(side=tk.LEFT, expand=True, pady=10)
        create_label(col, text, style="dim", bg=THEME["bg_panel"]).pack()
        lbl = create_label(col, val, style="normal", bg=THEME["bg_panel"])
        lbl.pack()
        app.stats_labels[text] = lbl
