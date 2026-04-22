#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI/tabs/tab_bot.py — Вкладка БОТ"""

import threading
import tkinter as tk
import types
from pathlib import Path
from tkinter import scrolledtext

from ..theme import THEME
from ..widgets import create_button, create_label
from ..scenario_editor import ScenarioEditor


def _patch_methods(app):
    """Monkey-patches all _bot_* methods onto app."""

    def _bot_log(self, msg: str, tag: str = "info"):
        self.root.after(0, lambda: self._bot_append_log(msg, tag))

    def _bot_append_log(self, msg: str, tag: str):
        self.bot_log.insert(tk.END, msg + "\n", tag)
        self.bot_log.see(tk.END)
        try:
            if self._session_logger:
                self._session_logger.write(msg, tag)
        except Exception:
            pass

    def _bot_screenshot(self):
        if not self.adb.connected_device:
            self._bot_log("❌ Устройство не подключено. Нажмите СТАРТ сначала.", "error")
            return
        threading.Thread(target=self._bot_screenshot_thread, daemon=True).start()

    def _bot_screenshot_thread(self):
        try:
            from processes.BOT.bot_01_screenshot import BotScreenshot
            from PIL import Image, ImageTk

            self._bot_log("📸 Делаем скриншот...", "info")
            ss = BotScreenshot(self.adb.connected_device, self._bot_log)
            arr = ss.capture()
            if arr is None:
                return
            img = Image.fromarray(arr[:, :, ::-1])
            img.thumbnail((600, 190))
            photo = ImageTk.PhotoImage(img)
            self._last_screenshot = arr
            self._last_screenshot_orig = Image.fromarray(arr[:, :, ::-1])
            self._last_screenshot_img  = img.copy()
            self.root.after(0, lambda: self._show_preview(photo))
            self._bot_log("✅ Скриншот готов. Можно вырезать паттерн.", "success")
        except Exception as e:
            self._bot_log(f"❌ Ошибка: {e}", "error")

    def _show_preview(self, photo):
        self.bot_preview_label.config(image=photo, text="")
        self.bot_preview_label.image = photo

    def _bot_crop_pattern(self):
        if not hasattr(self, "_last_screenshot_orig"):
            self._bot_log("⚠ Сначала нажмите кнопку 'Скриншот'!", "warning")
            self.root.after(0, lambda: tk.messagebox.showwarning(
                "Нет скриншота",
                "Сначала сделайте скриншот экрана BlueStacks.\n\nНажмите кнопку '📸 Скриншот'.",
                parent=self.root))
            return
        self.root.after(0, self._crop_window_new)

    def _crop_window_new(self):
        import tkinter.messagebox
        from PIL import ImageTk
        from UI.scenario_editor import StepDialog

        win = tk.Toplevel(self.root)
        win.title("Вырезать паттерн")
        win.configure(bg=THEME["bg_main"])
        win.resizable(False, False)

        create_label(win, "Нарисуйте прямоугольник на скриншоте. Можно перетащить или изменить размер.",
                     style="dim", bg=THEME["bg_main"]).pack(pady=(6, 2))

        orig = self._last_screenshot_orig.copy()
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
            x1,y1,x2,y2 = rect["x1"],rect["y1"],rect["x2"],rect["y2"]
            nl=abs(ex-x1)<HANDLE; nr=abs(ex-x2)<HANDLE
            nt=abs(ey-y1)<HANDLE; nb=abs(ey-y2)<HANDLE
            inside = x1<ex<x2 and y1<ey<y2
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

        def on_motion(e): canvas.config(cursor=cursors.get(get_mode(e.x,e.y),"crosshair"))
        def on_press(e):
            drag["mode"]=get_mode(e.x,e.y); drag["ox"],drag["oy"]=e.x,e.y
            drag["rx1"],drag["ry1"]=rect["x1"],rect["y1"]
            drag["rx2"],drag["ry2"]=rect["x2"],rect["y2"]
        def on_drag(e):
            dx,dy=e.x-drag["ox"],e.y-drag["oy"]; m=drag["mode"]
            x1,y1,x2,y2=drag["rx1"],drag["ry1"],drag["rx2"],drag["ry2"]
            if m=="draw": rect["x1"],rect["y1"],rect["x2"],rect["y2"]=drag["ox"],drag["oy"],e.x,e.y
            elif m=="move": rect["x1"],rect["y1"],rect["x2"],rect["y2"]=x1+dx,y1+dy,x2+dx,y2+dy
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
        btn_row = tk.Frame(bottom, bg=THEME["bg_panel"])
        btn_row.pack(fill=tk.X, pady=(8, 0))

        def on_save():
            name = name_var.get().strip().replace(" ", "_")
            if not name:
                tk.messagebox.showwarning("Ошибка", "Введите имя паттерна", parent=win)
                return
            x1=min(rect["x1"],rect["x2"]); y1=min(rect["y1"],rect["y2"])
            x2=max(rect["x1"],rect["x2"]); y2=max(rect["y1"],rect["y2"])
            if x2-x1<5 or y2-y1<5:
                tk.messagebox.showwarning("Ошибка", "Выделите область на скриншоте", parent=win)
                return
            rx1,ry1=int(x1*scale_x),int(y1*scale_y)
            rx2,ry2=int(x2*scale_x),int(y2*scale_y)
            patterns_dir = Path(__file__).parent.parent.parent / "processes" / "BOT" / "patterns"
            orig.crop((rx1,ry1,rx2,ry2)).save(patterns_dir / f"{name}.png")
            self._bot_log(f"✅ Паттерн сохранён: {name}.png ({rx2-rx1}x{ry2-ry1}px)", "success")
            win.destroy()
            if hasattr(self, "_scenario_editor"):
                step_template = {"type": "find_and_tap",
                                 "params": {"pattern": name, "threshold": 0.8,
                                            "retries": 3, "retry_delay": 2.0}}
                dlg = StepDialog(self.root, title=f"Настройка шага для паттерна '{name}'",
                                 step=step_template)
                if dlg.result:
                    self._scenario_editor.add_step_direct(dlg.result)
                    self._bot_log(f"➕ Шаг добавлен в сценарий: {name}", "info")

        create_button(btn_row, "💾 Сохранить и добавить в сценарий",
                      on_save, style="start", width=34).pack(side=tk.LEFT)
        create_button(btn_row, "✖ Отмена", win.destroy, width=12).pack(side=tk.LEFT, padx=8)

    def _refresh_patterns_list(self, parent):
        patterns_dir = Path(__file__).parent.parent.parent / "processes" / "BOT" / "patterns"
        files = list(patterns_dir.glob("*.png"))
        if files:
            for f in files:
                create_label(parent, f"  • {f.stem}", style="dim", bg=THEME["bg_panel"]).pack(anchor="w", padx=10)
        else:
            create_label(parent, "  Нет паттернов", style="dim", bg=THEME["bg_panel"]).pack(anchor="w", padx=10)

    def _bot_collect(self):
        if not self.adb.connected_device:
            self._bot_log("❌ Устройство не подключено", "error")
            return
        threading.Thread(target=self._bot_collect_thread, daemon=True).start()

    def _bot_collect_thread(self):
        try:
            from processes.BOT.bot_04_actions import BotActions
            BotActions(self.adb.connected_device, self._bot_log).collect_resources()
        except Exception as e:
            self._bot_log(f"❌ Ошибка: {e}", "error")

    def _bot_attack(self):
        if not self.adb.connected_device:
            self._bot_log("❌ Устройство не подключено", "error")
            return
        threading.Thread(target=self._bot_attack_thread, daemon=True).start()

    def _bot_attack_thread(self):
        try:
            from processes.BOT.bot_04_actions import BotActions
            BotActions(self.adb.connected_device, self._bot_log).start_attack()
        except Exception as e:
            self._bot_log(f"❌ Ошибка: {e}", "error")

    def _bot_close_popup(self):
        if not self.adb.connected_device:
            self._bot_log("❌ Устройство не подключено", "error")
            return
        threading.Thread(target=self._bot_close_thread, daemon=True).start()

    def _bot_close_thread(self):
        try:
            from processes.BOT.bot_04_actions import BotActions
            BotActions(self.adb.connected_device, self._bot_log).close_popup()
        except Exception as e:
            self._bot_log(f"❌ Ошибка: {e}", "error")

    def _bot_start_record(self): self._bot_log("ℹ️ Запись сценария пока не реализована.", "warning")
    def _bot_play_record(self):  self._bot_log("ℹ️ Воспроизведение сценария пока не реализовано.", "warning")
    def _bot_save_record(self):  self._bot_log("ℹ️ Сохранение сценария пока не реализовано.", "warning")

    # Привязываем все методы к app
    for name, fn in [
        ("_bot_log",              _bot_log),
        ("_bot_append_log",       _bot_append_log),
        ("_bot_screenshot",       _bot_screenshot),
        ("_bot_screenshot_thread",_bot_screenshot_thread),
        ("_show_preview",         _show_preview),
        ("_bot_crop_pattern",     _bot_crop_pattern),
        ("_crop_window_new",      _crop_window_new),
        ("_refresh_patterns_list",_refresh_patterns_list),
        ("_bot_collect",          _bot_collect),
        ("_bot_collect_thread",   _bot_collect_thread),
        ("_bot_attack",           _bot_attack),
        ("_bot_attack_thread",    _bot_attack_thread),
        ("_bot_close_popup",      _bot_close_popup),
        ("_bot_close_thread",     _bot_close_thread),
        ("_bot_start_record",     _bot_start_record),
        ("_bot_play_record",      _bot_play_record),
        ("_bot_save_record",      _bot_save_record),
    ]:
        setattr(app, name, types.MethodType(fn, app))


def build(app):
    """Строит вкладку БОТ. app = BotMainWindow."""
    _patch_methods(app)
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
