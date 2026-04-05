#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI/tabs/tab_check.py — Вкладка ПРОВЕРКА"""

import tkinter as tk
from tkinter import scrolledtext
from ..theme import THEME
from ..widgets import create_button, create_label


def build(app):
    """Строит вкладку ПРОВЕРКА. app = BotMainWindow."""
    frame = app.frames["check"]

    btn_row = tk.Frame(frame, bg=THEME["bg_main"])
    btn_row.pack(fill=tk.X, pady=(0, 8))

    app.check_btn = create_button(
        btn_row, "🔍  Проверить всё",
        command=app.on_check_button_click, width=22
    )
    app.check_btn.pack(side=tk.LEFT, padx=(0, 8))

    app.install_btn = create_button(
        btn_row, "📦  Установить пакеты",
        command=app.on_install_button_click, width=22
    )
    app.install_btn.pack(side=tk.LEFT, padx=(0, 8))
    app.install_btn.config(state=tk.DISABLED, fg=THEME["text_disabled"])

    app.uninstall_btn = create_button(
        btn_row, "🗑  Удалить пакеты",
        command=app.on_uninstall_button_click, style="danger", width=18
    )
    app.uninstall_btn.pack(side=tk.LEFT, padx=(0, 8))

    create_button(btn_row, "🗑  Очистить логи",
                  command=app.on_clear_logs, width=18).pack(side=tk.LEFT)
    create_button(btn_row, "📸  Скриншот",
                  command=app.on_screenshot, width=14).pack(side=tk.RIGHT, padx=(8, 0))

    # Статус-карточки
    cards = tk.Frame(frame, bg=THEME["bg_main"])
    cards.pack(fill=tk.X, pady=(0, 8))

    app.status_labels = {}
    for key, title, val in [
        ("packages",   "📦 Пакеты",     "—"),
        ("bluestacks", "🖥 BlueStacks",  "—"),
        ("path",       "📁 Путь",        "—"),
    ]:
        card = tk.Frame(cards, bg=THEME["bg_card"], padx=12, pady=8)
        card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        create_label(card, title, style="dim", bg=THEME["bg_card"]).pack(anchor="w")
        lbl = create_label(card, val, style="normal", bg=THEME["bg_card"])
        lbl.pack(anchor="w")
        app.status_labels[key] = lbl

    # Прогресс-бар
    app.progress_bar = tk.Frame(frame, bg=THEME["accent_blue"], height=2)
    app.progress_bar.pack(fill=tk.X, pady=(0, 8))
    app._progress_running = False

    # Лог
    log_frame = tk.Frame(frame, bg=THEME["bg_input"], padx=2, pady=2)
    log_frame.pack(fill=tk.BOTH, expand=True)

    app.log_text = scrolledtext.ScrolledText(
        log_frame, wrap=tk.WORD, font=THEME["font_log"],
        bg=THEME["bg_input"], fg=THEME["text_primary"],
        insertbackground=THEME["accent_green"],
        selectbackground=THEME["accent_blue"],
        relief=tk.FLAT, bd=0,
    )
    app.log_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
    for tag, color in [
        ("success", THEME["accent_green"]),
        ("error",   THEME["accent_red"]),
        ("warning", THEME["accent_orange"]),
        ("info",    THEME["accent_blue"]),
        ("dim",     THEME["text_secondary"]),
    ]:
        app.log_text.tag_config(tag, foreground=color)
