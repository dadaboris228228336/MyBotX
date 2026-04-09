#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI/tabs/tab_settings.py — Вкладка НАСТРОЙКИ."""

import json
import types
import tkinter as tk
from pathlib import Path
from ..theme import THEME
from ..widgets import create_button, create_label, create_separator


def build(app):
    """Строит вкладку НАСТРОЙКИ и патчит _save_settings на app."""

    # ── monkey-patch _save_settings ─────────────────────────────────────
    def _save_settings(self):
        config_path = Path(__file__).parent.parent.parent.parent / "CONFIG" / "config.json"
        try:
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)

            config.setdefault("technical_config", {}).setdefault("adb_settings", {})
            config["technical_config"]["adb_settings"]["timeout"]  = float(self.cfg_timeout.get())
            config["technical_config"]["adb_settings"]["max_wait"] = int(self.cfg_max_wait.get())
            bs = config.setdefault("bluestacks", {})
            bs["path"]          = self.cfg_bs_path.get()
            bs["window_width"]  = int(self.cfg_bs_width.get())
            bs["window_height"] = int(self.cfg_bs_height.get())
            config["dev_mode"]  = self._dev_mode_var.get()

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            self.settings_status.config(text="✅ Настройки сохранены!", fg=THEME["accent_green"])
        except Exception as e:
            self.settings_status.config(text=f"❌ Ошибка: {e}", fg=THEME["accent_red"])

    app._save_settings = types.MethodType(_save_settings, app)

    # ── build widgets ────────────────────────────────────────────────────
    frame = app.frames["settings"]
    config_path = Path(__file__).parent.parent.parent.parent / "CONFIG" / "config.json"

    scroll = tk.Frame(frame, bg=THEME["bg_main"])
    scroll.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    create_label(scroll, "⚙️ Настройки MyBotX", style="header", bg=THEME["bg_main"]).pack(anchor="w", pady=(0, 10))
    create_separator(scroll).pack(fill=tk.X, pady=(0, 16))

    try:
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
    except Exception:
        config = {}

    adb_cfg = config.get("technical_config", {}).get("adb_settings", {})

    # ── ADB ──────────────────────────────────────────────────────────────
    create_label(scroll, "🔌 ADB", style="dim", bg=THEME["bg_main"]).pack(anchor="w", pady=(0, 4))

    row1 = tk.Frame(scroll, bg=THEME["bg_main"])
    row1.pack(fill=tk.X, pady=4)
    create_label(row1, "Таймаут порта (сек):", style="normal", bg=THEME["bg_main"], width=22, anchor="w").pack(side=tk.LEFT)
    app.cfg_timeout = tk.Entry(row1, bg=THEME["bg_input"], fg=THEME["accent_blue"],
                               font=THEME["font_normal"], relief=tk.FLAT, width=8,
                               insertbackground=THEME["accent_green"])
    app.cfg_timeout.insert(0, str(adb_cfg.get("timeout", 1.0)))
    app.cfg_timeout.pack(side=tk.LEFT, padx=8)

    row2 = tk.Frame(scroll, bg=THEME["bg_main"])
    row2.pack(fill=tk.X, pady=4)
    create_label(row2, "Макс. ожидание (сек):", style="normal", bg=THEME["bg_main"], width=22, anchor="w").pack(side=tk.LEFT)
    app.cfg_max_wait = tk.Entry(row2, bg=THEME["bg_input"], fg=THEME["accent_blue"],
                                font=THEME["font_normal"], relief=tk.FLAT, width=8,
                                insertbackground=THEME["accent_green"])
    app.cfg_max_wait.insert(0, str(adb_cfg.get("max_wait", 15)))
    app.cfg_max_wait.pack(side=tk.LEFT, padx=8)

    create_separator(scroll).pack(fill=tk.X, pady=12)

    # ── BlueStacks ───────────────────────────────────────────────────────
    create_label(scroll, "📱 BlueStacks", style="dim", bg=THEME["bg_main"]).pack(anchor="w", pady=(0, 4))

    bs_cfg  = config.get("bluestacks", {})
    bs_path = bs_cfg.get("path", "")
    row3 = tk.Frame(scroll, bg=THEME["bg_main"])
    row3.pack(fill=tk.X, pady=4)
    create_label(row3, "Путь к HD-Player.exe:", style="normal", bg=THEME["bg_main"], width=22, anchor="w").pack(side=tk.LEFT)
    app.cfg_bs_path = tk.Entry(row3, bg=THEME["bg_input"], fg=THEME["accent_blue"],
                               font=THEME["font_normal"], relief=tk.FLAT, width=40,
                               insertbackground=THEME["accent_green"])
    app.cfg_bs_path.insert(0, bs_path)
    app.cfg_bs_path.pack(side=tk.LEFT, padx=8)

    row_res = tk.Frame(scroll, bg=THEME["bg_main"])
    row_res.pack(fill=tk.X, pady=4)
    create_label(row_res, "Разрешение окна (px):", style="normal",
                 bg=THEME["bg_main"], width=22, anchor="w").pack(side=tk.LEFT)
    app.cfg_bs_width = tk.Entry(row_res, bg=THEME["bg_input"], fg=THEME["accent_blue"],
                                font=THEME["font_normal"], relief=tk.FLAT, width=7,
                                insertbackground=THEME["accent_green"])
    app.cfg_bs_width.insert(0, str(bs_cfg.get("window_width", 1280)))
    app.cfg_bs_width.pack(side=tk.LEFT, padx=(8, 2))
    create_label(row_res, "×", style="dim", bg=THEME["bg_main"]).pack(side=tk.LEFT)
    app.cfg_bs_height = tk.Entry(row_res, bg=THEME["bg_input"], fg=THEME["accent_blue"],
                                 font=THEME["font_normal"], relief=tk.FLAT, width=7,
                                 insertbackground=THEME["accent_green"])
    app.cfg_bs_height.insert(0, str(bs_cfg.get("window_height", 720)))
    app.cfg_bs_height.pack(side=tk.LEFT, padx=(2, 8))
    create_label(row_res, "Рекомендуется: 1280×720", style="dim",
                 bg=THEME["bg_main"]).pack(side=tk.LEFT)

    create_separator(scroll).pack(fill=tk.X, pady=12)

    # ── Бот ──────────────────────────────────────────────────────────────
    create_label(scroll, "🤖 Бот", style="dim", bg=THEME["bg_main"]).pack(anchor="w", pady=(0, 4))

    row4 = tk.Frame(scroll, bg=THEME["bg_main"])
    row4.pack(fill=tk.X, pady=4)
    create_label(row4, "Порог паттерна (0-1):", style="normal", bg=THEME["bg_main"], width=22, anchor="w").pack(side=tk.LEFT)
    app.cfg_threshold = tk.Entry(row4, bg=THEME["bg_input"], fg=THEME["accent_blue"],
                                 font=THEME["font_normal"], relief=tk.FLAT, width=8,
                                 insertbackground=THEME["accent_green"])
    app.cfg_threshold.insert(0, "0.8")
    app.cfg_threshold.pack(side=tk.LEFT, padx=8)

    row5 = tk.Frame(scroll, bg=THEME["bg_main"])
    row5.pack(fill=tk.X, pady=4)
    create_label(row5, "Пауза между действиями:", style="normal", bg=THEME["bg_main"], width=22, anchor="w").pack(side=tk.LEFT)
    app.cfg_action_delay = tk.Entry(row5, bg=THEME["bg_input"], fg=THEME["accent_blue"],
                                    font=THEME["font_normal"], relief=tk.FLAT, width=8,
                                    insertbackground=THEME["accent_green"])
    app.cfg_action_delay.insert(0, "1.0")
    app.cfg_action_delay.pack(side=tk.LEFT, padx=8)

    create_separator(scroll).pack(fill=tk.X, pady=12)

    # ── Dev Mode ─────────────────────────────────────────────────────────
    create_label(scroll, "🛠 Режим разработчика", style="dim", bg=THEME["bg_main"]).pack(anchor="w", pady=(0, 4))

    dev_row = tk.Frame(scroll, bg=THEME["bg_main"])
    dev_row.pack(fill=tk.X, pady=4)

    app._dev_mode_var = tk.BooleanVar(value=config.get("dev_mode", False))

    def _toggle_dev_mode():
        enabled = app._dev_mode_var.get()
        if enabled:
            app.tab_buttons["dev"].pack(side=tk.LEFT)
        else:
            app.tab_buttons["dev"].pack_forget()
            if hasattr(app, "_current_tab") and app._current_tab == "dev":
                app._switch_tab("settings")

    if config.get("dev_mode", False):
        app.tab_buttons["dev"].pack(side=tk.LEFT)

    dev_check = tk.Checkbutton(
        dev_row,
        text="Включить Dev Mode (редактирование констант базы)",
        variable=app._dev_mode_var,
        command=_toggle_dev_mode,
        bg=THEME["bg_main"],
        fg=THEME["accent_orange"],
        selectcolor=THEME["bg_input"],
        activebackground=THEME["bg_main"],
        activeforeground=THEME["accent_orange"],
        font=THEME["font_normal"],
        relief=tk.FLAT,
        cursor="hand2",
    )
    dev_check.pack(side=tk.LEFT)

    create_separator(scroll).pack(fill=tk.X, pady=12)

    create_button(scroll, "💾  Сохранить настройки",
                  command=app._save_settings, style="start", width=26).pack(anchor="w")

    app.settings_status = create_label(scroll, "", style="dim", bg=THEME["bg_main"])
    app.settings_status.pack(anchor="w", pady=6)
