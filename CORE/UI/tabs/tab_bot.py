#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI/tabs/tab_bot.py — Вкладка БОТ"""

import tkinter as tk
from tkinter import scrolledtext
from ..theme import THEME
from ..widgets import create_button, create_label
from ..scenario_editor import ScenarioEditor


def build(app):
    """Строит вкладку БОТ. app = BotMainWindow."""
    frame = app.frames["bot"]

    # Верхняя панель: скриншот + вырезать паттерн
    top_row = tk.Frame(frame, bg=THEME["bg_main"])
    top_row.pack(fill=tk.X, pady=(0, 4))

    create_button(top_row, "📸 Скриншот",
                  app._bot_screenshot,   width=18).pack(side=tk.LEFT, padx=(0, 6))
    create_button(top_row, "✂️ Вырезать паттерн",
                  app._bot_crop_pattern, width=20).pack(side=tk.LEFT)

    # Превью + лог рядом
    preview_row = tk.Frame(frame, bg=THEME["bg_main"])
    preview_row.pack(fill=tk.X, pady=(0, 4))

    # Превью (слева)
    preview_frame = tk.Frame(preview_row, bg=THEME["bg_card"], height=140, width=420)
    preview_frame.pack(side=tk.LEFT, fill=tk.Y)
    preview_frame.pack_propagate(False)

    app.bot_preview_label = tk.Label(
        preview_frame,
        text="📸 Скриншот появится здесь",
        bg=THEME["bg_card"], fg=THEME["text_secondary"],
        font=THEME["font_normal"]
    )
    app.bot_preview_label.pack(expand=True)

    # Лог (справа)
    log_frame = tk.Frame(preview_row, bg=THEME["bg_input"])
    log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

    create_label(log_frame, "📋 Лог:", style="dim",
                 bg=THEME["bg_input"]).pack(anchor="w", padx=4, pady=(2, 0))

    app.bot_log = scrolledtext.ScrolledText(
        log_frame, wrap=tk.WORD, font=THEME["font_log"],
        bg=THEME["bg_input"], fg=THEME["text_primary"],
        relief=tk.FLAT, bd=0, height=8,
    )
    app.bot_log.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    for tag, color in [
        ("success", THEME["accent_green"]),
        ("error",   THEME["accent_red"]),
        ("warning", THEME["accent_orange"]),
        ("info",    THEME["accent_blue"]),
        ("dim",     THEME["text_secondary"]),
    ]:
        app.bot_log.tag_config(tag, foreground=color)

    # Редактор сценариев
    app._scenario_editor = ScenarioEditor(
        frame, app.adb, app._bot_log,
        start_callback=app.on_start_bot,
        is_connected=lambda: bool(app.adb.connected_device)
    )
    app._scenario_editor.pack(fill=tk.BOTH, expand=True)
