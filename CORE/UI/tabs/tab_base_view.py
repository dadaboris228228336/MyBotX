#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI/tabs/tab_base_view.py — Вкладка БАЗА"""

import threading
import tkinter as tk
from tkinter import scrolledtext
from ..theme import THEME
from ..widgets import create_button, create_label


def build(app):
    """Строит вкладку БАЗА. app = BotMainWindow."""
    frame = app.frames["base"]

    # Верхняя панель: кнопки управления
    top_row = tk.Frame(frame, bg=THEME["bg_main"])
    top_row.pack(fill=tk.X, pady=(0, 4))

    app._base_btn_screenshot = create_button(
        top_row, "📸 Скриншот", app._base_screenshot, width=18
    )
    app._base_btn_screenshot.pack(side=tk.LEFT, padx=(0, 6))

    app._base_btn_zoom_in = create_button(
        top_row, "🔍 Приблизить", app._base_zoom_in, width=16
    )
    app._base_btn_zoom_in.pack(side=tk.LEFT, padx=(0, 6))

    app._base_btn_zoom_out = create_button(
        top_row, "🔎 Отдалить", app._base_zoom_out, width=16
    )
    app._base_btn_zoom_out.pack(side=tk.LEFT, padx=(0, 6))

    app._base_btn_find_center = create_button(
        top_row, "🎯 Найти центр базы", app._base_find_center, width=20
    )
    app._base_btn_find_center.pack(side=tk.LEFT)

    # Превью + лог рядом
    preview_row = tk.Frame(frame, bg=THEME["bg_main"])
    preview_row.pack(fill=tk.X, pady=(0, 4))

    # Превью (слева)
    preview_frame = tk.Frame(preview_row, bg=THEME["bg_card"], height=140, width=420)
    preview_frame.pack(side=tk.LEFT, fill=tk.Y)
    preview_frame.pack_propagate(False)

    app.base_preview_label = tk.Label(
        preview_frame,
        text="📸 Скриншот появится здесь",
        bg=THEME["bg_card"], fg=THEME["text_secondary"],
        font=THEME["font_normal"],
    )
    app.base_preview_label.pack(expand=True)

    # Лог (справа)
    log_frame = tk.Frame(preview_row, bg=THEME["bg_input"])
    log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

    create_label(log_frame, "📋 Лог:", style="dim",
                 bg=THEME["bg_input"]).pack(anchor="w", padx=4, pady=(2, 0))

    app.base_log = scrolledtext.ScrolledText(
        log_frame, wrap=tk.WORD, font=THEME["font_log"],
        bg=THEME["bg_input"], fg=THEME["text_primary"],
        relief=tk.FLAT, bd=0, height=8,
    )
    app.base_log.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    for tag, color in [
        ("success", THEME["accent_green"]),
        ("error",   THEME["accent_red"]),
        ("warning", THEME["accent_orange"]),
        ("info",    THEME["accent_blue"]),
        ("dim",     THEME["text_secondary"]),
    ]:
        app.base_log.tag_config(tag, foreground=color)

    # Привязываем методы к app
    app._base_screenshot   = _make_base_screenshot(app)
    app._base_zoom_in      = _make_base_zoom_in(app)
    app._base_zoom_out     = _make_base_zoom_out(app)
    app._base_find_center  = _make_base_find_center(app)
    app._base_log          = _make_base_log(app)

    # Обновляем команды кнопок на только что созданные методы
    app._base_btn_screenshot.config(command=app._base_screenshot)
    app._base_btn_zoom_in.config(command=app._base_zoom_in)
    app._base_btn_zoom_out.config(command=app._base_zoom_out)
    app._base_btn_find_center.config(command=app._base_find_center)


# ---------------------------------------------------------------------------
# Фабрики методов
# ---------------------------------------------------------------------------

def _make_base_log(app):
    """Возвращает функцию логирования в app.base_log."""
    def _base_log(msg: str, tag: str = ""):
        def _write():
            app.base_log.config(state=tk.NORMAL)
            if tag:
                app.base_log.insert(tk.END, msg + "\n", tag)
            else:
                app.base_log.insert(tk.END, msg + "\n")
            app.base_log.see(tk.END)
            app.base_log.config(state=tk.DISABLED)
        app.root.after(0, _write)
    return _base_log


