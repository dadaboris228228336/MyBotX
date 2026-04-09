#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/tabs/tab_dev.py — Вкладка DEV (режим разработчика).

Содержит редактор параметров бота, секцию создания паттернов,
последовательность запуска и размеры построек.
"""

import json
import threading
import tkinter as tk
import types
from pathlib import Path

from ..theme import THEME
from ..widgets import create_button, create_label, create_separator


def build(app):
    """Строит вкладку DEV и monkey-patches все _dev_* методы на app."""

    # ── Monkey-patch методов ──────────────────────────────────────────────

    def _dev_screenshot(self):
        if not self.adb.connected_device:
            self._dev_log("❌ Устройство не подключено", "error")
            return
        threading.Thread(target=self._dev_screenshot_thread, daemon=True).start()

    def _dev_screenshot_thread(self):
        try:
            from processes.BOT.bot_01_screenshot import BotScreenshot
            from PIL import Image, ImageTk

            self._dev_log("📸 Делаем скриншот...", "info")
            ss = BotScreenshot(self.adb.connected_device, self._dev_log)
            arr = ss.capture()

            if arr is None:
                self._dev_log("❌ Скриншот не получен", "error")
                return

            img = Image.fromarray(arr[:, :, ::-1])
            img.thumbnail((600, 190))
            photo = ImageTk.PhotoImage(img)
            self._dev_last_screenshot_orig = Image.fromarray(arr[:, :, ::-1])

            def _update():
                self.dev_preview_label.config(image=photo, text="")
                self.dev_preview_label.image = photo
            self.root.after(0, _update)
            self._dev_log("✅ Скриншот готов. Можно вырезать паттерн.", "success")
        except Exception as e:
            self._dev_log(f"❌ Ошибка: {e}", "error")

    def _dev_log(self, msg, tag="info"):
        if not hasattr(self, "dev_log_text"):
            return
        def _write():
            try:
                self.dev_log_text.config(state=tk.NORMAL)
                self.dev_log_text.insert(tk.END, msg + "\n")
                self.dev_log_text.see(tk.END)
                self.dev_log_text.config(state=tk.DISABLED)
            except Exception:
                pass
        self.root.after(0, _write)

    def _refresh_dev_pattern_dropdowns(self):
        patterns_dir = Path(__file__).parent.parent.parent / "processes" / "BOT" / "patterns"
        choices = ["(нет)"] + [f.stem for f in sorted(patterns_dir.glob("*.png"))]
        for pat_var, _, pat_menu in getattr(self, "_dev_startup_steps", []):
            try:
                if pat_var.get() not in choices:
                    pat_var.set("(нет)")
                menu = pat_menu["menu"]
                menu.delete(0, "end")
                for choice in choices:
                    menu.add_command(label=choice,
                                     command=lambda v=choice, var=pat_var: var.set(v))
            except Exception:
                pass

    def _dev_crop_pattern(self):
        if not self._dev_last_screenshot_orig:
            tk.messagebox.showwarning("Нет скриншота",
                                      "⚠ Сначала нажмите кнопку 'Скриншот'!",
                                      parent=self.root)
            return
        self.root.after(0, self._dev_crop_window)

    def _dev_crop_window(self):
        import tkinter.messagebox
        from PIL import ImageTk

        win = tk.Toplevel(self.root)
        win.title("Вырезать паттерн (Dev)")
        win.configure(bg=THEME["bg_main"])
        win.resizable(False, False)

        create_label(win, "Нарисуйте прямоугольник на скриншоте.",
                     style="dim", bg=THEME["bg_main"]).pack(pady=(6, 2))

        orig = self._dev_last_screenshot_orig.copy()
        display = orig.copy()
        display.thumbnail((900, 500))
        photo = ImageTk.PhotoImage(display)
        scale_x = orig.width / display.width
        scale_y = orig.height / display.height

        canvas = tk.Canvas(win, width=display.width, height=display.height,
                           bg=THEME["bg_main"], cursor="crosshair")
        canvas.pack(padx=8)
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image = photo

        rect = {"id": None, "x1": 50, "y1": 50, "x2": 200, "y2": 150}
        drag = {"mode": None, "ox": 0, "oy": 0, "rx1": 0, "ry1": 0, "rx2": 0, "ry2": 0}
        HANDLE = 10

        def draw_rect():
            if rect["id"]:
                canvas.delete(rect["id"])
            rect["id"] = canvas.create_rectangle(
                rect["x1"], rect["y1"], rect["x2"], rect["y2"],
                outline=THEME["accent_green"], width=2, dash=(4, 2))

        draw_rect()

        def get_mode(ex, ey):
            x1, y1, x2, y2 = rect["x1"], rect["y1"], rect["x2"], rect["y2"]
            nl = abs(ex-x1) < HANDLE; nr = abs(ex-x2) < HANDLE
            nt = abs(ey-y1) < HANDLE; nb = abs(ey-y2) < HANDLE
            inside = x1 < ex < x2 and y1 < ey < y2
            if nl and nt: return "resize_tl"
            if nr and nt: return "resize_tr"
            if nl and nb: return "resize_bl"
            if nr and nb: return "resize_br"
            if nl: return "resize_l"
            if nr: return "resize_r"
            if nt: return "resize_t"
            if nb: return "resize_b"
            if inside: return "move"
            return "draw"

        cursors = {"move":"fleur","resize_tl":"top_left_corner","resize_tr":"top_right_corner",
                   "resize_bl":"bottom_left_corner","resize_br":"bottom_right_corner",
                   "resize_l":"left_side","resize_r":"right_side",
                   "resize_t":"top_side","resize_b":"bottom_side","draw":"crosshair"}

        def on_motion(e): canvas.config(cursor=cursors.get(get_mode(e.x, e.y), "crosshair"))
        def on_press(e):
            drag["mode"] = get_mode(e.x, e.y)
            drag["ox"], drag["oy"] = e.x, e.y
            drag["rx1"], drag["ry1"] = rect["x1"], rect["y1"]
            drag["rx2"], drag["ry2"] = rect["x2"], rect["y2"]
        def on_drag(e):
            dx, dy = e.x-drag["ox"], e.y-drag["oy"]
            m = drag["mode"]
            x1,y1,x2,y2 = drag["rx1"],drag["ry1"],drag["rx2"],drag["ry2"]
            if m=="draw": rect["x1"],rect["y1"],rect["x2"],rect["y2"] = drag["ox"],drag["oy"],e.x,e.y
            elif m=="move": rect["x1"],rect["y1"],rect["x2"],rect["y2"] = x1+dx,y1+dy,x2+dx,y2+dy
            elif m=="resize_l": rect["x1"]=x1+dx
            elif m=="resize_r": rect["x2"]=x2+dx
            elif m=="resize_t": rect["y1"]=y1+dy
            elif m=="resize_b": rect["y2"]=y2+dy
            elif m=="resize_tl": rect["x1"],rect["y1"]=x1+dx,y1+dy
            elif m=="resize_tr": rect["x2"],rect["y1"]=x2+dx,y1+dy
            elif m=="resize_bl": rect["x1"],rect["y2"]=x1+dx,y2+dy
            elif m=="resize_br": rect["x2"],rect["y2"]=x2+dx,y2+dy
            draw_rect()

        canvas.bind("<Motion>", on_motion)
        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)

        bottom = tk.Frame(win, bg=THEME["bg_panel"], padx=12, pady=10)
        bottom.pack(fill=tk.X, padx=8, pady=6)
        row1 = tk.Frame(bottom, bg=THEME["bg_panel"])
        row1.pack(fill=tk.X, pady=2)
        create_label(row1, "Имя паттерна:", style="dim", bg=THEME["bg_panel"]).pack(side=tk.LEFT)
        name_var = tk.StringVar(value="pattern_1")
        tk.Entry(row1, textvariable=name_var, width=22, bg=THEME["bg_input"],
                 fg=THEME["accent_blue"], font=THEME["font_normal"], relief=tk.FLAT,
                 insertbackground=THEME["accent_green"]).pack(side=tk.LEFT, padx=8)
        btn_row2 = tk.Frame(bottom, bg=THEME["bg_panel"])
        btn_row2.pack(fill=tk.X, pady=(8, 0))

        def on_save():
            name = name_var.get().strip().replace(" ", "_")
            if not name:
                tk.messagebox.showwarning("Ошибка", "Введите имя паттерна", parent=win)
                return
            x1 = min(rect["x1"], rect["x2"]); y1 = min(rect["y1"], rect["y2"])
            x2 = max(rect["x1"], rect["x2"]); y2 = max(rect["y1"], rect["y2"])
            if x2-x1 < 5 or y2-y1 < 5:
                tk.messagebox.showwarning("Ошибка", "Выделите область на скриншоте", parent=win)
                return
            rx1,ry1 = int(x1*scale_x), int(y1*scale_y)
            rx2,ry2 = int(x2*scale_x), int(y2*scale_y)
            patterns_dir = Path(__file__).parent.parent.parent / "processes" / "BOT" / "patterns"
            orig.crop((rx1, ry1, rx2, ry2)).save(patterns_dir / f"{name}.png")
            self._dev_log(f"✅ Паттерн сохранён: {name}.png ({rx2-rx1}x{ry2-ry1}px)", "success")
            win.destroy()
            self._refresh_dev_pattern_dropdowns()

        create_button(btn_row2, "💾 Сохранить паттерн", on_save, style="start", width=26).pack(side=tk.LEFT)
        create_button(btn_row2, "✖ Отмена", win.destroy, width=12).pack(side=tk.LEFT, padx=8)

    def _dev_load_values(self):
        if not hasattr(self, "_dev_entries"):
            return
        constants_path = Path(__file__).parent.parent.parent.parent / "CONFIG" / "base_constants.json"
        try:
            with open(constants_path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
        for key_path, var in self._dev_entries.items():
            try:
                if len(key_path) == 2:
                    section, field = key_path
                    val = data.get(section, {}).get(field, "")
                else:
                    _, bkey, dim = key_path
                    val = data.get("buildings", {}).get(bkey, {}).get(dim, "")
                var.set(str(val))
            except Exception:
                pass

    def _dev_save(self):
        def _parse_number(v):
            try:
                return int(v) if "." not in str(v) else float(v)
            except Exception:
                return v
        constants_path = Path(__file__).parent.parent.parent.parent / "CONFIG" / "base_constants.json"
        try:
            try:
                with open(constants_path, encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
            for key_path, var in self._dev_entries.items():
                raw = var.get().strip()
                if len(key_path) == 2:
                    section, field = key_path
                    data.setdefault(section, {})[field] = _parse_number(raw)
                else:
                    _, bkey, dim = key_path
                    data.setdefault("buildings", {}).setdefault(bkey, {})[dim] = _parse_number(raw)
            if hasattr(self, "_dev_startup_steps"):
                data["startup_steps"] = [
                    {"pattern": p.get(), "action": a.get()}
                    for p, a, *_ in self._dev_startup_steps
                ]
            if hasattr(self, "_dev_startup_wait"):
                data["startup_wait"] = _parse_number(self._dev_startup_wait.get())
            with open(constants_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            self._dev_status.config(text="✅ Сохранено!", fg=THEME["accent_green"])
        except Exception as e:
            self._dev_status.config(text=f"❌ Ошибка: {e}", fg=THEME["accent_red"])

    # Привязываем методы к app
    app._dev_screenshot            = types.MethodType(_dev_screenshot, app)
    app._dev_screenshot_thread     = types.MethodType(_dev_screenshot_thread, app)
    app._dev_log                   = types.MethodType(_dev_log, app)
    app._refresh_dev_pattern_dropdowns = types.MethodType(_refresh_dev_pattern_dropdowns, app)
    app._dev_crop_pattern          = types.MethodType(_dev_crop_pattern, app)
    app._dev_crop_window           = types.MethodType(_dev_crop_window, app)
    app._dev_load_values           = types.MethodType(_dev_load_values, app)
    app._dev_save                  = types.MethodType(_dev_save, app)

    # ── Построение UI ────────────────────────────────────────────────────

    frame = app.frames["dev"]

    canvas = tk.Canvas(frame, bg=THEME["bg_main"], highlightthickness=0)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scroll = tk.Frame(canvas, bg=THEME["bg_main"])
    scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def section(title, desc=None):
        tk.Frame(scroll, bg=THEME["accent_blue"], height=2).pack(fill=tk.X, padx=20, pady=4)
        create_label(scroll, title, style="header", bg=THEME["bg_main"]).pack(anchor="w", padx=20, pady=(8,2))
        if desc:
            create_label(scroll, desc, style="dim", bg=THEME["bg_main"]).pack(anchor="w", padx=20, pady=(0,6))

    app._dev_entries = {}

    def entry_row(parent, label, key_path, default):
        row = tk.Frame(parent, bg=THEME["bg_main"])
        row.pack(fill=tk.X, pady=2, padx=20)
        create_label(row, label, style="normal", bg=THEME["bg_main"], width=30, anchor="w").pack(side=tk.LEFT)
        var = tk.StringVar(value=str(default))
        tk.Entry(row, textvariable=var, bg=THEME["bg_input"], fg=THEME["accent_blue"],
                 font=THEME["font_normal"], relief=tk.FLAT, width=10,
                 insertbackground=THEME["accent_green"]).pack(side=tk.LEFT, padx=8)
        app._dev_entries[key_path] = var
        return var

    create_label(scroll, "⚙️ Dev Mode", style="title", bg=THEME["bg_main"]).pack(anchor="w", padx=20, pady=(10,2))
    create_label(scroll, "Технические параметры бота. Изменения применяются после сохранения.",
                 style="dim", bg=THEME["bg_main"]).pack(anchor="w", padx=20, pady=(0,10))

    section("📐 1. Сетка базы", "Параметры изометрической сетки CoC (44×44 клетки)")
    entry_row(scroll, "Ширина сетки (клетки):", ("base", "grid_width_cells"), 44)
    entry_row(scroll, "Высота сетки (клетки):", ("base", "grid_height_cells"), 44)
    entry_row(scroll, "Угол правых диагоналей (°):", ("base", "isometric_angle_right"), 27.0)
    entry_row(scroll, "Угол левых диагоналей (°):", ("base", "isometric_angle_left"), 153.0)
    entry_row(scroll, "Допуск угла (°):", ("base", "angle_tolerance"), 3.0)

    section("🔍 2. Зум", "Ctrl+scroll в окне BlueStacks.")
    entry_row(scroll, "Прокруток за одно нажатие:", ("zoom", "scroll_ticks"), 10)
    entry_row(scroll, "Пауза между прокрутками (мс):", ("zoom", "scroll_interval_ms"), 50)
    entry_row(scroll, "Макс. шагов отдаления:", ("zoom", "max_out_steps"), 5)

    section("🎯 3. Центрирование", "Параметры алгоритма центрирования базы")
    entry_row(scroll, "Допуск центра (px):", ("centering", "center_tolerance_px"), 20)
    entry_row(scroll, "Отступ от края (px):", ("centering", "edge_margin_px"), 20)
    entry_row(scroll, "Макс. попыток коррекции:", ("centering", "max_correction_attempts"), 3)

    section("🚀 4. Последовательность запуска",
            "Шаги выполняемые после нажатия СТАРТ.")

    create_label(scroll, "Ожидание после запуска игры (сек):", style="normal", bg=THEME["bg_main"]).pack(anchor="w", padx=20, pady=(0,2))
    app._dev_startup_wait = tk.StringVar(value="15")
    tk.Entry(scroll, textvariable=app._dev_startup_wait, bg=THEME["bg_input"],
             fg=THEME["accent_blue"], font=THEME["font_normal"], relief=tk.FLAT, width=6,
             insertbackground=THEME["accent_green"]).pack(anchor="w", padx=20, pady=(0,8))

    # ── Секция создания паттернов ──
    tk.Frame(scroll, bg=THEME["accent_blue"], height=1).pack(fill=tk.X, padx=20, pady=(8,4))
    create_label(scroll, "📸 Создание паттернов", style="header", bg=THEME["bg_main"]).pack(anchor="w", padx=20, pady=(0,4))

    pat_section = tk.Frame(scroll, bg=THEME["bg_card"], padx=10, pady=8)
    pat_section.pack(fill=tk.X, padx=20, pady=(0,8))

    app.dev_preview_label = tk.Label(
        pat_section, text="📸 Скриншот появится здесь",
        bg=THEME["bg_input"], fg=THEME["accent_blue"],
        font=THEME["font_normal"], width=60, height=8, anchor="center"
    )
    app.dev_preview_label.pack(pady=(0,6))

    _dev_btn_row = tk.Frame(pat_section, bg=THEME["bg_card"])
    _dev_btn_row.pack(anchor="w")
    create_button(_dev_btn_row, "📸 Скриншот", app._dev_screenshot, width=16).pack(side=tk.LEFT, padx=(0,8))
    create_button(_dev_btn_row, "✂️ Вырезать паттерн", app._dev_crop_pattern, width=20).pack(side=tk.LEFT)

    app.dev_log_text = tk.Text(
        pat_section, height=4, bg=THEME["bg_input"], fg=THEME["accent_blue"],
        font=THEME["font_normal"], relief=tk.FLAT, state=tk.DISABLED
    )
    app.dev_log_text.pack(fill=tk.X, pady=(6,0))
    app._dev_last_screenshot_orig = None

    # ── Список шагов запуска ──
    create_label(scroll, "Шаги (паттерн → действие):", style="dim", bg=THEME["bg_main"]).pack(anchor="w", padx=20, pady=(0,4))
    create_label(scroll, "Бот ищет паттерн каждые 5 сек. Если найден — выполняет действие.",
                 style="dim", bg=THEME["bg_main"]).pack(anchor="w", padx=20, pady=(0,6))

    steps_frame = tk.Frame(scroll, bg=THEME["bg_card"], padx=10, pady=8)
    steps_frame.pack(fill=tk.X, padx=20, pady=(0,8))

    app._dev_startup_steps = []

    ACTIONS = ["tap", "zoom_out", "zoom_in", "center_base", "wait_5s", "skip"]

    def _get_patterns():
        patterns_dir = Path(__file__).parent.parent.parent / "processes" / "BOT" / "patterns"
        return ["(нет)"] + [f.stem for f in sorted(patterns_dir.glob("*.png"))]

    def _add_step(pattern="(нет)", action="tap"):
        row = tk.Frame(steps_frame, bg=THEME["bg_card"])
        row.pack(fill=tk.X, pady=2)
        idx = len(app._dev_startup_steps) + 1
        create_label(row, f"{idx}.", style="dim", bg=THEME["bg_card"], width=3).pack(side=tk.LEFT)

        pat_var = tk.StringVar(value=pattern)
        pat_menu = tk.OptionMenu(row, pat_var, *_get_patterns())
        pat_menu.config(bg=THEME["bg_input"], fg=THEME["accent_blue"],
                        font=THEME["font_normal"], relief=tk.FLAT, width=16,
                        activebackground=THEME["bg_card"])
        pat_menu.pack(side=tk.LEFT, padx=(0,6))

        act_var = tk.StringVar(value=action)
        act_menu = tk.OptionMenu(row, act_var, *ACTIONS)
        act_menu.config(bg=THEME["bg_input"], fg=THEME["accent_green"],
                        font=THEME["font_normal"], relief=tk.FLAT, width=18,
                        activebackground=THEME["bg_card"])
        act_menu.pack(side=tk.LEFT, padx=(0,6))

        def _remove():
            row.destroy()
            app._dev_startup_steps.remove((pat_var, act_var, pat_menu))
        tk.Button(row, text="✕", command=_remove, bg=THEME["bg_card"],
                  fg=THEME["accent_red"], font=THEME["font_normal"],
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT)

        app._dev_startup_steps.append((pat_var, act_var, pat_menu))

    btn_add_row = tk.Frame(steps_frame, bg=THEME["bg_card"])
    btn_add_row.pack(fill=tk.X, pady=(6,0))
    create_button(btn_add_row, "+ Добавить шаг", _add_step, width=18).pack(side=tk.LEFT)

    try:
        constants_path = Path(__file__).parent.parent.parent.parent / "CONFIG" / "base_constants.json"
        saved = json.loads(constants_path.read_text(encoding="utf-8")).get("startup_steps", [])
        for s in saved:
            _add_step(s.get("pattern", "(нет)"), s.get("action", "tap"))
    except Exception:
        pass

    if not app._dev_startup_steps:
        _add_step("(нет)", "zoom_out")
        _add_step("(нет)", "center_base")

    section("🏗 5. Размеры построек", "Размер каждой постройки в клетках сетки")

    buildings_frame = tk.Frame(scroll, bg=THEME["bg_main"])
    buildings_frame.pack(fill=tk.X, padx=20)
    col_left  = tk.Frame(buildings_frame, bg=THEME["bg_main"])
    col_right = tk.Frame(buildings_frame, bg=THEME["bg_main"])
    col_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
    col_right.pack(side=tk.LEFT, fill=tk.X, expand=True)

    building_defaults = [
        ("town_hall", "Town Hall", 4, 4), ("cannon", "Cannon", 3, 3),
        ("archer_tower", "Archer Tower", 3, 3), ("mortar", "Mortar", 3, 3),
        ("tesla", "Tesla", 2, 2), ("wall", "Wall", 1, 1),
        ("gold_mine", "Gold Mine", 3, 3), ("elixir_collector", "Elixir Collector", 3, 3),
    ]
    for i, (bkey, bname, dw, dh) in enumerate(building_defaults):
        parent_col = col_left if i % 2 == 0 else col_right
        grp = tk.Frame(parent_col, bg=THEME["bg_main"])
        grp.pack(fill=tk.X, pady=2)
        create_label(grp, f"{bname}:", style="dim", bg=THEME["bg_main"], width=18, anchor="w").pack(side=tk.LEFT)
        create_label(grp, "W:", style="dim", bg=THEME["bg_main"]).pack(side=tk.LEFT)
        var_w = tk.StringVar(value=str(dw))
        tk.Entry(grp, textvariable=var_w, bg=THEME["bg_input"], fg=THEME["accent_blue"],
                 font=THEME["font_normal"], relief=tk.FLAT, width=4,
                 insertbackground=THEME["accent_green"]).pack(side=tk.LEFT, padx=(2,6))
        create_label(grp, "H:", style="dim", bg=THEME["bg_main"]).pack(side=tk.LEFT)
        var_h = tk.StringVar(value=str(dh))
        tk.Entry(grp, textvariable=var_h, bg=THEME["bg_input"], fg=THEME["accent_blue"],
                 font=THEME["font_normal"], relief=tk.FLAT, width=4,
                 insertbackground=THEME["accent_green"]).pack(side=tk.LEFT, padx=2)
        app._dev_entries[("buildings", bkey, "w")] = var_w
        app._dev_entries[("buildings", bkey, "h")] = var_h

    tk.Frame(scroll, bg=THEME["accent_blue"], height=2).pack(fill=tk.X, padx=20, pady=12)
    btn_row = tk.Frame(scroll, bg=THEME["bg_main"])
    btn_row.pack(anchor="w", padx=20, pady=(0,10))
    create_button(btn_row, "💾  Сохранить", command=app._dev_save,
                  style="start", width=18).pack(side=tk.LEFT, padx=(0,10))
    create_button(btn_row, "🔄  Сбросить", command=app._dev_load_values,
                  width=16).pack(side=tk.LEFT)
    app._dev_status = create_label(scroll, "", style="dim", bg=THEME["bg_main"])
    app._dev_status.pack(anchor="w", padx=20, pady=(0,20))

    app._dev_load_values()
