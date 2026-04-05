#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 UI/scenario_editor.py
Редактор сценариев для вкладки БОТ.
Сценарий = список шагов, каждый шаг — тип действия + параметры.
Сохраняется в CORE/temp/scenarios/<name>.json
"""

import json
import threading
import time
import tkinter as tk
import tkinter.simpledialog as sd
import tkinter.messagebox as mb
from pathlib import Path
from tkinter import ttk

from .theme import THEME
from .widgets import create_button, create_label, create_separator

SCENARIOS_DIR = Path(__file__).parent.parent / "temp" / "scenarios"
PATTERNS_DIR  = Path(__file__).parent.parent / "processes" / "BOT" / "patterns"

# ── Типы шагов ──────────────────────────────────────────────────────────────
STEP_TYPES = [
    "Найти паттерн и нажать",
    "Нажать по координатам",
    "Свайп",
    "Отдалить (pinch out)",
    "Приблизить (pinch in)",
    "Кнопка HOME",
    "Кнопка BACK",
    "Ввод текста",
    "Запустить приложение",
    "Закрыть приложение",
    "Подождать",
]

STEP_TYPE_KEYS = {
    "Найти паттерн и нажать": "find_and_tap",
    "Нажать по координатам":  "tap_coords",
    "Свайп":                  "swipe",
    "Отдалить (pinch out)":   "pinch_out",
    "Приблизить (pinch in)":  "pinch_in",
    "Кнопка HOME":            "key_home",
    "Кнопка BACK":            "key_back",
    "Ввод текста":            "input_text",
    "Запустить приложение":   "launch_app",
    "Закрыть приложение":     "stop_app",
    "Подождать":              "wait",
}
STEP_KEY_LABELS = {v: k for k, v in STEP_TYPE_KEYS.items()}


def _get_adb():
    local = Path(__file__).parent.parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    return str(local) if local.exists() else "adb"


def _adb_run(device, args, timeout=10):
    import subprocess
    return subprocess.run([_get_adb(), "-s", device, *args],
                         capture_output=True, timeout=timeout)


class ScenarioRunner:
    """Выполняет шаги сценария последовательно в вызывающем потоке."""

    def __init__(self, steps, device, log):
        self.steps  = steps
        self.device = device
        self.log    = log

    def run(self):
        total = len(self.steps)
        for i, step in enumerate(self.steps, 1):
            t    = step["type"]
            p    = step.get("params", {})
            label = STEP_KEY_LABELS.get(t, t)
            self.log(f"▶ Шаг {i}/{total}: {label}", "info")
            try:
                self._dispatch(t, p)
            except Exception as e:
                self.log(f"❌ Ошибка на шаге {i}: {e}", "error")
                return
        self.log("✅ Сценарий завершён", "success")

    def _dispatch(self, t, p):
        d = self.device
        if t == "find_and_tap":
            self._find_and_tap(p)
        elif t == "tap_coords":
            _adb_run(d, ["shell", "input", "tap", str(p["x"]), str(p["y"])])
            self.log(f"  👆 tap ({p['x']}, {p['y']})", "dim")
        elif t == "swipe":
            _adb_run(d, ["shell", "input", "swipe",
                         str(p["x1"]), str(p["y1"]),
                         str(p["x2"]), str(p["y2"]),
                         str(p.get("duration", 300))])
            self.log(f"  👆 swipe ({p['x1']},{p['y1']})→({p['x2']},{p['y2']})", "dim")
        elif t == "pinch_out":
            self._pinch(d, zoom_in=False, times=int(p.get("times", 1)))
        elif t == "pinch_in":
            self._pinch(d, zoom_in=True,  times=int(p.get("times", 1)))
        elif t == "key_home":
            _adb_run(d, ["shell", "input", "keyevent", "3"])
            self.log("  🏠 HOME", "dim")
        elif t == "key_back":
            _adb_run(d, ["shell", "input", "keyevent", "4"])
            self.log("  ↩ BACK", "dim")
        elif t == "input_text":
            text = p.get("text", "").replace(" ", "%s")
            _adb_run(d, ["shell", "input", "text", text])
            self.log(f"  ⌨ text: {p.get('text','')}", "dim")
        elif t == "launch_app":
            _adb_run(d, ["shell", "monkey", "-p", p["package"], "-c",
                         "android.intent.category.LAUNCHER", "1"])
            self.log(f"  🚀 launch: {p['package']}", "dim")
        elif t == "stop_app":
            _adb_run(d, ["shell", "am", "force-stop", p["package"]])
            self.log(f"  🛑 stop: {p['package']}", "dim")
        elif t == "wait":
            secs = float(p.get("seconds", 1))
            self.log(f"  ⏳ ждём {secs}с", "dim")
            time.sleep(secs)

    def _find_and_tap(self, p):
        import subprocess, numpy as np, cv2
        from PIL import Image
        import io

        pattern_name = p["pattern"]
        threshold    = float(p.get("threshold", 0.8))
        retries      = int(p.get("retries", 3))
        delay        = float(p.get("retry_delay", 2.0))

        pattern_path = PATTERNS_DIR / f"{pattern_name}.png"
        if not pattern_path.exists():
            self.log(f"  ❌ Паттерн не найден: {pattern_name}", "error")
            return

        template = cv2.imread(str(pattern_path))
        if template is None:
            self.log(f"  ❌ Не удалось загрузить: {pattern_name}", "error")
            return

        for attempt in range(1, retries + 1):
            result = _adb_run(self.device,
                              ["exec-out", "screencap", "-p"], timeout=15)
            if result.returncode != 0:
                self.log("  ❌ Ошибка скриншота", "error")
                return

            img = Image.open(io.BytesIO(result.stdout)).convert("RGB")
            screen = np.array(img)[:, :, ::-1]  # RGB→BGR

            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val >= threshold:
                h, w = template.shape[:2]
                cx = max_loc[0] + w // 2
                cy = max_loc[1] + h // 2
                _adb_run(self.device, ["shell", "input", "tap", str(cx), str(cy)])
                self.log(f"  ✅ '{pattern_name}' найден ({max_val:.2f}) → tap ({cx},{cy})", "success")
                return

            self.log(f"  ⚠ попытка {attempt}/{retries}: '{pattern_name}' не найден ({max_val:.2f})", "warning")
            if attempt < retries:
                time.sleep(delay)

        self.log(f"  ⏭ '{pattern_name}' не найден за {retries} попыток — пропускаем", "warning")

    def _pinch(self, device, zoom_in: bool, times: int):
        # Pinch через два одновременных свайпа (ADB не поддерживает multi-touch напрямую,
        # используем sendevent или просто двойной swipe с задержкой)
        cx, cy = 540, 960
        offset = 200
        for _ in range(times):
            if zoom_in:
                # Приближение: пальцы сходятся к центру
                _adb_run(device, ["shell", "input", "swipe",
                                  str(cx - offset), str(cy), str(cx), str(cy), "300"])
                _adb_run(device, ["shell", "input", "swipe",
                                  str(cx + offset), str(cy), str(cx), str(cy), "300"])
            else:
                # Отдаление: пальцы расходятся от центра
                _adb_run(device, ["shell", "input", "swipe",
                                  str(cx), str(cy), str(cx - offset), str(cy), "300"])
                _adb_run(device, ["shell", "input", "swipe",
                                  str(cx), str(cy), str(cx + offset), str(cy), "300"])
            time.sleep(0.3)
        direction = "🔍 pinch_in" if zoom_in else "🔭 pinch_out"
        self.log(f"  {direction} x{times}", "dim")


# ── ScenarioEditor widget ────────────────────────────────────────────────────

class ScenarioEditor(tk.Frame):
    """
    Встраиваемый виджет редактора сценариев.
    Использование:
        editor = ScenarioEditor(parent, adb_manager, log_callback)
        editor.pack(fill=tk.BOTH, expand=True)
    """

    def __init__(self, parent, adb, log_callback):
        super().__init__(parent, bg=THEME["bg_main"])
        self.adb = adb
        self.log = log_callback  # fn(msg, tag)
        self._steps = []         # список dict шагов текущего сценария
        self._running = False
        SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)
        self._build()

    # ── Построение UI ────────────────────────────────────────────────────────

    def _build(self):
        # ── Верхняя панель: выбор / создание сценария ──
        top = tk.Frame(self, bg=THEME["bg_panel"], pady=6)
        top.pack(fill=tk.X)

        create_label(top, "🎬 Сценарий:", style="dim",
                     bg=THEME["bg_panel"]).pack(side=tk.LEFT, padx=(8, 4))

        self._scenario_var = tk.StringVar(value="")
        self._scenario_menu = tk.OptionMenu(top, self._scenario_var, "")
        self._scenario_menu.config(
            bg=THEME["bg_input"], fg=THEME["accent_blue"],
            font=THEME["font_normal"], relief=tk.FLAT,
            activebackground=THEME["bg_card"],
            activeforeground=THEME["accent_blue"],
            highlightthickness=0, width=20,
        )
        self._scenario_menu["menu"].config(
            bg=THEME["bg_input"], fg=THEME["accent_blue"],
            font=THEME["font_normal"],
        )
        self._scenario_menu.pack(side=tk.LEFT, padx=4)

        create_button(top, "＋ Новый",    self._new_scenario,    width=10).pack(side=tk.LEFT, padx=2)
        create_button(top, "✏ Переим.",   self._rename_scenario, width=10).pack(side=tk.LEFT, padx=2)
        create_button(top, "🗑 Удалить",  self._delete_scenario, width=10).pack(side=tk.LEFT, padx=2)

        self._scenario_var.trace_add("write", lambda *_: self._load_current())
        self._refresh_scenario_list()

        create_separator(self).pack(fill=tk.X)

        # ── Средняя часть: список шагов + форма добавления ──
        middle = tk.Frame(self, bg=THEME["bg_main"])
        middle.pack(fill=tk.BOTH, expand=True, pady=4)

        # Список шагов (левая часть)
        list_frame = tk.Frame(middle, bg=THEME["bg_main"])
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))

        create_label(list_frame, "Шаги сценария:", style="dim",
                     bg=THEME["bg_main"]).pack(anchor="w", padx=4)

        lb_frame = tk.Frame(list_frame, bg=THEME["bg_input"])
        lb_frame.pack(fill=tk.BOTH, expand=True, padx=4)

        scrollbar = tk.Scrollbar(lb_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._listbox = tk.Listbox(
            lb_frame,
            bg=THEME["bg_input"], fg=THEME["text_primary"],
            font=THEME["font_log"], relief=tk.FLAT,
            selectbackground=THEME["accent_blue"],
            selectforeground=THEME["bg_main"],
            yscrollcommand=scrollbar.set,
            activestyle="none",
        )
        self._listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._listbox.yview)

        # Кнопки управления шагами
        step_btns = tk.Frame(list_frame, bg=THEME["bg_main"])
        step_btns.pack(fill=tk.X, padx=4, pady=2)
        create_button(step_btns, "▲", self._move_up,     width=4).pack(side=tk.LEFT, padx=1)
        create_button(step_btns, "▼", self._move_down,   width=4).pack(side=tk.LEFT, padx=1)
        create_button(step_btns, "🗑", self._delete_step, width=4).pack(side=tk.LEFT, padx=1)

        # Форма добавления шага (правая часть)
        form_outer = tk.Frame(middle, bg=THEME["bg_panel"], width=260)
        form_outer.pack(side=tk.LEFT, fill=tk.Y, padx=(4, 0))
        form_outer.pack_propagate(False)

        create_label(form_outer, "Добавить шаг:", style="dim",
                     bg=THEME["bg_panel"]).pack(anchor="w", padx=8, pady=(6, 2))

        # Тип шага
        self._step_type_var = tk.StringVar(value=STEP_TYPES[0])
        type_menu = tk.OptionMenu(form_outer, self._step_type_var, *STEP_TYPES)
        type_menu.config(
            bg=THEME["bg_input"], fg=THEME["accent_blue"],
            font=THEME["font_small"], relief=tk.FLAT,
            activebackground=THEME["bg_card"],
            activeforeground=THEME["accent_blue"],
            highlightthickness=0, width=26,
        )
        type_menu["menu"].config(
            bg=THEME["bg_input"], fg=THEME["accent_blue"],
            font=THEME["font_small"],
        )
        type_menu.pack(padx=8, pady=2, fill=tk.X)

        self._step_type_var.trace_add("write", lambda *_: self._refresh_form())

        # Динамическая форма параметров
        self._form_frame = tk.Frame(form_outer, bg=THEME["bg_panel"])
        self._form_frame.pack(fill=tk.X, padx=8, pady=4)

        create_button(form_outer, "＋ Добавить шаг", self._add_step,
                      style="start", width=26).pack(padx=8, pady=6)

        self._refresh_form()

        # ── Нижняя панель: запуск / сохранение ──
        create_separator(self).pack(fill=tk.X)
        bottom = tk.Frame(self, bg=THEME["bg_panel"], pady=6)
        bottom.pack(fill=tk.X)

        self._run_btn = create_button(bottom, "▶ Запустить", self._run_scenario,
                                      style="start", width=16)
        self._run_btn.pack(side=tk.LEFT, padx=8)

        create_button(bottom, "💾 Сохранить", self._save_scenario, width=14).pack(side=tk.LEFT, padx=4)
        create_button(bottom, "📂 Загрузить",  self._load_current,  width=14).pack(side=tk.LEFT, padx=4)

    # ── Динамическая форма параметров ────────────────────────────────────────

    def _refresh_form(self):
        for w in self._form_frame.winfo_children():
            w.destroy()
        self._form_widgets = {}

        t = self._step_type_var.get()

        if t == "Найти паттерн и нажать":
            self._field("Паттерн:", "pattern", self._pattern_menu())
            self._entry("Порог (0-1):", "threshold", "0.8")
            self._entry("Попыток:", "retries", "3")
            self._entry("Пауза между попытками (с):", "retry_delay", "2.0")

        elif t == "Нажать по координатам":
            self._entry("X:", "x", "540")
            self._entry("Y:", "y", "960")

        elif t == "Свайп":
            self._entry("X1:", "x1", "300")
            self._entry("Y1:", "y1", "960")
            self._entry("X2:", "x2", "780")
            self._entry("Y2:", "y2", "960")
            self._entry("Длительность (мс):", "duration", "300")

        elif t in ("Отдалить (pinch out)", "Приблизить (pinch in)"):
            self._entry("Количество раз:", "times", "3")

        elif t in ("Запустить приложение", "Закрыть приложение"):
            self._entry("Package (com.xxx):", "package", "com.supercell.clashofclans")

        elif t == "Ввод текста":
            self._entry("Текст:", "text", "")

        elif t == "Подождать":
            self._entry("Секунд:", "seconds", "2.0")

        # HOME, BACK — параметров нет

    def _entry(self, label, key, default):
        row = tk.Frame(self._form_frame, bg=THEME["bg_panel"])
        row.pack(fill=tk.X, pady=1)
        create_label(row, label, style="dim", bg=THEME["bg_panel"]).pack(anchor="w")
        var = tk.StringVar(value=default)
        e = tk.Entry(row, textvariable=var,
                     bg=THEME["bg_input"], fg=THEME["accent_blue"],
                     font=THEME["font_small"], relief=tk.FLAT,
                     insertbackground=THEME["accent_green"], width=22)
        e.pack(fill=tk.X)
        self._form_widgets[key] = var

    def _field(self, label, key, widget):
        row = tk.Frame(self._form_frame, bg=THEME["bg_panel"])
        row.pack(fill=tk.X, pady=1)
        create_label(row, label, style="dim", bg=THEME["bg_panel"]).pack(anchor="w")
        widget.pack(fill=tk.X)
        # widget уже содержит StringVar через self._form_widgets[key]

    def _pattern_menu(self):
        patterns = [f.stem for f in PATTERNS_DIR.glob("*.png")]
        if not patterns:
            patterns = ["(нет паттернов)"]
        var = tk.StringVar(value=patterns[0])
        self._form_widgets["pattern"] = var
        m = tk.OptionMenu(self._form_frame, var, *patterns)
        m.config(bg=THEME["bg_input"], fg=THEME["accent_blue"],
                 font=THEME["font_small"], relief=tk.FLAT,
                 activebackground=THEME["bg_card"],
                 highlightthickness=0, width=22)
        m["menu"].config(bg=THEME["bg_input"], fg=THEME["accent_blue"],
                         font=THEME["font_small"])
        return m

    # ── Управление шагами ────────────────────────────────────────────────────

    def _add_step(self):
        t_label = self._step_type_var.get()
        t_key   = STEP_TYPE_KEYS[t_label]
        params  = {}

        try:
            w = self._form_widgets
            if t_key == "find_and_tap":
                params = {
                    "pattern":     w["pattern"].get(),
                    "threshold":   float(w["threshold"].get()),
                    "retries":     int(w["retries"].get()),
                    "retry_delay": float(w["retry_delay"].get()),
                }
            elif t_key == "tap_coords":
                params = {"x": int(w["x"].get()), "y": int(w["y"].get())}
            elif t_key == "swipe":
                params = {k: int(w[k].get()) for k in ("x1","y1","x2","y2","duration")}
            elif t_key in ("pinch_out", "pinch_in"):
                params = {"times": int(w["times"].get())}
            elif t_key in ("launch_app", "stop_app"):
                params = {"package": w["package"].get().strip()}
            elif t_key == "input_text":
                params = {"text": w["text"].get()}
            elif t_key == "wait":
                params = {"seconds": float(w["seconds"].get())}
            # key_home, key_back — params пустой
        except (ValueError, KeyError) as e:
            self.log(f"❌ Неверные параметры: {e}", "error")
            return

        step = {"type": t_key, "params": params}
        self._steps.append(step)
        self._refresh_listbox()
        self.log(f"➕ Добавлен шаг: {t_label}", "info")

    def _step_label(self, step):
        t = step["type"]
        p = step.get("params", {})
        label = STEP_KEY_LABELS.get(t, t)
        if t == "find_and_tap":
            return f"{label}: {p.get('pattern','')} (x{p.get('retries',1)})"
        elif t == "tap_coords":
            return f"{label}: ({p.get('x')}, {p.get('y')})"
        elif t == "swipe":
            return f"{label}: ({p.get('x1')},{p.get('y1')})→({p.get('x2')},{p.get('y2')})"
        elif t in ("pinch_out", "pinch_in"):
            return f"{label} x{p.get('times',1)}"
        elif t in ("launch_app", "stop_app"):
            return f"{label}: {p.get('package','')}"
        elif t == "input_text":
            return f"{label}: {p.get('text','')[:20]}"
        elif t == "wait":
            return f"{label}: {p.get('seconds')}с"
        return label

    def _refresh_listbox(self):
        self._listbox.delete(0, tk.END)
        if not self._steps:
            self._listbox.insert(tk.END, "  (нет шагов)")
            return
        for i, step in enumerate(self._steps, 1):
            self._listbox.insert(tk.END, f"  {i}. {self._step_label(step)}")

    def _selected_index(self):
        sel = self._listbox.curselection()
        if not sel or not self._steps:
            return None
        return sel[0]

    def _move_up(self):
        i = self._selected_index()
        if i is None or i == 0:
            return
        self._steps[i-1], self._steps[i] = self._steps[i], self._steps[i-1]
        self._refresh_listbox()
        self._listbox.selection_set(i-1)

    def _move_down(self):
        i = self._selected_index()
        if i is None or i >= len(self._steps) - 1:
            return
        self._steps[i], self._steps[i+1] = self._steps[i+1], self._steps[i]
        self._refresh_listbox()
        self._listbox.selection_set(i+1)

    def _delete_step(self):
        i = self._selected_index()
        if i is None:
            self.log("⚠ Выберите шаг для удаления", "warning")
            return
        removed = self._steps.pop(i)
        self._refresh_listbox()
        self.log(f"🗑 Удалён шаг: {self._step_label(removed)}", "dim")

    # ── Управление сценариями ────────────────────────────────────────────────

    def _scenario_files(self):
        return sorted(SCENARIOS_DIR.glob("*.json"))

    def _refresh_scenario_list(self):
        menu = self._scenario_menu["menu"]
        menu.delete(0, tk.END)
        files = self._scenario_files()
        if files:
            for f in files:
                name = f.stem
                menu.add_command(label=name,
                                 command=lambda n=name: self._scenario_var.set(n))
            if not self._scenario_var.get() or \
               not (SCENARIOS_DIR / f"{self._scenario_var.get()}.json").exists():
                self._scenario_var.set(files[0].stem)
        else:
            menu.add_command(label="(нет сценариев)", command=lambda: None)
            self._scenario_var.set("")

    def _new_scenario(self):
        name = sd.askstring("Новый сценарий", "Введите имя сценария:", parent=self)
        if not name:
            return
        name = name.strip().replace(" ", "_")
        path = SCENARIOS_DIR / f"{name}.json"
        path.write_text("[]", encoding="utf-8")
        self._refresh_scenario_list()
        self._scenario_var.set(name)
        self._steps = []
        self._refresh_listbox()
        self.log(f"✅ Создан сценарий: {name}", "success")

    def _rename_scenario(self):
        current = self._scenario_var.get()
        if not current:
            return
        new_name = sd.askstring("Переименовать", f"Новое имя для '{current}':", parent=self)
        if not new_name:
            return
        new_name = new_name.strip().replace(" ", "_")
        old_path = SCENARIOS_DIR / f"{current}.json"
        new_path = SCENARIOS_DIR / f"{new_name}.json"
        old_path.rename(new_path)
        self._refresh_scenario_list()
        self._scenario_var.set(new_name)
        self.log(f"✏ Переименован: {current} → {new_name}", "info")

    def _delete_scenario(self):
        current = self._scenario_var.get()
        if not current:
            return
        if not mb.askyesno("Удалить", f"Удалить сценарий '{current}'?", parent=self):
            return
        (SCENARIOS_DIR / f"{current}.json").unlink(missing_ok=True)
        self._steps = []
        self._refresh_listbox()
        self._refresh_scenario_list()
        self.log(f"🗑 Удалён сценарий: {current}", "dim")

    def _save_scenario(self):
        name = self._scenario_var.get()
        if not name:
            self.log("⚠ Сначала создайте сценарий", "warning")
            return
        path = SCENARIOS_DIR / f"{name}.json"
        path.write_text(json.dumps(self._steps, ensure_ascii=False, indent=2),
                        encoding="utf-8")
        self.log(f"💾 Сценарий '{name}' сохранён ({len(self._steps)} шагов)", "success")

    def _load_current(self, *_):
        name = self._scenario_var.get()
        if not name:
            return
        path = SCENARIOS_DIR / f"{name}.json"
        if not path.exists():
            return
        try:
            self._steps = json.loads(path.read_text(encoding="utf-8"))
            self._refresh_listbox()
            self.log(f"📂 Загружен сценарий '{name}' ({len(self._steps)} шагов)", "info")
        except Exception as e:
            self.log(f"❌ Ошибка загрузки: {e}", "error")

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
        self._run_btn.config(text="⏳ Выполняется...", state=tk.DISABLED,
                             fg=THEME["text_disabled"])

        def _thread():
            runner = ScenarioRunner(self._steps, self.adb.connected_device, self.log)
            runner.run()
            self.after(0, self._on_run_done)

        threading.Thread(target=_thread, daemon=True).start()

    def _on_run_done(self):
        self._running = False
        self._run_btn.config(text="▶ Запустить", state=tk.NORMAL,
                             fg=THEME["btn_start_fg"])