def _make_base_screenshot(app):
    """Возвращает обработчик кнопки «📸 Скриншот»."""
    def _base_screenshot():
        if not app.adb.connected_device:
            app._base_log("❌ Устройство не подключено", "error")
            return
        threading.Thread(target=_screenshot_thread, daemon=True).start()

    def _screenshot_thread():
        try:
            from processes.BOT.bot_01_screenshot import BotScreenshot
            from PIL import Image, ImageTk

            app._base_log("📸 Делаем скриншот...", "info")
            ss = BotScreenshot(app.adb.connected_device, app._base_log)
            arr = ss.capture()
            if arr is None:
                app._base_log("❌ Скриншот вернул None", "error")
                return

            img = Image.fromarray(arr[:, :, ::-1])
            img.thumbnail((600, 190))
            photo = ImageTk.PhotoImage(img)

            def _show():
                app.base_preview_label.config(image=photo, text="")
                app.base_preview_label.image = photo

            app.root.after(0, _show)
            app._base_log("✅ Скриншот готов", "success")
        except Exception as e:
            app._base_log(f"❌ Ошибка: {e}", "error")

    return _base_screenshot


def _make_base_zoom_in(app):
    """Возвращает обработчик кнопки «🔍 Приблизить»."""
    def _base_zoom_in():
        if not app.adb.connected_device:
            app._base_log("❌ Устройство не подключено", "error")
            return
        threading.Thread(target=_zoom_in_thread, daemon=True).start()

    def _zoom_in_thread():
        try:
            vc = _make_view_controller(app)
            if vc is None:
                return
            vc.zoom_in()
        except Exception as e:
            app._base_log(f"❌ Ошибка приближения: {e}", "error")

    return _base_zoom_in


def _make_base_zoom_out(app):
    """Возвращает обработчик кнопки «🔎 Отдалить»."""
    def _base_zoom_out():
        if not app.adb.connected_device:
            app._base_log("❌ Устройство не подключено", "error")
            return
        threading.Thread(target=_zoom_out_thread, daemon=True).start()

    def _zoom_out_thread():
        try:
            vc = _make_view_controller(app)
            if vc is None:
                return
            vc.zoom_out()
        except Exception as e:
            app._base_log(f"❌ Ошибка отдаления: {e}", "error")

    return _base_zoom_out


def _make_base_find_center(app):
    """Возвращает обработчик кнопки «🎯 Найти центр базы»."""
    def _base_find_center():
        if not app.adb.connected_device:
            app._base_log("❌ Устройство не подключено", "error")
            return
        threading.Thread(target=_find_center_thread, daemon=True).start()

    def _find_center_thread():
        try:
            from processes.BOT.bot_01_screenshot import BotScreenshot
            from PIL import Image, ImageTk

            vc = _make_view_controller(app)
            if vc is None:
                return

            def _screenshot_provider():
                ss = BotScreenshot(app.adb.connected_device, app._base_log)
                return ss.capture()

            app._base_log("🎯 Запуск поиска центра базы...", "info")
            success = vc.find_and_center(_screenshot_provider)

            if success:
                # Показываем финальный скриншот в превью
                arr = _screenshot_provider()
                if arr is not None:
                    img = Image.fromarray(arr[:, :, ::-1])
                    img.thumbnail((600, 190))
                    photo = ImageTk.PhotoImage(img)

                    def _show():
                        app.base_preview_label.config(image=photo, text="")
                        app.base_preview_label.image = photo

                    app.root.after(0, _show)
                app._base_log("✅ Центр базы найден", "success")
            else:
                app._base_log("⚠ Не удалось найти центр базы", "warning")
        except Exception as e:
            app._base_log(f"❌ Ошибка: {e}", "error")

    return _base_find_center


# ---------------------------------------------------------------------------
# Вспомогательная функция
# ---------------------------------------------------------------------------

def _make_view_controller(app):
    """Создаёт ViewController с текущими параметрами устройства."""
    import os
    from pathlib import Path

    try:
        from processes.BASE_VIEW.base_03_view_controller import ViewController
        from processes.BASE_VIEW.base_00_constants import load_constants
    except ImportError:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        from CORE.processes.BASE_VIEW.base_03_view_controller import ViewController
        from CORE.processes.BASE_VIEW.base_00_constants import load_constants

    constants_path = Path(__file__).parent.parent.parent.parent / "CONFIG" / "base_constants.json"
    constants = load_constants(str(constants_path))

    # Получаем размеры экрана из adb или используем дефолтные
    screen_w = getattr(app, "_base_screen_w", 1280)
    screen_h = getattr(app, "_base_screen_h", 720)

    return ViewController(
        device_serial=app.adb.connected_device,
        screen_w=screen_w,
        screen_h=screen_h,
        constants=constants,
        log_callback=app._base_log,
    )
