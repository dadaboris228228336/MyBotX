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
        step_label, ScenarioStorage, ScenarioRunner, PresetStorage
    )
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from processes.SCENARIO import (
        STEP_TYPES, STEP_TYPE_KEYS, STEP_KEY_LABELS,
        step_label, ScenarioStorage, ScenarioRunner, PresetStorage
    )

# GAP Req 6.1 / 6.2: The requirement says ScenarioEditor SHALL directly import
# BotActions (from CORE/processes/BOT/bot_04_actions.py) and BotTap
# (from CORE/processes/BOT/bot_03_tap.py). In the actual implementation these
# are used indirectly via scenario_04_adb_actions.py (do_find_and_tap, do_tap,
# do_swipe). The imports are absent here and in tab_bot.py.

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
            # Форматируем значение без лишних нулей: 2.0 → "2", 3.8 → "3.8"
            raw = p.get(key, default)
            try:
                fval = float(raw)
                display = str(int(fval)) if fval == int(fval) else str(fval)
            except Exception:
                display = str(raw)
            var = tk.StringVar(value=display)
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
            entry("Секунд (сколько крутить колёсико):", "seconds", 2.0)
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
            # GAP Req 2.8: validation errors shown via messagebox popup instead of BotLog.
            # Requirement says errors should be logged to BotLog (log_callback) with tag "error".
            # Note: StepDialog has no reference to log_callback; it would need to be passed in.
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
        self._stop_requested = False
        ScenarioStorage.ensure_dir()
        self._build()

    def _build(self):
        # ── Секция пресетов ──
        preset_bar = tk.Frame(self, bg=THEME["bg_card"], pady=4)
        preset_bar.pack(fill=tk.X)

        create_label(preset_bar, "📦 Пресеты:", style="dim",
                     bg=THEME["bg_card"]).pack(side=tk.LEFT, padx=(8, 4))

        self._preset_var = tk.StringVar()
        self._preset_menu = tk.OptionMenu(preset_bar, self._preset_var, "")
        self._preset_menu.config(
            bg=THEME["bg_input"], fg=THEME["accent_green"],
            font=THEME["font_normal"], relief=tk.FLAT,
            activebackground=THEME["bg_card"],
            highlightthickness=0, width=22,
        )
        self._preset_menu["menu"].config(
            bg=THEME["bg_input"], fg=THEME["accent_green"],
            font=THEME["font_normal"],
        )
        self._preset_menu.pack(side=tk.LEFT, padx=4)

        create_button(preset_bar, "📥 Загрузить", self._load_preset,
                      width=14).pack(side=tk.LEFT, padx=2)

        self._preset_dev_btn = create_button(
            preset_bar, "✏ Изм. пресет", self._edit_preset_dev,
            width=14
        )
        self._preset_dev_btn.pack(side=tk.LEFT, padx=2)

        self._preset_info = create_label(
            preset_bar, "", style="dim", bg=THEME["bg_card"]
        )
        self._preset_info.pack(side=tk.LEFT, padx=8)

        self._refresh_preset_list()
        self._preset_var.trace_add("write", lambda *_: self._on_preset_change())
        self._on_preset_change()

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

        # Drag & drop для перетаскивания шагов
        self._drag_start_index = None
        self._listbox.bind("<ButtonPress-1>",   self._on_drag_start)
        self._listbox.bind("<B1-Motion>",        self._on_drag_motion)
        self._listbox.bind("<ButtonRelease-1>",  self._on_drag_release)

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

        self._stop_btn = create_button(
            bottom, "⏹ Стоп", self._stop_scenario,
            style="danger", width=10
        )
        self._stop_btn.pack(side=tk.LEFT, padx=4)
        self._stop_btn.config(state=tk.DISABLED, fg=THEME["text_disabled"])

        create_button(bottom, "💾 Сохранить", self._save,
                      width=14).pack(side=tk.LEFT, padx=4)

        # Загружаем список сценариев
        self._refresh_scenario_list()
        self._scenario_var.trace_add("write", lambda *_: self._on_scenario_change())
        # Явно загружаем шаги первого сценария
        self._on_scenario_change()

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
            # GAP Req 3.4: when no step is selected (i is None), no warning is logged to BotLog.
            # Requirement says a warning should be logged when no step is selected.
            return
        self._steps[i-1], self._steps[i] = self._steps[i], self._steps[i-1]
        self._refresh_listbox()
        self._listbox.selection_set(i-1)

    def _move_down(self):
        i = self._get_selected()
        if i is None or i >= len(self._steps) - 1:
            # GAP Req 3.4: when no step is selected (i is None), no warning is logged to BotLog.
            # Requirement says a warning should be logged when no step is selected.
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
            # GAP Req 1.3: placeholder text differs from spec ("Нет шагов. Добавьте первый шаг.")
            # Functionally equivalent but wording does not match the requirement exactly.
            self._listbox.insert(tk.END, "  (нет шагов — нажмите '＋ Добавить шаг')")
            return
        for i, s in enumerate(self._steps, 1):
            self._listbox.insert(tk.END, f"  {i}. {step_label(s)}")

    # ── Drag & Drop ──────────────────────────────────────────────────────────

    def _on_drag_start(self, event):
        self._drag_start_index = self._listbox.nearest(event.y)
        self._listbox.config(cursor="fleur")

    def _on_drag_motion(self, event):
        if self._drag_start_index is None or not self._steps:
            return
        target = self._listbox.nearest(event.y)
        if target != self._drag_start_index:
            # Подсвечиваем целевую позицию
            self._listbox.selection_clear(0, tk.END)
            self._listbox.selection_set(target)

    def _on_drag_release(self, event):
        if self._drag_start_index is None or not self._steps:
            self._listbox.config(cursor="")
            return

        target = self._listbox.nearest(event.y)
        src = self._drag_start_index

        if src != target and 0 <= src < len(self._steps) and 0 <= target < len(self._steps):
            # Перемещаем шаг
            step = self._steps.pop(src)
            self._steps.insert(target, step)
            self._refresh_listbox()
            self._listbox.selection_set(target)

        self._drag_start_index = None
        self._listbox.config(cursor="")

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
            # GAP Req 4.3 / 4.4: ScenarioStorage.load() silently returns [] on missing file
            # or invalid JSON. The requirement says BotLog should receive specific messages:
            # "Файл сценария не найден" (missing) or an error message (bad JSON).
            # Currently no feedback is given to the user via log_callback.
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

        # GAP Req 5.9: when device is not connected, the requirement says log
        # "❌ Устройство не подключено" and do NOT start execution.
        # Instead, the current implementation auto-triggers the START flow and
        # waits up to 30 seconds for a connection — which is a UX improvement
        # but diverges from the specified behaviour.
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

    def _stop_scenario(self):
        """Останавливает выполнение сценария."""
        if self._running:
            self._stop_requested = True
            self.log("⏹ Остановка сценария...", "warning")
            self._stop_btn.config(state=tk.DISABLED, fg=THEME["text_disabled"])

    def _start_running(self):
        """Запускает выполнение шагов сценария."""
        self._running = True
        self._stop_requested = False
        self._run_btn.config(text="⏳ Выполняется...",
                             state=tk.DISABLED, fg=THEME["text_disabled"])
        self._stop_btn.config(state=tk.NORMAL, fg=THEME["accent_red"])

        def _thread():
            from processes.SCENARIO.scenario_01_runner import ScenarioRunner
            runner = ScenarioRunner(self._steps, self.adb.connected_device, self.log)
            runner.stop_flag = lambda: self._stop_requested
            runner.run()
            self.after(0, self._on_run_done)

        threading.Thread(target=_thread, daemon=True).start()

    def _on_run_done(self):
        self._running = False
        self._stop_requested = False
        self._run_btn.config(text="▶ Запустить",
                             state=tk.NORMAL, fg=THEME["btn_start_fg"])
        self._stop_btn.config(state=tk.DISABLED, fg=THEME["text_disabled"])

    # ── Пресеты ──────────────────────────────────────────────────────────────

    def _refresh_preset_list(self):
        menu = self._preset_menu["menu"]
        menu.delete(0, tk.END)
        self._presets_meta = PresetStorage.list_presets()
        if self._presets_meta:
            for p in self._presets_meta:
                label = p["name"]
                menu.add_command(label=label,
                                 command=lambda x=p["file"]: self._preset_var.set(x))
            if self._preset_var.get() not in [p["file"] for p in self._presets_meta]:
                self._preset_var.set(self._presets_meta[0]["file"])
        else:
            menu.add_command(label="(нет пресетов)", command=lambda: None)
            self._preset_var.set("")

    def _on_preset_change(self):
        file = self._preset_var.get()
        if not file:
            return
        meta = PresetStorage.load_meta(file)
        desc = meta.get("description", "")
        short = desc[:60] + "…" if len(desc) > 60 else desc
        self._preset_info.config(text=short)
        state = tk.NORMAL if PresetStorage.is_dev_mode() else tk.DISABLED
        fg = THEME["accent_orange"] if PresetStorage.is_dev_mode() else THEME["text_disabled"]
        self._preset_dev_btn.config(state=state, fg=fg)

    def _load_preset(self):
        file = self._preset_var.get()
        if not file:
            self.log("⚠ Выберите пресет", "warning")
            return
        steps = PresetStorage.load_steps(file)
        if not steps:
            self.log(f"⚠ Пресет '{file}' пуст или не найден", "warning")
            return
        if self._steps:
            answer = mb.askyesnocancel(
                "Загрузить пресет",
                f"Загрузить пресет '{file}'?\n\n"
                "Да — заменить текущие шаги\n"
                "Нет — добавить к текущим шагам\n"
                "Отмена — отменить",
                parent=self
            )
            if answer is None:
                return
            if answer:
                self._steps = list(steps)
            else:
                self._steps.extend(steps)
        else:
            self._steps = list(steps)
        self._refresh_listbox()
        self.log(f"📥 Пресет '{file}' загружен ({len(steps)} шагов)", "success")

    def _edit_preset_dev(self):
        """Открывает диалог редактирования пресета (только dev_mode)."""
        if not PresetStorage.is_dev_mode():
            self.log("🔒 Редактирование пресетов доступно только в режиме разработчика", "warning")
            return
        file = self._preset_var.get()
        if not file:
            self.log("⚠ Выберите пресет", "warning")
            return
        _PresetEditDialog(self, file, self.log, self._refresh_preset_list)

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


