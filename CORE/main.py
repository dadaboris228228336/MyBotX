#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🖥️ MyBotX GUI v3.0.0 - Геймерский интерфейс
"""

import sys
import time
import tkinter as tk
import threading
from pathlib import Path
from tkinter import scrolledtext

try:
    from dependency_checker import DependencyChecker
    from bluestacks_manager import BlueStacksManager
    from advanced_adb_manager import AdvancedADBManager
    from UI.theme import THEME
    from UI.widgets import create_button, create_label, create_frame, create_separator
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from dependency_checker import DependencyChecker
    from bluestacks_manager import BlueStacksManager
    from advanced_adb_manager import AdvancedADBManager
    from UI.theme import THEME
    from UI.widgets import create_button, create_label, create_frame, create_separator


class BotMainWindow:

    def __init__(self, root):
        self.root = root
        self.root.title("MyBotX v3.0.0")
        self.root.geometry("960x620")
        self.root.configure(bg=THEME["bg_main"])
        self.root.resizable(False, False)

        self.checker = None
        self.is_checking = False
        self.bluestacks = BlueStacksManager()
        self.adb = AdvancedADBManager()

        self._build_ui()

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
            text="v3.0.0  |  Clash of Clans Bot",
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
            "main":  tk.Frame(self.tab_content, bg=THEME["bg_main"]),
            "check": tk.Frame(self.tab_content, bg=THEME["bg_main"]),
            "about": tk.Frame(self.tab_content, bg=THEME["bg_main"]),
        }

        # Кнопки вкладок
        self.tab_buttons = {}
        tabs = [("main", "🏠  ОСНОВНОЕ"), ("check", "🔍  ПРОВЕРКА"), ("about", "ℹ️  О ПРОГРАММЕ")]
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

        create_separator(self.root).pack(fill=tk.X)

        # Наполняем вкладки
        self._build_main_tab()
        self._build_check_tab()
        self._build_about_tab()

        # Показываем первую вкладку
        self._switch_tab("main")

    def _switch_tab(self, key):
        """Переключение вкладки"""
        for k, frame in self.frames.items():
            frame.pack_forget()
        self.frames[key].pack(fill=tk.BOTH, expand=True)

        for k, btn in self.tab_buttons.items():
            if k == key:
                btn.config(fg=THEME["accent_blue"], bg=THEME["bg_card"])
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

        for text, val in [("BlueStacks", "—"), ("ADB", "—"), ("Игра", "—")]:
            col = tk.Frame(stats, bg=THEME["bg_panel"])
            col.pack(side=tk.LEFT, expand=True, pady=10)
            create_label(col, text, style="dim", bg=THEME["bg_panel"]).pack()
            lbl = create_label(col, val, style="normal", bg=THEME["bg_panel"])
            lbl.pack()

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
    # ВКЛАДКА: О ПРОГРАММЕ
    # ─────────────────────────────────────────────

    def _build_about_tab(self):
        frame = self.frames["about"]

        center = tk.Frame(frame, bg=THEME["bg_main"])
        center.place(relx=0.5, rely=0.5, anchor="center")

        create_label(center, "⚡ MyBotX", style="title", bg=THEME["bg_main"]).pack(pady=(0, 4))
        create_label(center, "v3.0.0", style="header", bg=THEME["bg_main"]).pack()

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

            self.checker = DependencyChecker("requirements.txt")
            self.checker.check_dependencies()

            installed = len(self.checker.installed_packages)
            missing = len(self.checker.missing_packages)
            self.root.after(0, lambda: self.status_labels["packages"].config(
                text=f"✅ {installed} уст. / ❌ {missing} нет",
                fg=THEME["accent_green"] if missing == 0 else THEME["accent_red"]
            ))
            if missing > 0:
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
            self._log("🗑 Удаление пакетов...", "warning")
            import subprocess
            packages = ["psutil"]
            for pkg in packages:
                result = subprocess.run(
                    ["pip", "uninstall", pkg, "-y"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    self._log(f"✅ {pkg} удалён", "success")
                else:
                    self._log(f"⚠️ {pkg}: {result.stderr.strip()}", "warning")
            self._log("✅ Готово", "success")
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

    def on_start_bot(self):
        thread = threading.Thread(target=self._start_thread, daemon=True)
        thread.start()

    def _start_thread(self):
        import time
        self._set_status("🔍 Проверяем BlueStacks...", "info")

        if not self.bluestacks.is_installed():
            self._set_status("❌ BlueStacks не установлен", "error")
            return

        if not self.bluestacks.is_running():
            self._set_status("⚙️ Запускаем BlueStacks...", "warning")
            success, _ = self.bluestacks.launch()
            if not success:
                self._set_status("❌ Не удалось запустить BlueStacks", "error")
                return
            time.sleep(15)

        self._set_status("🔌 Подключаемся к ADB...", "info")
        success, serial = self.adb.connect_to_bluestacks_with_wait(
            wait_timeout=15, retry_interval=2
        )
        if not success:
            self._set_status("❌ Не удалось подключиться к ADB", "error")
            return

        self._set_status("🎮 Запускаем Clash of Clans...", "info")
        success = self.adb.launch_app("com.supercell.clashofclans", "com.supercell.titan.GameApp")

        if success:
            self._set_status("✅ Clash of Clans запущен!", "success")
            self.root.after(0, lambda: self.header_status.config(
                text="● РАБОТАЕТ", fg=THEME["accent_green"]
            ))
        else:
            self._set_status("❌ Ошибка при запуске игры", "error")

        self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))

    # ─────────────────────────────────────────────
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ─────────────────────────────────────────────

    def _log(self, message: str, tag: str = "info"):
        self.root.after(0, lambda: self._append_log(message, tag))

    def _append_log(self, message: str, tag: str):
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)

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


def main():
    root = tk.Tk()
    BotMainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
