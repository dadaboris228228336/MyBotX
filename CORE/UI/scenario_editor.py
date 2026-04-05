#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/scenario_editor.py - Редактор сценариев v2.0
Только UI. Логика в CORE/processes/SCENARIO/
"""

import threading
import tkinter as tk
import tkinter.simpledialog as sd
import tkinter.messagebox as mb
from pathlib import Path

from .theme import THEME
from .widgets import create_button, create_label, create_separator

try:
    from processes.SCENARIO import (
        STEP_TYPES, STEP_TYPE_KEYS, STEP_KEY_LABELS,
        step_label, ScenarioStorage, ScenarioRunner
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from processes.SCENARIO import (
        STEP_TYPES, STEP_TYPE_KEYS, STEP_KEY_LABELS,
        step_label, ScenarioStorage, ScenarioRunner
    )

PATTERNS_DIR = Path(__file__).parent.parent / "processes" / "BOT" / "patterns"


class ScenarioEditor(tk.Frame):
    """Редактор сценариев — встраивается во вкладку БОТ."""

    def __init__(self, parent, adb, log_callback):
        super().__init__(parent, bg=THEME["bg_main"])
        self.adb      = adb
        self.log      = log_callback
        self._steps   = []
        self._running = False
        self._current_scenario = ""
        ScenarioStorage.ensure_dir()
        self._build()

    # ── Построение UI ────────────────────────────────────────────────────────

    def _build(self):
        # ── Строка выбора сценария ──
        top = tk.Frame(self, bg=THEME["bg_panel"], pady=6)
        top.pack(fill=tk.X)

        create_label(top, "🎬 Сценарий:", style="dim",
                     bg=THEME["bg_panel"]).pack(side=tk.LEFT, padx=(8, 4))

        self._scenario_var = tk.StringVar()
        self._scenario_menu = tk.OptionMenu(top, self._scenario_var, "")
        self._scenario_menu.config(
            bg=THEME["bg_input"], fg=THEME["accent_blue"],
            font=THEME["font_normal"], relief=tk.FLAT,
            activebackground=THEME["bg_card"],
            highlightthickness=0, width=18,
        )
        self._scenario_menu["menu"].config(
            bg=THEME["bg_input"], fg=THEME["accent_blue"],
            font=THEME["font_normal"],
        )
        self._scenario_menu.pack(side=tk.LEFT, padx=4)

        create_button(top, "＋",  self._new_scenario,    width=3).pack(side=tk.LEFT, padx=1)
        create_button(top, "✏",   self._rename_scenario, width=3).pack(side=tk.LEFT, padx=1)
        create_button(top, "🗑",  self._delete_scenario, width=3).pack(side=tk.LEFT, padx=1)

        create_separator(self).pack(fill=tk.X)

        # ── Основная область: список шагов + панель редактирования ──
        body = tk.Frame(self, bg=THEME["bg_main"])
        body.pack(fill=tk.BOTH, expand=True)

        # Левая часть — список шагов
        left = tk.Frame(body, bg=THEME["bg_main"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        create_label(left, "Шаги:", style="dim",
                     bg=THEME["bg_main"]).pack(anchor="w", padx=4, pady=(4, 0))

        lb_wrap = tk.Frame(left, bg=THEME["bg_input"])
        lb_wrap.pack(fill=tk.BOTH, expand=True, padx=4)

        sb = tk.Scrollbar(lb_wrap)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._listbox = tk.Listbox(
            lb_wrap,
            bg=THEME["bg_input"], fg=THEME["text_primary"],
            font=THEME["font_log"], relief=tk.FLAT,
            selectbackground=THEME["accent_blue"],
            selectforeground=THEME["bg_main"],
            yscrollcommand=sb.set, activestyle="none",
        )
        self._listbox.pack(fill=tk.BOTH, expand=True)
        sb.config(command=self._listbox.yview)
        self._listbox.bind("<<ListboxSelect>>", lambda e: self._on_select())

        # Кнопки управления шагами
        btns = tk.Frame(left, bg=THEME["bg_main"])
        btns.pack(fill=tk.X, padx=4, pady=2)
        create_button(btns, "▲", self._move_up,     width=3).pack(side=tk.LEFT, padx=1)
        create_button(btns, "▼", self._move_down,   width=3).pack(side=tk.LEFT, padx=1)
        create_button(btns, "🗑", self._delete_step, width=3).pack(side=tk.LEFT, padx=1)

        # Правая часть — панель редактирования/добавления шага
        self._right = tk.Frame(body, bg=THEME["bg_panel"], width=270)
        self._right.pack(side=tk.LEFT, fill=tk.Y, padx=(4, 0))
        self._right.pack_propagate(False)

        self._panel_title = create_label(
            self._right, "Добавить шаг:", style="dim", bg=THEME["bg_panel"]
        )
        self._panel_title.pack(anchor="w", padx=8, pady=(6, 2))

        # Тип шага
        self._step_type_var = tk.StringVar(value=STEP_TYPES[0])
        self._type_menu = tk.OptionMenu(self._right, self._step_type_var, *STEP_TYPES)
        self._type_menu.config(
            bg=THEME["bg_input"], fg=THEME["accent_blue"],
            font=THEME["font_small"], relief=tk.FLAT,
            activebackground=THEME["bg_card"],
            highlightthickness=0, width=26,
        )
        self._type_menu["menu"].config(
            bg=THEME["bg_input"], fg=THEME["accent_blue"],
            font=THEME["font_small"],
        )
        self._type_menu.pack(padx=8, pady=2, fill=tk.X)
        self._step_type_var.trace_add("write", lambda *_: self._refresh_params())

        # Динамические параметры
        self._params_frame = tk.Frame(self._right, bg=THEME["bg_panel"])
        self._params_frame.pack(fill=tk.X, padx=8, pady=4)
        self._param_vars = {}

        # Кнопки действий
        self._action_btn = create_button(
            self._right, "＋ Добавить шаг", self._add_step,
            style="start", width=26
        )
        self._action_btn.pack(padx=8, pady=(4, 2))

        self._cancel_btn = create_button(
            self._right, "✖ Отмена", self._cancel_edit, width=26
        )
        # cancel скрыт по умолчанию
        self._editing_index = None

        self._refresh_params()

        # ── Нижняя панель ──
        create_separator(self).pack(fill=tk.X)
        bottom = tk.Frame(self, bg=THEME["bg_panel"], pady=6)
        bottom.pack(fill=tk.X)

        self._run_btn = create_button(
            bottom, "▶ Запустить", self._run_scenario, style="start", width=16
        )
        self._run_btn.pack(side=tk.LEFT, padx=8)
        create_button(bottom, "💾 Сохранить", self._save, width=14).pack(side=tk.LEFT, padx=4)

        # Загружаем список сценариев
        self._refresh_scenario_list()
        self._scenario_var.trace_add("write", lambda *_: self._on_scenario_change())

    # ── Параметры шага ───────────────────────────────────────────────────────

    def _refresh_params(self, values: dict = None):
        """Перестраивает форму параметров под выбранный тип шага."""
        for w in self._params_frame.winfo_children():
            w.destroy()
        self._param_vars = {}

        t = STEP_TYPE_KEYS.get(self._step_type_var.get(), "")

        def entry(label, key, default):
            row = tk.Frame(self._params_frame, bg=THEME["bg_panel"])
            row.pack(fill=tk.X, pady=1)
            create_label(row, label, style="dim", bg=THEME["bg_panel"]).pack(anchor="w")
            var = tk.StringVar(value=str(values.get(key, default) if values else default))
            tk.Entry(row, textvariable=var, width=24,
                     bg=THEME["bg_input"], fg=THEME["accent_blue"],
                     font=THEME["font_small"], relief=tk.FLAT,
                     insertbackground=THEME["accent_green"]).pack(fill=tk.X)
            self._param_vars[key] = var

        def pattern_selector(key):
            row = tk.Frame(self._params_frame, bg=THEME["bg_panel"])
            row.pack(fill=tk.X, pady=1)
            create_label(row, "Паттерн:", style="dim", bg=THEME["bg_panel"]).pack(anchor="w")
            patterns = [f.stem for f in PATTERNS_DIR.glob("*.png")] or ["(нет паттернов)"]
            current = (values or {}).get(key, patterns[0])
            if current not in patterns:
                patterns.insert(0, current)
            var = tk.StringVar(value=current)
            m = tk.OptionMenu(row, var, *patterns)
            m.config(bg=THEME["bg_input"], fg=THEME["accent_blue"],
                     font=THEME["font_small"], relief=tk.FLAT,
                     activebackground=THEME["bg_card"],
                     highlightthickness=0, width=22)
            m["menu"].config(bg=THEME["bg_input"], fg=THEME["accent_blue"],
                             font=THEME["font_small"])
            m.pack(fill=tk.X)
            self._param_vars[key] = var

        if t == "find_and_tap":
            pattern_selector("pattern")
            entry("Порог совпадения (0-1):", "threshold", 0.8)
            entry("Попыток:", "retries", 3)
            entry("Пауза между попытками (с):", "retry_delay", 2.0)
        elif t == "tap_coords":
            entry("X:", "x", 540)
            entry("Y:", "y", 960)
        elif t == "swipe":
            entry("X1:", "x1", 300); entry("Y1:", "y1", 960)
            entry("X2:", "x2", 780); entry("Y2:", "y2", 960)
            entry("Длительность (мс):", "duration", 300)
        elif t in ("pinch_out", "pinch_in"):
            entry("Количество раз:", "times", 3)
        elif t in ("launch_app", "stop_app"):
            entry("Package:", "package", "com.supercell.clashofclans")
        elif t == "input_text":
            entry("Текст:", "text", "")
        elif t == "wait":
            entry("Секунд:", "seconds", 2.0)
        else:
            create_label(self._params_frame, "Нет параметров",
                         style="dim", bg=THEME["bg_panel"]).pack()

    def _collect_params(self) -> dict | None:
        """Собирает параметры из формы. Возвращает None при ошибке."""
        t = STEP_TYPE_KEYS.get(self._step_type_var.get(), "")
        p = {}
        try:
            for key, var in self._param_vars.items():
                val = var.get()
                if key in ("x", "y", "x1", "y1", "x2", "y2", "duration", "times", "retries"):
                    p[key] = int(val)
                elif key in ("threshold", "retry_delay", "seconds"):
                    p[key] = float(val)
                else:
                    p[key] = val
        except ValueError as e:
            self.log(f"❌ Неверное значение: {e}", "error")
            return None
        return p

    # ── Управление шагами ────────────────────────────────────────────────────

    def _on_select(self):
        """Клик на шаг — загружаем его параметры в форму для редактирования."""
        i = self._get_selected()
        if i is None or i >= len(self._steps):
            return
        step = self._steps[i]
        t_key = step.get("type", "")
        t_label = STEP_KEY_LABELS.get(t_key, STEP_TYPES[0])
        p = step.get("params", {})

        self._editing_index = i
        self._step_type_var.set(t_label)
        self.after(60, lambda: self._refresh_params(p))
        self._panel_title.config(text=f"Редактировать шаг {i+1}:")
        self._action_btn.config(text="💾 Сохранить изменения",
                                command=self._save_edit)
        self._cancel_btn.pack(padx=8, pady=(0, 4))

    def _cancel_edit(self):
        """Отмена редактирования — возврат к режиму добавления."""
        self._editing_index = None
        self._listbox.selection_clear(0, tk.END)
        self._panel_title.config(text="Добавить шаг:")
        self._action_btn.config(text="＋ Добавить шаг", command=self._add_step)
        self._cancel_btn.pack_forget()
        self._refresh_params()

    def _add_step(self):
        t_key = STEP_TYPE_KEYS.get(self._step_type_var.get(), "")
        p = self._collect_params()
        if p is None:
            return
        self._steps.append({"type": t_key, "params": p})
        self._refresh_listbox()
        self.log(f"➕ Шаг добавлен: {self._step_type_var.get()}", "info")

    def _save_edit(self):
        i = self._editing_index
        if i is None:
            return
        t_key = STEP_TYPE_KEYS.get(self._step_type_var.get(), "")
        p = self._collect_params()
        if p is None:
            return
        self._steps[i] = {"type": t_key, "params": p}
        self._refresh_listbox()
        self._listbox.selection_set(i)
        self.log(f"✏ Шаг {i+1} обновлён", "info")
        self._cancel_edit()

    def _delete_step(self):
        i = self._get_selected()
        if i is None:
            self.log("⚠ Выберите шаг", "warning")
            return
        removed = self._steps.pop(i)
        self._refresh_listbox()
        self._cancel_edit()
        self.log(f"🗑 Удалён: {step_label(removed)}", "dim")

    def _move_up(self):
        i = self._get_selected()
        if i is None or i == 0:
            return
        self._steps[i-1], self._steps[i] = self._steps[i], self._steps[i-1]
        self._refresh_listbox()
        self._listbox.selection_set(i-1)

    def _move_down(self):
        i = self._get_selected()
        if i is None or i >= len(self._steps) - 1:
            return
        self._steps[i], self._steps[i+1] = self._steps[i+1], self._steps[i]
        self._refresh_listbox()
        self._listbox.selection_set(i+1)

    def _get_selected(self) -> int | None:
        sel = self._listbox.curselection()
        if not sel or not self._steps:
            return None
        return sel[0]

    def _refresh_listbox(self):
        self._listbox.delete(0, tk.END)
        if not self._steps:
            self._listbox.insert(tk.END, "  (нет шагов — добавьте первый)")
            return
        for i, s in enumerate(self._steps, 1):
            self._listbox.insert(tk.END, f"  {i}. {step_label(s)}")

    # ── Управление сценариями ────────────────────────────────────────────────

    def _refresh_scenario_list(self):
        menu = self._scenario_menu["menu"]
        menu.delete(0, tk.END)
        names = ScenarioStorage.list_scenarios()
        if names:
            for n in names:
                menu.add_command(label=n,
                                 command=lambda x=n: self._scenario_var.set(x))
            if not self._scenario_var.get() or \
               self._scenario_var.get() not in names:
                self._scenario_var.set(names[0])
        else:
            menu.add_command(label="(нет сценариев)", command=lambda: None)
            self._scenario_var.set("")

    def _on_scenario_change(self):
        name = self._scenario_var.get()
        if name:
            self._current_scenario = name
            self._steps = ScenarioStorage.load(name)
            self._refresh_listbox()
            self._cancel_edit()

    def _new_scenario(self):
        name = sd.askstring("Новый сценарий", "Имя сценария:", parent=self)
        if not name:
            return
        name = name.strip().replace(" ", "_")
        ScenarioStorage.create(name)
        self._refresh_scenario_list()
        self._scenario_var.set(name)
        self.log(f"✅ Создан сценарий: {name}", "success")

    def _rename_scenario(self):
        cur = self._scenario_var.get()
        if not cur:
            return
        new = sd.askstring("Переименовать", f"Новое имя для '{cur}':", parent=self)
        if not new:
            return
        new = new.strip().replace(" ", "_")
        ScenarioStorage.rename(cur, new)
        self._refresh_scenario_list()
        self._scenario_var.set(new)

    def _delete_scenario(self):
        cur = self._scenario_var.get()
        if not cur:
            return
        if not mb.askyesno("Удалить", f"Удалить сценарий '{cur}'?", parent=self):
            return
        ScenarioStorage.delete(cur)
        self._steps = []
        self._refresh_listbox()
        self._refresh_scenario_list()
        self.log(f"🗑 Удалён сценарий: {cur}", "dim")

    def _save(self):
        name = self._scenario_var.get()
        if not name:
            self.log("⚠ Сначала создайте сценарий", "warning")
            return
        ScenarioStorage.save(name, self._steps)
        self.log(f"💾 Сохранено: '{name}' ({len(self._steps)} шагов)", "success")

    # ── Запуск ───────────────────────────────────────────────────────────────

    def _run_scenario(self):
        if self._running:
            return
        if not self.adb.connected_device:
            self.log("❌ Устройство не подключено. Нажмите СТАРТ сначала.", "error")
            return
        if not self._steps:
            self.log("⚠ Сценарий пуст", "warning")
            return

        self._running = True
        self._run_btn.config(text="⏳ Выполняется...",
                             state=tk.DISABLED, fg=THEME["text_disabled"])

        def _thread():
            runner = ScenarioRunner(self._steps, self.adb.connected_device, self.log)
            runner.run()
            self.after(0, self._on_run_done)

        threading.Thread(target=_thread, daemon=True).start()

    def _on_run_done(self):
        self._running = False
        self._run_btn.config(text="▶ Запустить",
                             state=tk.NORMAL, fg=THEME["btn_start_fg"])

    # ── Публичный API ────────────────────────────────────────────────────────

    def add_find_and_tap_step(self, pattern_name: str):
        """Добавляет шаг find_and_tap из внешнего кода (crop window)."""
        self._steps.append({
            "type": "find_and_tap",
            "params": {"pattern": pattern_name, "threshold": 0.8,
                       "retries": 3, "retry_delay": 2.0}
        })
        self._refresh_listbox()