class _PresetEditDialog(tk.Toplevel):
    """Диалог редактирования пресета (только dev_mode)."""

    def __init__(self, parent, file_stem: str, log, refresh_cb):
        super().__init__(parent)
        self.title(f"✏ Редактор пресета: {file_stem}")
        self.configure(bg=THEME["bg_panel"])
        self.resizable(True, True)
        self.grab_set()
        self._file = file_stem
        self._log = log
        self._refresh_cb = refresh_cb
        self._steps = PresetStorage.load_steps(file_stem)
        self._meta = PresetStorage.load_meta(file_stem)
        self._build()
        self.transient(parent)

    def _build(self):
        # Метаданные
        meta_frame = tk.Frame(self, bg=THEME["bg_panel"], padx=12, pady=8)
        meta_frame.pack(fill=tk.X)

        for field, label in [("name", "Название:"), ("description", "Описание:"), ("version", "Версия:")]:
            row = tk.Frame(meta_frame, bg=THEME["bg_panel"])
            row.pack(fill=tk.X, pady=2)
            create_label(row, label, style="dim", bg=THEME["bg_panel"], width=12, anchor="w").pack(side=tk.LEFT)
            var = tk.StringVar(value=self._meta.get(field, ""))
            tk.Entry(row, textvariable=var, bg=THEME["bg_input"], fg=THEME["accent_blue"],
                     font=THEME["font_normal"], relief=tk.FLAT, width=50,
                     insertbackground=THEME["accent_green"]).pack(side=tk.LEFT, fill=tk.X, expand=True)
            setattr(self, f"_meta_{field}", var)

        create_separator(self).pack(fill=tk.X, padx=12, pady=4)

        # Список шагов
        list_frame = tk.Frame(self, bg=THEME["bg_panel"], padx=12)
        list_frame.pack(fill=tk.BOTH, expand=True)

        create_label(list_frame, "Шаги пресета:", style="dim", bg=THEME["bg_panel"]).pack(anchor="w")

        lb_wrap = tk.Frame(list_frame, bg=THEME["bg_input"])
        lb_wrap.pack(fill=tk.BOTH, expand=True)
        sb = tk.Scrollbar(lb_wrap)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._lb = tk.Listbox(lb_wrap, bg=THEME["bg_input"], fg=THEME["text_primary"],
                              font=THEME["font_log"], relief=tk.FLAT,
                              selectbackground=THEME["accent_blue"],
                              selectforeground=THEME["bg_main"],
                              yscrollcommand=sb.set, height=12)
        self._lb.pack(fill=tk.BOTH, expand=True)
        sb.config(command=self._lb.yview)
        self._lb.bind("<Double-Button-1>", lambda e: self._edit_step())
        self._refresh_lb()

        btns = tk.Frame(list_frame, bg=THEME["bg_panel"])
        btns.pack(fill=tk.X, pady=4)
        create_button(btns, "＋ Добавить", self._add_step, style="start", width=14).pack(side=tk.LEFT, padx=(0, 4))
        create_button(btns, "✏ Изменить", self._edit_step, width=12).pack(side=tk.LEFT, padx=2)
        create_button(btns, "▲", self._move_up, width=3).pack(side=tk.LEFT, padx=1)
        create_button(btns, "▼", self._move_down, width=3).pack(side=tk.LEFT, padx=1)
        create_button(btns, "🗑", self._del_step, width=3).pack(side=tk.LEFT, padx=1)

        create_separator(self).pack(fill=tk.X, padx=12, pady=4)

        bottom = tk.Frame(self, bg=THEME["bg_panel"], padx=12, pady=8)
        bottom.pack(fill=tk.X)
        create_button(bottom, "💾 Сохранить пресет", self._save, style="start", width=20).pack(side=tk.LEFT)
        create_button(bottom, "✖ Закрыть", self.destroy, width=12).pack(side=tk.LEFT, padx=8)

    def _refresh_lb(self):
        self._lb.delete(0, tk.END)
        if not self._steps:
            self._lb.insert(tk.END, "  (нет шагов)")
            return
        for i, s in enumerate(self._steps, 1):
            self._lb.insert(tk.END, f"  {i}. {step_label(s)}")

    def _get_sel(self):
        sel = self._lb.curselection()
        return sel[0] if sel and self._steps else None

    def _add_step(self):
        dlg = StepDialog(self, title="Добавить шаг в пресет")
        if dlg.result:
            self._steps.append(dlg.result)
            self._refresh_lb()

    def _edit_step(self):
        i = self._get_sel()
        if i is None:
            return
        dlg = StepDialog(self, title=f"Редактировать шаг {i+1}", step=self._steps[i])
        if dlg.result:
            self._steps[i] = dlg.result
            self._refresh_lb()
            self._lb.selection_set(i)

    def _del_step(self):
        i = self._get_sel()
        if i is None:
            return
        self._steps.pop(i)
        self._refresh_lb()

    def _move_up(self):
        i = self._get_sel()
        if i is None or i == 0:
            return
        self._steps[i-1], self._steps[i] = self._steps[i], self._steps[i-1]
        self._refresh_lb()
        self._lb.selection_set(i-1)

    def _move_down(self):
        i = self._get_sel()
        if i is None or i >= len(self._steps) - 1:
            return
        self._steps[i], self._steps[i+1] = self._steps[i+1], self._steps[i]
        self._refresh_lb()
        self._lb.selection_set(i+1)

    def _save(self):
        meta = {
            "name":        self._meta_name.get().strip(),
            "description": self._meta_description.get().strip(),
            "version":     self._meta_version.get().strip(),
            "author":      self._meta.get("author", ""),
        }
        try:
            PresetStorage.save(self._file, meta, self._steps)
            self._log(f"💾 Пресет '{self._file}' сохранён ({len(self._steps)} шагов)", "success")
            self._refresh_cb()
            self.destroy()
        except PermissionError as e:
            mb.showerror("Ошибка", str(e), parent=self)
