#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI/tabs/tab_auto.py — Вкладка АВТО (автоматизация запуска и сценариев)."""

import json
import types
import tkinter as tk
from pathlib import Path
from ..theme import THEME
from ..widgets import create_button, create_label, create_separator


def build(app):
    """Строит вкладку АВТО и патчит get_auto_settings на app."""

    # ── monkey-patch get_auto_settings ──────────────────────────────────
    def get_auto_settings(self) -> dict:
        """Возвращает текущие настройки автоматизации."""
        return {k: v.get() for k, v in self._auto_vars.items()}

    app.get_auto_settings = types.MethodType(get_auto_settings, app)

    # ── build widgets ────────────────────────────────────────────────────
    frame = app.frames["auto"]
    config_path = Path(__file__).parent.parent.parent.parent / "CONFIG" / "config.json"

    def load_auto_cfg() -> dict:
        try:
            with open(config_path, encoding="utf-8") as f:
                return json.load(f).get("auto_settings", {})
        except Exception:
            return {}

    def save_auto_cfg():
        try:
            with open(config_path, encoding="utf-8") as f:
                cfg = json.load(f)
            cfg["auto_settings"] = {
                "minimize_bs":        app._auto_vars["minimize_bs"].get(),
                "minimize_bs_delay":  app._auto_bs_delay.get(),
                "minimize_bot":       app._auto_vars["minimize_bot"].get(),
                "minimize_bot_delay": app._auto_bot_delay.get(),
                "autorun_scenario":   app._auto_vars["autorun_scenario"].get(),
                "repeat_scenario":    app._auto_vars["repeat_scenario"].get(),
                "repeat_count":       app._auto_repeat_count.get(),
                "repeat_pause":       app._auto_vars["repeat_pause"].get(),
                "repeat_pause_secs":  app._auto_repeat_pause.get(),
                "notify_done":        app._auto_vars["notify_done"].get(),
                "verbose_log":        app._auto_vars["verbose_log"].get(),
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    saved = load_auto_cfg()

    scroll = tk.Frame(frame, bg=THEME["bg_main"])
    scroll.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    create_label(scroll, "⚡ Автоматизация", style="header", bg=THEME["bg_main"]).pack(anchor="w", pady=(0, 6))
    create_separator(scroll).pack(fill=tk.X, pady=(0, 14))

    app._auto_vars = {}

    def toggle_row(parent, key, title, description, extra_widget_fn=None):
        row = tk.Frame(parent, bg=THEME["bg_card"], padx=12, pady=10)
        row.pack(fill=tk.X, pady=4)

        var = tk.BooleanVar(value=saved.get(key, False))
        app._auto_vars[key] = var

        left = tk.Frame(row, bg=THEME["bg_card"])
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)

        create_label(left, title, style="normal", bg=THEME["bg_card"]).pack(anchor="w")
        create_label(left, description, style="dim", bg=THEME["bg_card"]).pack(anchor="w")

        if extra_widget_fn:
            extra_widget_fn(left, var)

        lbl = tk.Label(row, text="○ ВЫКЛ", fg=THEME["text_secondary"],
                       bg=THEME["bg_card"], font=THEME["font_normal"], cursor="hand2")
        lbl.pack(side=tk.RIGHT, padx=8)

        def refresh_lbl(v=var):
            lbl.config(text="● ВКЛ" if v.get() else "○ ВЫКЛ",
                       fg=THEME["accent_green"] if v.get() else THEME["text_secondary"])

        def on_click(e, v=var):
            v.set(not v.get())

        lbl.bind("<Button-1>", on_click)
        var.trace_add("write", lambda *_: (refresh_lbl(), save_auto_cfg()))
        refresh_lbl()

    # ── Переключатели ────────────────────────────────────────────────────

    def bs_delay_widget(parent, var):
        row2 = tk.Frame(parent, bg=THEME["bg_card"])
        row2.pack(anchor="w", pady=(4, 0))
        create_label(row2, "Через (сек):", style="dim", bg=THEME["bg_card"]).pack(side=tk.LEFT)
        app._auto_bs_delay = tk.StringVar(value=saved.get("minimize_bs_delay", "10"))
        e = tk.Entry(row2, textvariable=app._auto_bs_delay, width=6,
                     bg=THEME["bg_input"], fg=THEME["accent_blue"],
                     font=THEME["font_small"], relief=tk.FLAT,
                     insertbackground=THEME["accent_green"])
        e.pack(side=tk.LEFT, padx=6)
        e.bind("<FocusOut>", lambda _: save_auto_cfg())
        e.bind("<Return>",   lambda _: save_auto_cfg())

    toggle_row(scroll, "minimize_bs",
               "📱 Свернуть BlueStacks при запуске бота",
               "Автоматически сворачивает окно BlueStacks через N секунд после старта",
               bs_delay_widget)

    def bot_delay_widget(parent, var):
        row2 = tk.Frame(parent, bg=THEME["bg_card"])
        row2.pack(anchor="w", pady=(4, 0))
        create_label(row2, "Через (сек):", style="dim", bg=THEME["bg_card"]).pack(side=tk.LEFT)
        app._auto_bot_delay = tk.StringVar(value=saved.get("minimize_bot_delay", "15"))
        e = tk.Entry(row2, textvariable=app._auto_bot_delay, width=6,
                     bg=THEME["bg_input"], fg=THEME["accent_blue"],
                     font=THEME["font_small"], relief=tk.FLAT,
                     insertbackground=THEME["accent_green"])
        e.pack(side=tk.LEFT, padx=6)
        e.bind("<FocusOut>", lambda _: save_auto_cfg())
        e.bind("<Return>",   lambda _: save_auto_cfg())

    toggle_row(scroll, "minimize_bot",
               "🤖 Свернуть MyBotX при запуске бота",
               "Сворачивает окно MyBotX через N секунд после старта сценария",
               bot_delay_widget)

    toggle_row(scroll, "autorun_scenario",
               "▶ Автозапуск сценария при нажатии СТАРТ",
               "Сразу запускает активный сценарий после подключения к BlueStacks")

    def repeat_widget(parent, var):
        row2 = tk.Frame(parent, bg=THEME["bg_card"])
        row2.pack(anchor="w", pady=(4, 0))
        create_label(row2, "Повторов (0 = бесконечно):", style="dim", bg=THEME["bg_card"]).pack(side=tk.LEFT)
        app._auto_repeat_count = tk.StringVar(value=saved.get("repeat_count", "0"))
        e = tk.Entry(row2, textvariable=app._auto_repeat_count, width=6,
                     bg=THEME["bg_input"], fg=THEME["accent_blue"],
                     font=THEME["font_small"], relief=tk.FLAT,
                     insertbackground=THEME["accent_green"])
        e.pack(side=tk.LEFT, padx=6)
        e.bind("<FocusOut>", lambda _: save_auto_cfg())
        e.bind("<Return>",   lambda _: save_auto_cfg())

    toggle_row(scroll, "repeat_scenario",
               "🔁 Повторять сценарий",
               "После завершения сценарий запускается снова",
               repeat_widget)

    def pause_widget(parent, var):
        row2 = tk.Frame(parent, bg=THEME["bg_card"])
        row2.pack(anchor="w", pady=(4, 0))
        create_label(row2, "Пауза (сек):", style="dim", bg=THEME["bg_card"]).pack(side=tk.LEFT)
        app._auto_repeat_pause = tk.StringVar(value=saved.get("repeat_pause_secs", "5"))
        e = tk.Entry(row2, textvariable=app._auto_repeat_pause, width=6,
                     bg=THEME["bg_input"], fg=THEME["accent_blue"],
                     font=THEME["font_small"], relief=tk.FLAT,
                     insertbackground=THEME["accent_green"])
        e.pack(side=tk.LEFT, padx=6)
        e.bind("<FocusOut>", lambda _: save_auto_cfg())
        e.bind("<Return>",   lambda _: save_auto_cfg())

    toggle_row(scroll, "repeat_pause",
               "⏸ Пауза между повторами сценария",
               "Ждать N секунд перед следующим повтором",
               pause_widget)

    toggle_row(scroll, "notify_done",
               "🔔 Уведомление по завершении сценария",
               "Показывает системное уведомление Windows когда сценарий завершён")

    toggle_row(scroll, "verbose_log",
               "📋 Подробный лог каждого шага",
               "Выводить детальную информацию о каждом действии в лог")

    create_separator(scroll).pack(fill=tk.X, pady=12)
    create_label(scroll, "💡 Предложения: скриншот по расписанию, стоп по паттерну, "
                          "авто-рестарт при зависании BlueStacks",
                 style="dim", bg=THEME["bg_main"]).pack(anchor="w")
