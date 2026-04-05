#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/scenario_editor.py - Редактор сценариев v3.0
Без правой панели. Параметры шага задаются в диалоговом окне.
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


class StepDialog(tk.Toplevel):
    """Диалог добавления/редактирования шага сценария."""

    def __init__(self, parent, title="Добавить шаг", step=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=THEME["bg_panel"])
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        self._step = step  # None = новый шаг, dict = редактирование
        self._param_vars = {}
        self._build()
        self.transient(parent)
        self.wait_window()

    def _build(self):
        pad = {"padx": 16, "pady": 4}

        # Тип шага
        type_row = tk.Frame(self, bg=THEME["bg_panel"])
        type_row.pack(fill=tk.X, padx=16, pady=(12, 4))
        create_label(type_row, "Тип шага:", style="dim",
                     bg=THEME["bg_panel"]).pack(anchor="w")

        init_type = STEP_TYPES[0]
        if self._step:
            init_type = STEP_KEY_LABELS.get(self._step.get("type", ""), STEP_TYPES[0])

        self._type_var = tk.StringVar(value=init_type)
        m = tk.OptionMenu(type_row, self._type_var, *STEP_TYPES)
        m.config(bg=THEME["bg_input"], fg=THEME["accent_blue"],
                 font=THEME["font_normal"], relief=tk.FLAT,
                 activebackground=THEME["bg_card"],
                 highlightthickness=0, width=30)
        m["menu"].config(bg=THEME["bg_input"], fg=THEME["accent_blue"],
                         font=THEME["font_normal"])
        m.pack(fill=tk.X)

        create_separator(self).pack(fill=tk.X, padx=16, pady=6)

        # Динамические параметры
        self._params_frame = tk.Frame(self, bg=THEME["bg_panel"])
        self._params_frame.pack(fill=tk.X, padx=16)

        self._type_var.trace_add("write", lambda *_: self._refresh_params())
        self._refresh_params()

        # Кнопки
        btn_row = tk.Frame(self, bg=THEME["bg_panel"])
        btn_row.pack(fill=tk.X, padx=16, pady=(8, 12))
        create_button(btn_row, "✅ Сохранить", self._on_save,
                      style="start", width=18).pack(side=tk.LEFT)
        create_button(btn_row, "✖ Отмена", self.destroy,
                      width=12).pack(side=tk.LEFT, padx=8)

    def _refresh_params(self):
        for w in self._params_frame.winfo_children():
            w.destroy()
        self._param_vars = {}

        t = STEP_TYPE_KEYS.get(self._type_var.get(), "")
        p = self._step.get("params", {}) if self._step else {}

        def entry(label, key, default):
            row = tk.Frame(self._params_frame, bg=THEME["bg_panel"])
            row.pack(fill=tk.X, pady=2)
            create_label(row, label, style="dim",
                         bg=THEME["bg_panel"]).pack(anchor="w")
            var = tk.StringVar(value=str(p.get(key, default)))
            tk.Entry(row, textvariable=var, width=32,
                     bg=THEME["bg_input"], fg=THEME["accent_blue"],
                     font=THEME["font_normal"], relief=tk.FLAT,
                     insertbackground=THEME["accent_green"]).pack(fill=tk.X)
            self._param_vars[key] = var

        def pattern_selector(key):
            row = tk.Frame(self._params_frame, bg=THEME["bg_panel"])
            row.pack(fill=tk.X, pady=2)
            create_label(row, "Паттерн:", style="dim",
                         bg=THEME["bg_panel"]).pack(anchor="w")
            patterns = [f.stem for f in PATTERNS_DIR.glob("*.png")]
            if not patterns:
                patterns = ["(нет паттернов — вырежьте через Скриншот)"]
            current = p.get(key, patterns[0])
            if current not in patterns:
                patterns.insert(0, current)
            var = tk.StringVar(value=current)
            m = tk.OptionMenu(row, var, *patterns)
            m.config(bg=THEME["bg_input"], fg=THEME["accent_blue"],
                     font=THEME["font_normal"], relief=tk.FLAT,
                     activebackground=THEME["bg_card"],
                     highlightthickness=0, width=30)
            m["menu"].config(bg=THEME["bg_input"], fg=THEME["accent_blue"],
                             font=THEME["font_normal"])
            m.pack(fill=tk.X)
            self._param_vars[key] = var

        if t == "find_and_tap":
            pattern_selector("pattern")
            entry("Порог совпадения (0.0 - 1.0):", "threshold", 0.8)
            entry("Количество попыток:", "retries", 3)
            entry("Пауза между попытками (сек):", "retry_delay", 2.0)
        elif t == "tap_coords":
            entry("X:", "x", 640)
            entry("Y:", "y", 360)
        elif t == "swipe":
            entry("X1:", "x1", 200); entry("Y1:", "y1", 360)
            entry("X2:", "x2", 1000); entry("Y2:", "y2", 360)
            entry("Длительность (мс):", "duration", 300)
        elif t in ("pinch_out", "pinch_in"):
            entry("Количество раз:", "times", 3)
        elif t in ("launch_app", "stop_app"):
            entry("Package (com.xxx):", "package", "com.supercell.clashofclans")
        elif t == "input_text":
            entry("Текст:", "text", "")
        elif t == "wait":
            entry("Секунд:", "seconds", 2.0)
        else:
            create_label(self._params_frame, "Нет параметров для этого шага",
                         style="dim", bg=THEME["bg_panel"]).pack(pady=8)

    def _on_save(self):
        t = STEP_TYPE_KEYS.get(self._type_var.get(), "")
        p = {}
        try:
            for key, var in self._param_vars.items():
                val = var.get()
                if key in ("x", "y", "x1", "y1", "x2", "y2",
                           "duration", "times", "retries"):
                    p[key] = int(val)
                elif key in ("threshold", "retry_delay", "seconds"):
                    p[key] = float(val)
                else:
                    p[key] = val
        except ValueError as e:
            mb.showerror("Ошибка", f"Неверное значение: {e}", parent=self)
            return
        self.result = {"type": t, "params": p}
        self.destroy()


