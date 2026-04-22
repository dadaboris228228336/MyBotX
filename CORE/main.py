#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🖥️ MyBotX GUI v3.0.0 - Геймерский интерфейс
"""

import os
import sys
import time
import tkinter as tk
import threading
from pathlib import Path
from tkinter import scrolledtext
import tkinter.messagebox

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dependency_checker import DependencyChecker
    from bluestacks_manager import BlueStacksManager
    from advanced_adb_manager import AdvancedADBManager
    from UI.theme import THEME
    from UI.widgets import create_button, create_label, create_frame, create_separator
    from UI.pattern_editor import PatternEditor
    from UI.scenario_editor import ScenarioEditor
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from dependency_checker import DependencyChecker
    from bluestacks_manager import BlueStacksManager
    from advanced_adb_manager import AdvancedADBManager
    from UI.theme import THEME
    from UI.widgets import create_button, create_label, create_frame, create_separator
    from UI.pattern_editor import PatternEditor
    from UI.scenario_editor import ScenarioEditor


class BotMainWindow:

    def __init__(self, root):
        self.root = root
        self.root.title("MyBotX")
        self.root.geometry("960x620")
        self.root.configure(bg=THEME["bg_main"])
        self.root.resizable(True, True)
        self.root.minsize(800, 550)

        # Иконка приложения
        try:
            icon_path = Path(__file__).parent / "mybotx.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass

        self.checker = None
        self.is_checking = False
        self.bluestacks = BlueStacksManager()
        self.adb = AdvancedADBManager()

        # Размеры экрана BlueStacks (обновляются при подключении устройства)
        self._base_screen_w = 1280
        self._base_screen_h = 720

        # Инициализируем логгер сессии
        try:
            import session_logger
            session_logger.init()
            self._session_logger = session_logger
        except Exception:
            self._session_logger = None

        # Записываем PID текущего процесса (R1: Smart Launcher PID)
        self._pid_file = Path(__file__).parent / "temp" / "mybotx.pid"
        self._pid_file.parent.mkdir(parents=True, exist_ok=True)
        self._pid_file.write_text(str(os.getpid()), encoding="utf-8")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_user)

        # Мониторинг BlueStacks — проверяем каждые 10 сек
        self._bs_monitor_active = False
        self._start_bs_monitor()

        self._build_ui()

        # Сворачиваем все окна кроме нашего через 1 секунду после запуска
        self.root.after(1000, self._minimize_other_windows)

    # ─────────────────────────────────────────────
    # ПОСТРОЕНИЕ UI
    # ─────────────────────────────────────────────

    def _build_ui(self):
        """Строим весь интерфейс"""
        self._build_header()
        self._build_tabs()

    def _build_header(self):
        """Шапка с логотипом и версией"""
        header = tk.Frame(self.root, bg=THEME["bg_panel"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        create_label(
            header,
            text="⚡ MyBotX",
            style="title",
            bg=THEME["bg_panel"]
        ).pack(side=tk.LEFT, padx=20, pady=10)

        create_label(
            header,
            text="v1.0.0  |  Clash of Clans Bot",
            style="dim",
            bg=THEME["bg_panel"]
        ).pack(side=tk.LEFT, pady=10)

        # Статус-индикатор справа
        self.header_status = create_label(
            header,
            text="● ГОТОВ",
            style="success",
            bg=THEME["bg_panel"]
        )
        self.header_status.pack(side=tk.RIGHT, padx=20)

        create_separator(self.root).pack(fill=tk.X)

    def _build_tabs(self):
        """Вкладки: ОСНОВНОЕ | ПРОВЕРКА | О ПРОГРАММЕ"""
        # Панель вкладок
        tab_bar = tk.Frame(self.root, bg=THEME["bg_main"])
        tab_bar.pack(fill=tk.X, padx=0, pady=0)

        self.tab_content = tk.Frame(self.root, bg=THEME["bg_main"])
        self.tab_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Создаём фреймы вкладок
        self.frames = {
            "main":     tk.Frame(self.tab_content, bg=THEME["bg_main"]),
            "check":    tk.Frame(self.tab_content, bg=THEME["bg_main"]),
            "bot":      tk.Frame(self.tab_content, bg=THEME["bg_main"]),
            "base":     tk.Frame(self.tab_content, bg=THEME["bg_main"]),
            "auto":     tk.Frame(self.tab_content, bg=THEME["bg_main"]),
            "settings": tk.Frame(self.tab_content, bg=THEME["bg_main"]),
            "about":    tk.Frame(self.tab_content, bg=THEME["bg_main"]),
            "dev":      tk.Frame(self.tab_content, bg=THEME["bg_main"]),
        }

        # Кнопки вкладок
        self.tab_buttons = {}
        tabs = [("main", "🏠  ОСНОВНОЕ"), ("check", "🔍  ПРОВЕРКА"), ("bot", "🤖  БОТ"), ("base", "🏰  БАЗА"), ("auto", "⚡  АВТО"), ("settings", "⚙️  НАСТРОЙКИ"), ("about", "ℹ️  О ПРОГРАММЕ")]
        for key, label in tabs:
            btn = tk.Button(
                tab_bar,
                text=label,
                bg=THEME["bg_panel"],
                fg=THEME["text_secondary"],
                font=THEME["font_normal"],
                relief=tk.FLAT,
                bd=0,
                padx=20,
                pady=10,
                cursor="hand2",
                command=lambda k=key: self._switch_tab(k),
                activebackground=THEME["bg_card"],
                activeforeground=THEME["accent_blue"],
            )
            btn.pack(side=tk.LEFT)
            self.tab_buttons[key] = btn

        # Кнопка DEV — скрыта по умолчанию
        dev_btn = tk.Button(
            tab_bar,
            text="⚙️  DEV",
            bg=THEME["bg_panel"],
            fg=THEME["accent_orange"],
            font=THEME["font_normal"],
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=lambda: self._switch_tab("dev"),
            activebackground=THEME["bg_card"],
            activeforeground=THEME["accent_orange"],
        )
        self.tab_buttons["dev"] = dev_btn
        # Не пакуем — скрыта по умолчанию

        create_separator(self.root).pack(fill=tk.X)

        # Наполняем вкладки через модули tabs/
        from UI.tabs.tab_main     import build as build_main
        from UI.tabs.tab_check    import build as build_check
        from UI.tabs.tab_bot      import build as build_bot
        from UI.tabs.tab_base_view import build as build_base
        from UI.tabs.tab_auto     import build as build_auto
        from UI.tabs.tab_settings import build as build_settings
        from UI.tabs.tab_about    import build as build_about
        from UI.tabs.tab_dev      import build as build_dev

        build_main(self)
        build_check(self)
        build_bot(self)
        build_base(self)
        build_auto(self)
        build_settings(self)
        build_about(self)
        build_dev(self)

        # Показываем первую вкладку
        self._switch_tab("main")

    def _switch_tab(self, key):
        """Переключение вкладки"""
        for k, frame in self.frames.items():
            frame.pack_forget()
        self.frames[key].pack(fill=tk.BOTH, expand=True)
        self._current_tab = key

        # При открытии DEV вкладки — загружаем актуальные значения
        if key == "dev" and hasattr(self, "_dev_load_values"):
            self._dev_load_values()

        for k, btn in self.tab_buttons.items():
            if k == key:
                if k == "dev":
                    btn.config(fg=THEME["accent_orange"], bg=THEME["bg_card"])
                else:
                    btn.config(fg=THEME["accent_blue"], bg=THEME["bg_card"])
            else:
                if k == "dev":
                    btn.config(fg=THEME["accent_orange"], bg=THEME["bg_panel"])
                else:
                    btn.config(fg=THEME["text_secondary"], bg=THEME["bg_panel"])

    # ─────────────────────────────────────────────
    # ВКЛАДКА: ОСНОВНОЕ
    # ─────────────────────────────────────────────

    def _build_main_tab(self):
        frame = self.frames["main"]

        # Центральный блок
        center = tk.Frame(frame, bg=THEME["bg_main"])
        center.place(relx=0.5, rely=0.5, anchor="center")

        create_label(center, "⚡ MyBotX", style="title", bg=THEME["bg_main"]).pack(pady=(0, 5))
        create_label(center, "Clash of Clans Automation Bot", style="dim", bg=THEME["bg_main"]).pack(pady=(0, 30))

        # Кнопка СТАРТ
        self.start_btn = create_button(
            center,
            text="▶   СТАРТ",
            command=self.on_start_bot,
            style="start",
            width=25
        )
        self.start_btn.pack(pady=10, ipady=6)

        # Статусбар
        self.statusbar = create_label(
            center,
            text="Готов к запуску",
            style="dim",
            bg=THEME["bg_main"]
        )
        self.statusbar.pack(pady=(15, 0))

        # Блок статистики внизу
        stats = tk.Frame(frame, bg=THEME["bg_panel"])
        stats.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)

        self.stats_labels = {}
        for text, val in [("BlueStacks", "—"), ("ADB", "—"), ("Игра", "—")]:
            col = tk.Frame(stats, bg=THEME["bg_panel"])
            col.pack(side=tk.LEFT, expand=True, pady=10)
            create_label(col, text, style="dim", bg=THEME["bg_panel"]).pack()
            lbl = create_label(col, val, style="normal", bg=THEME["bg_panel"])
            lbl.pack()
            self.stats_labels[text] = lbl

    # ─────────────────────────────────────────────
    # ВКЛАДКА: ПРОВЕРКА
    # ─────────────────────────────────────────────

    def _build_check_tab(self):
        frame = self.frames["check"]

        # Кнопки управления
        btn_row = tk.Frame(frame, bg=THEME["bg_main"])
        btn_row.pack(fill=tk.X, pady=(0, 8))

        self.check_btn = create_button(
            btn_row, "🔍  Проверить всё",
            command=self.on_check_button_click, width=22
        )
        self.check_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.install_btn = create_button(
            btn_row, "📦  Установить пакеты",
            command=self.on_install_button_click, width=22
        )
        self.install_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.install_btn.config(state=tk.DISABLED, fg=THEME["text_disabled"])

        self.uninstall_btn = create_button(
            btn_row, "🗑  Удалить пакеты",
            command=self.on_uninstall_button_click, style="danger", width=18
        )
        self.uninstall_btn.pack(side=tk.LEFT, padx=(0, 8))

        create_button(
            btn_row, "🗑  Очистить логи",
            command=self.on_clear_logs, width=18
        ).pack(side=tk.LEFT)

        create_button(
            btn_row, "📸  Скриншот",
            command=self.on_screenshot, width=14
        ).pack(side=tk.RIGHT, padx=(8, 0))

        # Статус-карточки
        cards = tk.Frame(frame, bg=THEME["bg_main"])
        cards.pack(fill=tk.X, pady=(0, 8))

        self.status_labels = {}
        items = [
            ("packages", "📦 Пакеты", "—"),
            ("bluestacks", "🖥 BlueStacks", "—"),
            ("path", "📁 Путь", "—"),
        ]
        for key, title, val in items:
            card = tk.Frame(cards, bg=THEME["bg_card"], padx=12, pady=8)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
            create_label(card, title, style="dim", bg=THEME["bg_card"]).pack(anchor="w")
            lbl = create_label(card, val, style="normal", bg=THEME["bg_card"])
            lbl.pack(anchor="w")
            self.status_labels[key] = lbl

        # Прогресс-бар
        self.progress_bar = tk.Frame(frame, bg=THEME["accent_blue"], height=2)
        self.progress_bar.pack(fill=tk.X, pady=(0, 8))
        self._progress_running = False

        # Лог
        log_frame = tk.Frame(frame, bg=THEME["bg_input"], padx=2, pady=2)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=THEME["font_log"],
            bg=THEME["bg_input"],
            fg=THEME["text_primary"],
            insertbackground=THEME["accent_green"],
            selectbackground=THEME["accent_blue"],
            relief=tk.FLAT,
            bd=0,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.log_text.tag_config("success", foreground=THEME["accent_green"])
        self.log_text.tag_config("error",   foreground=THEME["accent_red"])
        self.log_text.tag_config("warning", foreground=THEME["accent_orange"])
        self.log_text.tag_config("info",    foreground=THEME["accent_blue"])
        self.log_text.tag_config("dim",     foreground=THEME["text_secondary"])

    # ─────────────────────────────────────────────
    # ВКЛАДКА: БОТ
    # ─────────────────────────────────────────────

    def _build_bot_tab(self):
        frame = self.frames["bot"]

        # Верхняя панель: скриншот + вырезать паттерн
        top_row = tk.Frame(frame, bg=THEME["bg_main"])
        top_row.pack(fill=tk.X, pady=(0, 4))

        create_button(top_row, "📸 Скриншот",         self._bot_screenshot,   width=18).pack(side=tk.LEFT, padx=(0, 6))
        create_button(top_row, "✂️ Вырезать паттерн", self._bot_crop_pattern, width=20).pack(side=tk.LEFT)

        # Превью + лог рядом
        preview_row = tk.Frame(frame, bg=THEME["bg_main"])
        preview_row.pack(fill=tk.X, pady=(0, 4))

        # Превью скриншота (слева)
        preview_frame = tk.Frame(preview_row, bg=THEME["bg_card"], height=140, width=420)
        preview_frame.pack(side=tk.LEFT, fill=tk.Y)
        preview_frame.pack_propagate(False)

        self.bot_preview_label = tk.Label(
            preview_frame,
            text="📸 Скриншот появится здесь",
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            font=THEME["font_normal"]
        )
        self.bot_preview_label.pack(expand=True)

        # Лог бота (справа от скриншота)
        log_frame = tk.Frame(preview_row, bg=THEME["bg_input"])
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

        create_label(log_frame, "📋 Лог:", style="dim",
                     bg=THEME["bg_input"]).pack(anchor="w", padx=4, pady=(2, 0))

        self.bot_log = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=THEME["font_log"],
            bg=THEME["bg_input"],
            fg=THEME["text_primary"],
            relief=tk.FLAT,
            bd=0,
            height=8,
        )
        self.bot_log.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.bot_log.tag_config("success", foreground=THEME["accent_green"])
        self.bot_log.tag_config("error",   foreground=THEME["accent_red"])
        self.bot_log.tag_config("warning", foreground=THEME["accent_orange"])
        self.bot_log.tag_config("info",    foreground=THEME["accent_blue"])
        self.bot_log.tag_config("dim",     foreground=THEME["text_secondary"])

        # Редактор сценариев (внизу)
        self._scenario_editor = ScenarioEditor(frame, self.adb, self._bot_log,
                                               start_callback=self.on_start_bot,
                                               is_connected=lambda: bool(self.adb.connected_device))
        self._scenario_editor.pack(fill=tk.BOTH, expand=True)

    def _refresh_patterns_list(self, parent):
        """Показывает список паттернов из папки patterns/"""
        from pathlib import Path
        patterns_dir = Path(__file__).parent / "processes" / "BOT" / "patterns"
        files = list(patterns_dir.glob("*.png"))
        if files:
            for f in files:
                create_label(parent, f"  • {f.stem}", style="dim", bg=THEME["bg_panel"]).pack(anchor="w", padx=10)
        else:
            create_label(parent, "  Нет паттернов", style="dim", bg=THEME["bg_panel"]).pack(anchor="w", padx=10)

    def _bot_log(self, msg: str, tag: str = "info"):
        """Лог в окно бота"""
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
        """Сделать скриншот и показать превью"""
        if not self.adb.connected_device:
            self._bot_log("❌ Устройство не подключено. Нажмите СТАРТ сначала.", "error")
            return
        threading.Thread(target=self._bot_screenshot_thread, daemon=True).start()

    def _bot_screenshot_thread(self):
        try:
            from processes.SCREENSHOT import ScreenshotCapture as BotScreenshot
            from PIL import Image, ImageTk
            import io

            self._bot_log("📸 Делаем скриншот...", "info")
            ss = BotScreenshot(self.adb.connected_device, self._bot_log)
            arr = ss.capture()

            if arr is None:
                return

            # Показываем превью
            img = Image.fromarray(arr[:, :, ::-1])
            img.thumbnail((600, 190))
            photo = ImageTk.PhotoImage(img)

            # Сохраняем ОРИГИНАЛ для вырезки паттерна (не уменьшенное превью!)
            self._last_screenshot = arr
            self._last_screenshot_orig = Image.fromarray(arr[:, :, ::-1])  # оригинал
            self._last_screenshot_img  = img.copy()  # превью для отображения

            self.root.after(0, lambda: self._show_preview(photo))
            self._bot_log("✅ Скриншот готов. Можно вырезать паттерн.", "success")

        except Exception as e:
            self._bot_log(f"❌ Ошибка: {e}", "error")

    def _show_preview(self, photo):
        self.bot_preview_label.config(image=photo, text="")
        self.bot_preview_label.image = photo  # Держим ссылку

    def _bot_crop_pattern(self):
        """Открыть диалог вырезки паттерна — проверяем наличие скриншота"""
        if not hasattr(self, "_last_screenshot_orig"):
            self._bot_log("⚠ Сначала нажмите кнопку 'Скриншот'!", "warning")
            self.root.after(0, lambda: tk.messagebox.showwarning(
                "Нет скриншота",
                "Сначала сделайте скриншот экрана BlueStacks.\n\nНажмите кнопку '📸 Скриншот'.",
                parent=self.root
            ))
            return
        self.root.after(0, self._crop_window_new)

    def _crop_window_new(self):
        """Окно вырезки паттерна с перетаскиваемым прямоугольником и выбором действия"""
        import tkinter.messagebox
        from PIL import ImageTk
        from UI.scenario_editor import STEP_TYPES, STEP_TYPE_KEYS

        win = tk.Toplevel(self.root)
        win.title("Вырезать паттерн")
        win.configure(bg=THEME["bg_main"])
        win.resizable(False, False)

        # ── Инструкция ──
        create_label(win,
                     "Нарисуйте прямоугольник на скриншоте. Можно перетащить или изменить размер.",
                     style="dim", bg=THEME["bg_main"]).pack(pady=(6, 2))

        # ── Canvas со скриншотом — показываем оригинал, масштабированный под экран ──
        orig = self._last_screenshot_orig.copy()  # оригинал PIL Image
        display = orig.copy()
        display.thumbnail((900, 500))
        photo = ImageTk.PhotoImage(display)

        # Коэффициент масштаба: display → orig
        scale_x = orig.width  / display.width
        scale_y = orig.height / display.height

        canvas = tk.Canvas(win, width=display.width, height=display.height,
                           bg=THEME["bg_main"], cursor="crosshair")
        canvas.pack(padx=8)
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image = photo

        # Состояние прямоугольника
        rect = {"id": None, "x1": 50, "y1": 50, "x2": 200, "y2": 150}
        drag = {"mode": None, "ox": 0, "oy": 0, "rx1": 0, "ry1": 0, "rx2": 0, "ry2": 0}
        HANDLE = 10  # зона захвата края

        def draw_rect():
            if rect["id"]:
                canvas.delete(rect["id"])
            rect["id"] = canvas.create_rectangle(
                rect["x1"], rect["y1"], rect["x2"], rect["y2"],
                outline=THEME["accent_green"], width=2, dash=(4, 2)
            )

        draw_rect()

        def get_mode(ex, ey):
            x1, y1, x2, y2 = rect["x1"], rect["y1"], rect["x2"], rect["y2"]
            near_l = abs(ex - x1) < HANDLE
            near_r = abs(ex - x2) < HANDLE
            near_t = abs(ey - y1) < HANDLE
            near_b = abs(ey - y2) < HANDLE
            inside = x1 < ex < x2 and y1 < ey < y2

            if near_l and near_t: return "resize_tl"
            if near_r and near_t: return "resize_tr"
            if near_l and near_b: return "resize_bl"
            if near_r and near_b: return "resize_br"
            if near_l: return "resize_l"
            if near_r: return "resize_r"
            if near_t: return "resize_t"
            if near_b: return "resize_b"
            if inside:  return "move"
            return "draw"

        def update_cursor(ex, ey):
            m = get_mode(ex, ey)
            cursors = {
                "move": "fleur",
                "resize_tl": "top_left_corner", "resize_tr": "top_right_corner",
                "resize_bl": "bottom_left_corner", "resize_br": "bottom_right_corner",
                "resize_l": "left_side", "resize_r": "right_side",
                "resize_t": "top_side", "resize_b": "bottom_side",
                "draw": "crosshair",
            }
            canvas.config(cursor=cursors.get(m, "crosshair"))

        def on_motion(e):
            update_cursor(e.x, e.y)

        def on_press(e):
            drag["mode"] = get_mode(e.x, e.y)
            drag["ox"], drag["oy"] = e.x, e.y
            drag["rx1"], drag["ry1"] = rect["x1"], rect["y1"]
            drag["rx2"], drag["ry2"] = rect["x2"], rect["y2"]

        def on_drag(e):
            dx, dy = e.x - drag["ox"], e.y - drag["oy"]
            m = drag["mode"]
            x1, y1, x2, y2 = drag["rx1"], drag["ry1"], drag["rx2"], drag["ry2"]

            if m == "draw":
                rect["x1"], rect["y1"] = drag["ox"], drag["oy"]
                rect["x2"], rect["y2"] = e.x, e.y
            elif m == "move":
                rect["x1"], rect["y1"] = x1 + dx, y1 + dy
                rect["x2"], rect["y2"] = x2 + dx, y2 + dy
            elif m == "resize_l":  rect["x1"] = x1 + dx
            elif m == "resize_r":  rect["x2"] = x2 + dx
            elif m == "resize_t":  rect["y1"] = y1 + dy
            elif m == "resize_b":  rect["y2"] = y2 + dy
            elif m == "resize_tl": rect["x1"], rect["y1"] = x1+dx, y1+dy
            elif m == "resize_tr": rect["x2"], rect["y1"] = x2+dx, y1+dy
            elif m == "resize_bl": rect["x1"], rect["y2"] = x1+dx, y2+dy
            elif m == "resize_br": rect["x2"], rect["y2"] = x2+dx, y2+dy

            draw_rect()

        canvas.bind("<Motion>",         on_motion)
        canvas.bind("<ButtonPress-1>",  on_press)
        canvas.bind("<B1-Motion>",      on_drag)

        # ── Нижняя панель: только имя паттерна + кнопки ──
        bottom = tk.Frame(win, bg=THEME["bg_panel"], padx=12, pady=10)
        bottom.pack(fill=tk.X, padx=8, pady=6)

        row1 = tk.Frame(bottom, bg=THEME["bg_panel"])
        row1.pack(fill=tk.X, pady=2)
        create_label(row1, "Имя паттерна:", style="dim", bg=THEME["bg_panel"]).pack(side=tk.LEFT)
        name_var = tk.StringVar(value="pattern_1")
        tk.Entry(row1, textvariable=name_var, width=22,
                 bg=THEME["bg_input"], fg=THEME["accent_blue"],
                 font=THEME["font_normal"], relief=tk.FLAT,
                 insertbackground=THEME["accent_green"]).pack(side=tk.LEFT, padx=8)

        btn_row = tk.Frame(bottom, bg=THEME["bg_panel"])
        btn_row.pack(fill=tk.X, pady=(8, 0))

        def on_save():
            name = name_var.get().strip().replace(" ", "_")
            if not name:
                tk.messagebox.showwarning("Ошибка", "Введите имя паттерна", parent=win)
                return

            # Нормализуем координаты
            x1 = min(rect["x1"], rect["x2"])
            y1 = min(rect["y1"], rect["y2"])
            x2 = max(rect["x1"], rect["x2"])
            y2 = max(rect["y1"], rect["y2"])

            if x2 - x1 < 5 or y2 - y1 < 5:
                tk.messagebox.showwarning("Ошибка", "Выделите область на скриншоте", parent=win)
                return

            # Масштабируем координаты к оригинальному скриншоту
            rx1, ry1 = int(x1 * scale_x), int(y1 * scale_y)
            rx2, ry2 = int(x2 * scale_x), int(y2 * scale_y)

            cropped   = orig.crop((rx1, ry1, rx2, ry2))
            save_path = (Path(__file__).parent / "processes" / "BOT" / "patterns"
                         / f"{name}.png")
            cropped.save(save_path)
            self._bot_log(f"✅ Паттерн сохранён: {name}.png ({rx2-rx1}x{ry2-ry1}px)", "success")
            win.destroy()

            # Открываем диалог параметров шага с уже подставленным паттерном
            if hasattr(self, "_scenario_editor"):
                from UI.scenario_editor import StepDialog
                step_template = {
                    "type": "find_and_tap",
                    "params": {"pattern": name, "threshold": 0.8,
                               "retries": 3, "retry_delay": 2.0}
                }
                dlg = StepDialog(self.root,
                                 title=f"Настройка шага для паттерна '{name}'",
                                 step=step_template)
                if dlg.result:
                    self._scenario_editor.add_step_direct(dlg.result)
                    self._bot_log(f"➕ Шаг добавлен в сценарий: {name}", "info")

        create_button(btn_row, "💾 Сохранить и добавить в сценарий",
                      on_save, style="start", width=34).pack(side=tk.LEFT)
        create_button(btn_row, "✖ Отмена",
                      win.destroy, width=12).pack(side=tk.LEFT, padx=8)

    def _bot_collect(self):
        if not self.adb.connected_device:
            self._bot_log("❌ Устройство не подключено", "error")
            return
        threading.Thread(target=self._bot_collect_thread, daemon=True).start()

    def _bot_collect_thread(self):
        try:
            from processes.BOT.bot_02_actions import BotActions
            actions = BotActions(self.adb.connected_device, self._bot_log)
            actions.collect_resources()
        except Exception as e:
            self._bot_log(f"❌ Ошибка: {e}", "error")

    def _bot_attack(self):
        if not self.adb.connected_device:
            self._bot_log("❌ Устройство не подключено", "error")
            return
        threading.Thread(target=self._bot_attack_thread, daemon=True).start()

    def _bot_attack_thread(self):
        try:
            from processes.BOT.bot_02_actions import BotActions
            actions = BotActions(self.adb.connected_device, self._bot_log)
            actions.start_attack()
        except Exception as e:
            self._bot_log(f"❌ Ошибка: {e}", "error")

    def _bot_close_popup(self):
        if not self.adb.connected_device:
            self._bot_log("❌ Устройство не подключено", "error")
            return
        threading.Thread(target=self._bot_close_thread, daemon=True).start()

    def _bot_close_thread(self):
        try:
            from processes.BOT.bot_02_actions import BotActions
            actions = BotActions(self.adb.connected_device, self._bot_log)
            actions.close_popup()
        except Exception as e:
            self._bot_log(f"❌ Ошибка: {e}", "error")

    def _bot_start_record(self):
        self._bot_log("ℹ️ Запись сценария пока не реализована.", "warning")

    def _bot_play_record(self):
        self._bot_log("ℹ️ Воспроизведение сценария пока не реализовано.", "warning")

    def _bot_save_record(self):
        self._bot_log("ℹ️ Сохранение сценария пока не реализовано.", "warning")

    def _start_bs_monitor(self):
        """Запускает фоновый мониторинг процесса BlueStacks."""
        self._bs_monitor_active = True
        self._bs_was_running = False

        def _monitor():
            import time
            while self._bs_monitor_active:
                try:
                    is_running = self.bluestacks.is_running()

                    if self._bs_was_running and not is_running:
                        # BlueStacks только что упал
                        msg = "⚠ BlueStacks закрылся неожиданно!"
                        self._log(msg, "error")
                        self._set_status(msg, "error")
                        self._set_stat("BlueStacks", "❌ Закрыт", "error")
                        self._set_stat("ADB", "—", "normal")
                        self._set_stat("Игра", "—", "normal")
                        self.root.after(0, lambda: self.header_status.config(
                            text="● ОСТАНОВЛЕН", fg=THEME["accent_red"]
                        ))

                    self._bs_was_running = is_running
                except Exception:
                    pass
                time.sleep(10)

        threading.Thread(target=_monitor, daemon=True).start()

    def _minimize_other_windows(self):
        """При старте: сворачивает всё, показывает MyBotX + BlueStacks если запущен."""
        try:
            import win32gui, win32con, psutil

            BS_TITLES = ["bluestacks app player", "bluestacks", "hd-player"]
            OUR_TITLE = "mybotx"
            our_hwnd  = None
            bs_hwnd   = None

            # Проверяем запущен ли BlueStacks через процессы
            bs_running = any(
                p.name().lower() in ("hd-player.exe", "bluestacks.exe")
                for p in psutil.process_iter(['name'])
            )

            def cb(hwnd, _):
                nonlocal our_hwnd, bs_hwnd
                title = win32gui.GetWindowText(hwnd).strip()
                if not title:
                    return
                title_lower = title.lower()

                if OUR_TITLE in title_lower:
                    our_hwnd = hwnd
                    return

                if bs_running and any(bs in title_lower for bs in BS_TITLES):
                    bs_hwnd = hwnd
                    return

                if title in ("Program Manager", "Windows Input Experience",
                             "Microsoft Text Input Application"):
                    return

                if win32gui.IsWindowVisible(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

            win32gui.EnumWindows(cb, None)

            # Показываем BlueStacks если запущен
            if bs_hwnd:
                win32gui.ShowWindow(bs_hwnd, win32con.SW_RESTORE)

            # Поднимаем MyBotX
            if our_hwnd:
                win32gui.ShowWindow(our_hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(our_hwnd)
            else:
                self.root.lift()
                self.root.attributes('-topmost', True)
                self.root.after(200, lambda: self.root.attributes('-topmost', False))

        except Exception:
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after(200, lambda: self.root.attributes('-topmost', False))

    def _on_close_user(self):
        """Пользователь закрыл окно — автосохранение сценария, удаляем PID и лог"""
        self._bs_monitor_active = False

        # Автосохранение текущего сценария
        try:
            if hasattr(self, "_scenario_editor"):
                self._scenario_editor._save()
        except Exception:
            pass

        try:
            if self._pid_file.exists():
                self._pid_file.unlink()
        except Exception:
            pass
        try:
            session_logger._cleanup()
        except Exception:
            pass
        self.root.destroy()

    def _build_about_tab(self):
        frame = self.frames["about"]

        center = tk.Frame(frame, bg=THEME["bg_main"])
        center.place(relx=0.5, rely=0.5, anchor="center")

        create_label(center, "⚡ MyBotX", style="title", bg=THEME["bg_main"]).pack(pady=(0, 4))
        create_label(center, "v1.0.0", style="header", bg=THEME["bg_main"]).pack()

        create_separator(center).pack(fill=tk.X, pady=16)

        info = [
            ("Игра",      "Clash of Clans"),
            ("Эмулятор",  "BlueStacks 5"),
            ("Язык",      "Python 3.10+"),
            ("Лицензия",  "MIT"),
            ("Автор",     "Mihasa"),
        ]
        for label, value in info:
            row = tk.Frame(center, bg=THEME["bg_main"])
            row.pack(fill=tk.X, pady=3)
            create_label(row, f"{label}:", style="dim", bg=THEME["bg_main"], width=12, anchor="e").pack(side=tk.LEFT)
            create_label(row, value, style="normal", bg=THEME["bg_main"]).pack(side=tk.LEFT, padx=8)

    # ─────────────────────────────────────────────
    # ЛОГИКА КНОПОК
    # ─────────────────────────────────────────────

    def on_check_button_click(self):
        if self.is_checking:
            return
        thread = threading.Thread(target=self._check_thread, daemon=True)
        thread.start()

    def _check_thread(self):
        self.is_checking = True
        self.root.after(0, self._ui_start)

        try:
            self._log("=" * 50, "dim")
            self._log("🔍 ПРОВЕРКА PYTHON ПАКЕТОВ", "info")
            self._log("=" * 50, "dim")

            # Читаем requirements.txt с версиями
            import subprocess, sys
            req_path = Path(__file__).parent / "requirements.txt"
            required = {}  # {name: version}
            if req_path.exists():
                for line in req_path.read_text().splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "==" in line:
                            name, ver = line.split("==", 1)
                            required[name.strip().lower()] = ver.strip()
                        else:
                            required[line.lower()] = None

            # Получаем установленные пакеты с версиями
            import json
            import sys as _sys

            # Если запущено из PyInstaller EXE — все пакеты встроены
            if getattr(_sys, 'frozen', False):
                self._log("✅ Запущено из EXE — все пакеты встроены", "success")
                for pkg_name, req_ver in required.items():
                    self._log(f"  ✅ {pkg_name} (встроен)", "success")
                self.checker = type("Checker", (), {
                    "missing_packages": [],
                    "installed_packages": list(required.keys()),
                    "required_packages": list(required.keys()),
                })()
                inst_count = len(required)
                self.root.after(0, lambda: self.status_labels["packages"].config(
                    text=f"✅ {inst_count}/{inst_count} встроено",
                    fg=THEME["accent_green"]
                ))
            else:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "list", "--format=json"],
                    capture_output=True, text=True, timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                installed_map = {}
                if result.returncode == 0:
                    for pkg in json.loads(result.stdout):
                        installed_map[pkg["name"].lower()] = pkg["version"]

                missing = []
                for pkg_name, req_ver in required.items():
                    if pkg_name in installed_map:
                        inst_ver = installed_map[pkg_name]
                        if req_ver and inst_ver != req_ver:
                            self._log(f"  ⚠️ {pkg_name} — установлен {inst_ver}, нужен {req_ver}", "warning")
                            missing.append(pkg_name)
                        else:
                            self._log(f"  ✅ {pkg_name}=={inst_ver}", "success")
                    else:
                        self._log(f"  ❌ {pkg_name} — не установлен", "error")
                        missing.append(pkg_name)

                self._log("", "dim")
                if missing:
                    self._log(f"❌ Не установлено: {len(missing)} пакетов", "error")
                else:
                    self._log("✅ Все пакеты установлены!", "success")

                self.checker = type("Checker", (), {
                    "missing_packages": missing,
                    "installed_packages": [p for p in required if p not in missing],
                    "required_packages": list(required.keys()),
                })()

                inst_count = len(required) - len(missing)
                self.root.after(0, lambda: self.status_labels["packages"].config(
                    text=f"✅ {inst_count}/{len(required)} установлено",
                    fg=THEME["accent_green"] if not missing else THEME["accent_red"]
                ))
                if missing:
                    self.root.after(0, lambda: self.install_btn.config(
                        state=tk.NORMAL, fg=THEME["accent_blue"]
                    ))

            self._log("", "dim")
            self._log("🔍 ПОИСК BLUESTACKS", "info")
            self._log("=" * 50, "dim")

            if self.bluestacks.is_installed():
                path = self.bluestacks.get_path()
                self._log(f"✅ BlueStacks найден: {path}", "success")
                self.root.after(0, lambda: self.status_labels["bluestacks"].config(
                    text="✅ Установлен", fg=THEME["accent_green"]
                ))
                self.root.after(0, lambda: self.status_labels["path"].config(
                    text=str(path)[:50], fg=THEME["text_secondary"]
                ))
            else:
                self._log("❌ BlueStacks не найден", "error")
                self.root.after(0, lambda: self.status_labels["bluestacks"].config(
                    text="❌ Не найден", fg=THEME["accent_red"]
                ))

            if self.bluestacks.is_running():
                self._log("✅ BlueStacks запущен", "success")
                self.root.after(0, lambda: self.status_labels["bluestacks"].config(
                    text="✅ Запущен", fg=THEME["accent_green"]
                ))
            else:
                self._log("⚠️ BlueStacks не запущен", "warning")

            self._log("=" * 50, "dim")
            self._log("✅ ПРОВЕРКА ЗАВЕРШЕНА", "success")
            self._log("=" * 50, "dim")

        except Exception as e:
            self._log(f"❌ ОШИБКА: {e}", "error")
        finally:
            self.is_checking = False
            self.root.after(0, self._ui_end)

    def on_uninstall_button_click(self):
        thread = threading.Thread(target=self._uninstall_thread, daemon=True)
        thread.start()

    def _uninstall_thread(self):
        self.is_checking = True
        self.root.after(0, self._ui_start)
        try:
            # Читаем только НАШИ пакеты из requirements.txt
            from pathlib import Path
            import subprocess
            req_file = Path(__file__).parent / "requirements.txt"
            if not req_file.exists():
                self._log("❌ requirements.txt не найден", "error")
                return

            packages = []
            for line in req_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    # Убираем версию: psutil==5.9.6 → psutil
                    pkg = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
                    if pkg:
                        packages.append(pkg)

            if not packages:
                self._log("⚠️ Нет пакетов для удаления", "warning")
                return

            self._log(f"🗑 Удаляем {len(packages)} пакетов: {', '.join(packages)}", "warning")

            for pkg in packages:
                result = subprocess.run(
                    ["pip", "uninstall", pkg, "-y"],
                    capture_output=True, text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    self._log(f"✅ {pkg} удалён", "success")
                else:
                    self._log(f"⚠️ {pkg}: не установлен или ошибка", "warning")

            self._log(f"✅ Готово. Удалено: {len(packages)} пакетов", "success")
        except Exception as e:
            self._log(f"❌ Ошибка: {e}", "error")
        finally:
            self.is_checking = False
            self.root.after(0, self._ui_end)

    def on_install_button_click(self):
        if not self.checker or not self.checker.missing_packages:
            return
        thread = threading.Thread(target=self._install_thread, daemon=True)
        thread.start()

    def _install_thread(self):
        self.is_checking = True
        self.root.after(0, self._ui_start)
        try:
            self._log("📦 Установка пакетов...", "info")
            if self.checker.install_missing_packages():
                self._log("✅ Пакеты установлены!", "success")
            else:
                self._log("❌ Ошибка установки", "error")
        finally:
            self.is_checking = False
            self.root.after(0, self._ui_end)

    def on_clear_logs(self):
        self.log_text.delete(1.0, tk.END)
        for lbl in self.status_labels.values():
            lbl.config(text="—", fg=THEME["text_primary"])

    def on_screenshot(self):
        """Сделать скриншот и сохранить для отладки"""
        if not self.adb.connected_device:
            self._log("❌ Устройство не подключено", "error")
            return
        thread = threading.Thread(target=self._screenshot_thread, daemon=True)
        thread.start()

    def _screenshot_thread(self):
        try:
            from processes.SCREENSHOT import ScreenshotCapture as BotScreenshot
            from pathlib import Path
            import time
            sc = BotScreenshot(self.adb.connected_device, self._log_direct)
            path = str(Path(__file__).parent / "processes" / "BOT" / "patterns" / f"screenshot_{int(time.time())}.png")
            if sc.capture_and_save(path):
                self._log(f"✅ Скриншот сохранён в patterns/", "success")
            else:
                self._log("❌ Не удалось сделать скриншот", "error")
        except Exception as e:
            self._log(f"❌ Ошибка: {e}", "error")

    def on_start_bot(self):
        thread = threading.Thread(target=self._start_thread, daemon=True)
        thread.start()

    def _start_thread(self):
        import time
        import json
        self._set_status("🔍 Проверяем BlueStacks...", "info")

        if not self.bluestacks.is_installed():
            self._set_status("❌ BlueStacks не установлен", "error")
            self._set_stat("BlueStacks", "❌ Нет", "error")
            return

        if not self.bluestacks.is_running():
            self._set_status("⚙️ Запускаем BlueStacks...", "warning")
            self._set_stat("BlueStacks", "⚙️ Запуск...", "warning")
            success, _ = self.bluestacks.launch()
            if not success:
                self._set_status("❌ Не удалось запустить BlueStacks", "error")
                self._set_stat("BlueStacks", "❌ Ошибка", "error")
                return
            time.sleep(15)

        self._set_stat("BlueStacks", "✅ Запущен", "success")
        self._set_status("🔌 Подключаемся к ADB...", "info")
        self._set_stat("ADB", "⏳ Подключение...", "warning")

        success, serial = self.adb.connect_to_bluestacks_with_wait(
            wait_timeout=15, retry_interval=2
        )
        if not success:
            self._set_status("❌ Не удалось подключиться к ADB", "error")
            self._set_stat("ADB", "❌ Ошибка", "error")
            return

        self._set_stat("ADB", f"✅ {serial}", "success")
        self._set_status("🎮 Запускаем Clash of Clans...", "info")
        self._set_stat("Игра", "⏳ Запуск...", "warning")

        # Фиксируем разрешение в фоне — не блокируем запуск игры
        def _fix_res():
            self.bluestacks.set_fixed_resolution(serial, self._log_direct)
        threading.Thread(target=_fix_res, daemon=True).start()

        success = self.adb.launch_app("com.supercell.clashofclans", "com.supercell.titan.GameApp")

        if success:
            self._set_status("✅ Clash of Clans запущен!", "success")
            self._set_stat("Игра", "✅ Запущена", "success")
            self.root.after(0, lambda: self.header_status.config(
                text="● РАБОТАЕТ", fg=THEME["accent_green"]
            ))
            # Ждём загрузки игры и центрируем базу
            threading.Thread(target=self._wait_and_center, daemon=True).start()
        else:
            self._set_status("❌ Ошибка при запуске игры", "error")
            self._set_stat("Игра", "❌ Ошибка", "error")

        self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))

    def _wait_and_center(self):
        """Выполняет последовательность запуска из DEV настроек."""
        import time
        import json

        # Загружаем параметры из base_constants.json
        constants_path = Path(__file__).parent.parent / "CONFIG" / "base_constants.json"
        try:
            with open(constants_path, encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}

        wait_secs = int(cfg.get("startup_wait", 15))
        steps = cfg.get("startup_steps", [
            {"pattern": "(нет)", "action": "zoom_out"},
            {"pattern": "(нет)", "action": "center_base"},
        ])

        self._set_status(f"⏳ Ждём загрузки игры ({wait_secs} сек)...", "info")
        time.sleep(wait_secs)

        if not self.adb.connected_device:
            return

        import cv2
        patterns_dir = Path(__file__).parent / "processes" / "BOT" / "patterns"

        for i, step in enumerate(steps):
            pattern_name = step.get("pattern", "(нет)")
            action = step.get("action", "skip")

            self._set_status(f"🚀 Шаг {i+1}: паттерн='{pattern_name}' → {action}", "info")

            # Если паттерн задан — ждём его появления
            if pattern_name and pattern_name != "(нет)":
                pattern_path = patterns_dir / f"{pattern_name}.png"
                template = cv2.imread(str(pattern_path)) if pattern_path.exists() else None

                if template is not None:
                    found = False
                    for attempt in range(24):  # до 2 минут
                        try:
                            from processes.BOT.bot_01_screenshot import BotScreenshot
                            ss = BotScreenshot(self.adb.connected_device, None)
                            frame = ss.capture()
                            if frame is not None:
                                res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
                                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                                if max_val >= 0.7:
                                    found = True
                                    self._set_status(f"✅ Паттерн '{pattern_name}' найден ({max_val:.2f})", "success")
                                    # Если действие — нажать на паттерн
                                    if action == "tap":
                                        h, w = template.shape[:2]
                                        cx = max_loc[0] + w // 2
                                        cy = max_loc[1] + h // 2
                                        from processes.SCENARIO.scenario_04_adb_actions import do_tap
                                        do_tap(self.adb.connected_device, cx, cy)
                                        time.sleep(1)
                                    break
                        except Exception:
                            pass
                        time.sleep(5)

                    if not found:
                        self._set_status(f"⚠ Паттерн '{pattern_name}' не найден, пропускаем шаг", "warning")
                        continue

            # Выполняем действие
            if action == "zoom_out":
                if hasattr(self, "_base_zoom_out"):
                    self._base_zoom_out()
                    time.sleep(1)
            elif action == "zoom_in":
                if hasattr(self, "_base_zoom_in"):
                    self._base_zoom_in()
                    time.sleep(1)
            elif action == "center_base":
                self._set_status("🎯 Центрируем базу...", "info")
                if hasattr(self, "_base_find_center"):
                    self._base_find_center()
            elif action == "wait_5s":
                time.sleep(5)
            elif action == "tap":
                pass  # уже выполнено выше при нахождении паттерна

    def _resize_bluestacks_window(self, width: int, height: int):
        """Изменяет размер окна BlueStacks через win32api"""
        try:
            import ctypes
            user32 = ctypes.windll.user32

            # Ищем окно BlueStacks по заголовку
            bs_titles = ["BlueStacks", "BlueStacks App Player", "HD-Player"]
            hwnd = None
            for title in bs_titles:
                hwnd = user32.FindWindowW(None, title)
                if hwnd:
                    break

            if not hwnd:
                # Перебираем все окна с частичным совпадением
                import ctypes.wintypes
                found = []

                @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
                def enum_cb(hwnd, lParam):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buf = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buf, length + 1)
                        if "BlueStacks" in buf.value or "HD-Player" in buf.value:
                            found.append(hwnd)
                    return True

                user32.EnumWindows(enum_cb, 0)
                hwnd = found[0] if found else None

            if not hwnd:
                self._set_status("⚠ Окно BlueStacks не найдено для изменения размера", "warning")
                return

            # Восстанавливаем окно если свёрнуто
            SW_RESTORE = 9
            user32.ShowWindow(hwnd, SW_RESTORE)

            # Устанавливаем размер (SWP_NOMOVE = не двигать, только размер)
            SWP_NOMOVE    = 0x0002
            SWP_NOZORDER  = 0x0004
            user32.SetWindowPos(hwnd, None, 0, 0, width, height,
                                SWP_NOMOVE | SWP_NOZORDER)
            self._set_status(f"✅ BlueStacks: {width}×{height}px", "success")

        except Exception as e:
            self._set_status(f"⚠ Resize: {e}", "warning")

    # ─────────────────────────────────────────────
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ─────────────────────────────────────────────

    def _log(self, message: str, tag: str = "info"):
        self.root.after(0, lambda: self._append_log(message, tag))

    def _log_direct(self, message: str):
        """Для передачи как callback в BOT модули"""
        self._log(message, "info")

    def _append_log(self, message: str, tag: str):
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        try:
            if self._session_logger:
                self._session_logger.write(message, tag)
        except Exception:
            pass

    def _set_stat(self, key: str, text: str, style: str = "normal"):
        """Обновить статус-метку внизу главной вкладки"""
        colors = {
            "success": THEME["accent_green"],
            "error":   THEME["accent_red"],
            "warning": THEME["accent_orange"],
            "info":    THEME["accent_blue"],
            "normal":  THEME["text_primary"],
        }
        fg = colors.get(style, THEME["text_primary"])
        if hasattr(self, "stats_labels") and key in self.stats_labels:
            self.root.after(0, lambda t=text, c=fg: self.stats_labels[key].config(text=t, fg=c))

    def _set_status(self, text: str, style: str = "normal"):
        colors = {
            "success": THEME["accent_green"],
            "error":   THEME["accent_red"],
            "warning": THEME["accent_orange"],
            "info":    THEME["accent_blue"],
            "normal":  THEME["text_secondary"],
        }
        fg = colors.get(style, THEME["text_secondary"])
        self.root.after(0, lambda: self.statusbar.config(text=text, fg=fg))

    def _ui_start(self):
        self.check_btn.config(state=tk.DISABLED, fg=THEME["text_disabled"])
        self.progress_bar.config(bg=THEME["accent_green"])

    def _ui_end(self):
        self.check_btn.config(state=tk.NORMAL, fg=THEME["accent_blue"])
        self.progress_bar.config(bg=THEME["accent_blue"])


def _parse_number(value: str):
    """Преобразует строку в int или float. Если не получается — возвращает строку."""
    try:
        if "." in value:
            return float(value)
        return int(value)
    except (ValueError, TypeError):
        return value


def main():
    root = tk.Tk()
    BotMainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