class ScenarioEditor(tk.Frame):
    """Редактор сценариев v3.0 — без правой панели."""

    def __init__(self, parent, adb, log_callback,
                 start_callback=None, is_connected=None):
        super().__init__(parent, bg=THEME["bg_main"])
        self.adb            = adb
        self.log            = log_callback
        self._start_cb      = start_callback   # fn() — запускает СТАРТ
        self._is_connected  = is_connected or (lambda: bool(adb.connected_device))
        self._steps         = []
        self._running       = False
        ScenarioStorage.ensure_dir()
        self._build()

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
            highlightthickness=0, width=20,
        )
        self._scenario_menu["menu"].config(
            bg=THEME["bg_input"], fg=THEME["accent_blue"],
            font=THEME["font_normal"],
        )
        self._scenario_menu.pack(side=tk.LEFT, padx=4)

        create_button(top, "＋ Новый",   self._new_scenario,    width=10).pack(side=tk.LEFT, padx=2)
        create_button(top, "✏ Переим.",  self._rename_scenario, width=10).pack(side=tk.LEFT, padx=2)
        create_button(top, "🗑 Удалить", self._delete_scenario, width=10).pack(side=tk.LEFT, padx=2)

        create_separator(self).pack(fill=tk.X)

        # ── Список шагов ──
        list_frame = tk.Frame(self, bg=THEME["bg_main"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        create_label(list_frame, "Шаги сценария:", style="dim",
                     bg=THEME["bg_main"]).pack(anchor="w")

        lb_wrap = tk.Frame(list_frame, bg=THEME["bg_input"])
        lb_wrap.pack(fill=tk.BOTH, expand=True)

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
        self._listbox.bind("<Double-Button-1>", lambda e: self._edit_step())

        # Кнопки управления шагами
        btns = tk.Frame(list_frame, bg=THEME["bg_main"])
        btns.pack(fill=tk.X, pady=(4, 0))

        create_button(btns, "＋ Добавить шаг", self._add_step,
                      style="start", width=18).pack(side=tk.LEFT, padx=(0, 4))
        create_button(btns, "✏ Изменить", self._edit_step,   width=12).pack(side=tk.LEFT, padx=2)
        create_button(btns, "▲", self._move_up,   width=3).pack(side=tk.LEFT, padx=1)
        create_button(btns, "▼", self._move_down, width=3).pack(side=tk.LEFT, padx=1)
        create_button(btns, "🗑", self._delete_step, width=3).pack(side=tk.LEFT, padx=1)

        # ── Нижняя панель ──
        create_separator(self).pack(fill=tk.X)
        bottom = tk.Frame(self, bg=THEME["bg_panel"], pady=6)
        bottom.pack(fill=tk.X)

        self._run_btn = create_button(
            bottom, "▶ Запустить", self._run_scenario,
            style="start", width=16
        )
        self._run_btn.pack(side=tk.LEFT, padx=8)
        create_button(bottom, "💾 Сохранить", self._save,
                      width=14).pack(side=tk.LEFT, padx=4)

        # Загружаем список сценариев
        self._refresh_scenario_list()
        self._scenario_var.trace_add("write", lambda *_: self._on_scenario_change())

    # ── Управление шагами ────────────────────────────────────────────────────

    def _add_step(self):
        dlg = StepDialog(self, title="Добавить шаг")
        if dlg.result:
            self._steps.append(dlg.result)
            self._refresh_listbox()
            self.log(f"➕ Шаг добавлен: {step_label(dlg.result)}", "info")

    def _edit_step(self):
        i = self._get_selected()
        if i is None:
            self.log("⚠ Выберите шаг для редактирования", "warning")
            return
        dlg = StepDialog(self, title=f"Редактировать шаг {i+1}",
                         step=self._steps[i])
        if dlg.result:
            self._steps[i] = dlg.result
            self._refresh_listbox()
            self._listbox.selection_set(i)
            self.log(f"✏ Шаг {i+1} обновлён: {step_label(dlg.result)}", "info")

    def _delete_step(self):
        i = self._get_selected()
        if i is None:
            self.log("⚠ Выберите шаг для удаления", "warning")
            return
        removed = self._steps.pop(i)
        self._refresh_listbox()
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

    def _get_selected(self):
        sel = self._listbox.curselection()
        if not sel or not self._steps:
            return None
        return sel[0]

    def _refresh_listbox(self):
        self._listbox.delete(0, tk.END)
        if not self._steps:
            self._listbox.insert(tk.END, "  (нет шагов — нажмите '＋ Добавить шаг')")
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
            if self._scenario_var.get() not in names:
                self._scenario_var.set(names[0])
        else:
            menu.add_command(label="(нет сценариев)", command=lambda: None)
            self._scenario_var.set("")

    def _on_scenario_change(self):
        name = self._scenario_var.get()
        if name:
            self._steps = ScenarioStorage.load(name)
            self._refresh_listbox()

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
        if not self._steps:
            self.log("⚠ Сценарий пуст", "warning")
            return

        # Если устройство не подключено — сначала запускаем СТАРТ
        if not self._is_connected():
            self.log("🔌 Устройство не подключено — запускаем СТАРТ...", "info")
            if self._start_cb:
                self._start_cb()
            # Ждём подключения (макс 30 сек)
            self._run_btn.config(text="⏳ Подключение...",
                                 state=tk.DISABLED, fg=THEME["text_disabled"])
            self.after(1000, self._wait_for_connection)
            return

        self._start_running()

    def _wait_for_connection(self, attempts: int = 0):
        """Ждёт подключения ADB после запуска СТАРТ (макс 30 попыток по 1 сек)."""
        if self._is_connected():
            self.log("✅ Устройство подключено — запускаем сценарий", "success")
            self._start_running()
            return
        if attempts >= 30:
            self.log("❌ Не удалось подключиться за 30 секунд", "error")
            self._on_run_done()
            return
        self.after(1000, lambda: self._wait_for_connection(attempts + 1))

    def _start_running(self):
        """Запускает выполнение шагов сценария."""
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

    def add_step_direct(self, step: dict):
        """Добавляет готовый шаг напрямую (из диалога после вырезки паттерна)."""
        self._steps.append(step)
        self._refresh_listbox()
