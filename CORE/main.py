#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🖥️ MyBot GUI v3.0.0 - Главное приложение с графическим интерфейсом

ОСНОВНЫЕ ПРОЦЕССЫ ПО ПОРЯДКУ:
1. Инициализация GUI (создание окна, импорт модулей, настройка менеджеров)
2. Настройка стилей (темы, шрифты, цвета)
3. Создание виджетов (вкладки, кнопки, текстовые поля)
4. Создание вкладки ПРОВЕРКА (кнопки управления, статус, логи)
5. Создание вкладки ОСНОВНОЕ (кнопка СТАРТ, статусбар)
6. Создание вкладки О ПРОГРАММЕ (информация о версии)
7. Обработка кнопки "Проверить всё" (запуск проверки в потоке)
8. Проверка зависимостей в потоке (Python пакеты + BlueStacks)
9. Обработка кнопки "Установить пакеты" (установка через pip)
10. Обработка кнопки СТАРТ (запуск игры)
11. Запуск бота в потоке (проверка BS -> подключение ADB -> запуск игры)
12. Обновление UI (логи, статусы, прогресс-бар)
13. Очистка логов (сброс всех сообщений)
"""

import sys
import time
import tkinter as tk
import threading
from pathlib import Path
from tkinter import ttk, scrolledtext, messagebox

try:
    from dependency_checker import DependencyChecker
    from bluestacks_manager import BlueStacksManager
    from advanced_adb_manager import AdvancedADBManager
except ImportError:
    # Если не получается импортировать, добавляем путь
    sys.path.insert(0, str(Path(__file__).parent))
    from dependency_checker import DependencyChecker
    from bluestacks_manager import BlueStacksManager
    from advanced_adb_manager import AdvancedADBManager


class BotMainWindow:
    """Главное окно приложения бота с автопоиском BlueStacks"""

    def __init__(self, root):
        """ПРОЦЕСС 1: Инициализация GUI (окно, менеджеры, автопоиск BlueStacks)"""
        self.root = root
        self.root.title("MyBot - Управление зависимостями")
        self.root.geometry("900x600")

        self.checker = None
        self.is_checking = False

        # ← Автоматический поиск при инициализации!
        self.bluestacks = BlueStacksManager()
        self.adb = AdvancedADBManager()

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        """ПРОЦЕСС 2: Настройка визуальных стилей (темы, шрифты, цвета)"""
        style = ttk.Style()

        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', padding=[20, 10])
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))

    def create_widgets(self):
        """ПРОЦЕСС 3: Создание основных виджетов интерфейса (вкладки, заголовок)"""
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        header_label = ttk.Label(
            header_frame,
            text="🤖 MyBot - Управление зависимостями",
            style='Header.TLabel'
        )
        header_label.pack(side=tk.LEFT)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_main_tab()
        self.create_check_tab()
        self.create_about_tab()

    def create_check_tab(self):
        """ПРОЦЕСС 4: Создание вкладки ПРОВЕРКА (кнопки, статус, логи)"""
        check_frame = ttk.Frame(self.notebook)
        self.notebook.add(check_frame, text="✓ ПРОВЕРКА")

        # Верхняя панель с кнопками управления
        button_frame = ttk.LabelFrame(
            check_frame,
            text="Управление",
            padding=10
        )
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # ✅ ИСПРАВЛЕННАЯ КНОПКА - Теперь ищет BlueStacks!
        self.check_btn = ttk.Button(
            button_frame,
            text="🔍 Проверить всё",
            command=self.on_check_button_click,
            width=30
        )
        self.check_btn.pack(side=tk.LEFT, padx=5)

        self.install_btn = ttk.Button(
            button_frame,
            text="📦 Установить пакеты",
            command=self.on_install_button_click,
            width=30,
            state=tk.DISABLED
        )
        self.install_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Очистить логи",
            command=self.on_clear_logs,
            width=20
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Информационная панель со статусом
        info_frame = ttk.LabelFrame(
            check_frame,
            text="Статус",
            padding=10
        )
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        # Статистика пакетов Python
        status_subframe = ttk.Frame(info_frame)
        status_subframe.pack(fill=tk.X, pady=5)

        ttk.Label(status_subframe, text="Python пакетов:").pack(
            side=tk.LEFT, padx=5)
        self.status_required = ttk.Label(
            status_subframe,
            text="—",
            style='Status.TLabel',
            foreground="blue"
        )
        self.status_required.pack(side=tk.LEFT, padx=5)

        ttk.Label(status_subframe, text="Установлено:").pack(
            side=tk.LEFT, padx=20)
        self.status_installed = ttk.Label(
            status_subframe,
            text="—",
            style='Status.TLabel',
            foreground="green"
        )
        self.status_installed.pack(side=tk.LEFT, padx=5)

        ttk.Label(status_subframe, text="Недостаёт:").pack(
            side=tk.LEFT, padx=20)
        self.status_missing = ttk.Label(
            status_subframe,
            text="—",
            style='Status.TLabel',
            foreground="red"
        )
        self.status_missing.pack(side=tk.LEFT, padx=5)

        # Статус BlueStacks
        game_status_frame = ttk.Frame(info_frame)
        game_status_frame.pack(fill=tk.X, pady=5)

        ttk.Label(game_status_frame, text="BlueStacks:").pack(
            side=tk.LEFT, padx=5)
        self.game_status = ttk.Label(
            game_status_frame,
            text="—",
            style='Status.TLabel',
            foreground="gray"
        )
        self.game_status.pack(side=tk.LEFT, padx=5)

        # ✅ НОВОЕ - Статус найденного пути
        path_status_frame = ttk.Frame(info_frame)
        path_status_frame.pack(fill=tk.X, pady=5)

        ttk.Label(path_status_frame, text="Путь BlueStacks:").pack(
            side=tk.LEFT, padx=5)
        self.path_status = ttk.Label(
            path_status_frame,
            text="—",
            style='Status.TLabel',
            foreground="blue"
        )
        self.path_status.pack(side=tk.LEFT, padx=5)

        # Прогресс-бар
        progress_subframe = ttk.Frame(info_frame)
        progress_subframe.pack(fill=tk.X, pady=5)

        self.progress = ttk.Progressbar(
            progress_subframe,
            mode='indeterminate',
            length=400
        )
        self.progress.pack(fill=tk.X)

        # Панель с логами
        log_frame = ttk.LabelFrame(
            check_frame,
            text="Логи проверки",
            padding=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            height=15,
            font=('Courier', 9),
            bg='#f5f5f5'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('warning', foreground='orange')
        self.log_text.tag_config('info', foreground='blue')

    def create_main_tab(self):
        """ПРОЦЕСС 5: Создание вкладки ОСНОВНОЕ (кнопка СТАРТ, статусбар)"""
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="🏠 ОСНОВНОЕ")

        header_label = ttk.Label(
            main_frame,
            text="🤖 MyBot",
            font=('Arial', 24, 'bold')
        )
        header_label.pack(pady=50)

        self.start_btn = ttk.Button(
            main_frame,
            text="▶️ СТАРТ",
            command=self.on_start_bot,
            width=30
        )
        self.start_btn.pack(pady=20)

        self.statusbar = ttk.Label(
            main_frame,
            text="Готово",
            font=('Arial', 10),
            foreground="gray"
        )
        self.statusbar.pack(pady=10)

    def create_about_tab(self):
        """ПРОЦЕСС 6: Создание вкладки О ПРОГРАММЕ (информация о версии)"""
        about_frame = ttk.Frame(self.notebook)
        self.notebook.add(about_frame, text="ℹ️ О программе")

        infotext = ("MyBot v3.0.0\nPython 3.10+\nMIT License\n\n"
                    "С автоматическим поиском BlueStacks!")
        label = ttk.Label(
            about_frame,
            text=infotext,
            font=('Arial', 10),
            justify=tk.LEFT
        )
        label.pack(padx=20, pady=20)

    def on_check_button_click(self):
        """ПРОЦЕСС 7: Обработка кнопки 'Проверить всё' (запуск проверки в потоке)"""
        if self.is_checking:
            messagebox.showwarning("Внимание", "Проверка уже выполняется!")
            return

        thread = threading.Thread(target=self.check_dependencies_thread)
        thread.daemon = True
        thread.start()

    def check_dependencies_thread(self):
        """ПРОЦЕСС 8: Проверка зависимостей в потоке (Python пакеты + BlueStacks)"""
        self.is_checking = True

        self.root.after(0, self.update_ui_checking_start)

        try:
            # ============================================
            # 1️⃣ ПРОВЕРКА PYTHON ПАКЕТОВ
            # ============================================
            self.root.after(0, lambda: self.append_log("=" * 60, 'info'))
            self.root.after(0, lambda: self.append_log(
                "🔍 ПРОВЕРКА PYTHON ПАКЕТОВ", 'info'))
            self.root.after(0, lambda: self.append_log("=" * 60, 'info'))

            self.checker = DependencyChecker("requirements.txt")
            self.checker.check_dependencies()

            self.root.after(0, self.update_ui_with_results)

            # ============================================
            # 2️⃣ АВТОПОИСК И ПРОВЕРКА BlueStacks ✅ НОВОЕ!
            # ============================================
            self.root.after(0, lambda: self.append_log("", 'info'))
            self.root.after(0, lambda: self.append_log("=" * 60, 'info'))
            self.root.after(0, lambda: self.append_log(
                "🔍 АВТОПОИСК BlueStacks", 'info'))
            self.root.after(0, lambda: self.append_log("=" * 60, 'info'))

            # Проверяем установку
            if self.bluestacks.is_installed():
                path = self.bluestacks.get_path()
                self.root.after(0, lambda: self.append_log(
                    "✅ BlueStacks найден!", 'success'))
                self.root.after(0, lambda: self.append_log(
                    "   Путь: {}".format(path), 'info'))
                self.root.after(0, lambda: self.path_status.config(
                    text=path, foreground="green"))
                self.root.after(0, lambda: self.game_status.config(
                    text="✓ Установлен", foreground="green"))
            else:
                self.root.after(0, lambda: self.append_log(
                    "❌ BlueStacks не найден", 'error'))
                self.root.after(0, lambda: self.path_status.config(
                    text="Не найден", foreground="red"))
                self.root.after(0, lambda: self.game_status.config(
                    text="✗ Не установлен", foreground="red"))

            # Проверяем запущен ли
            if self.bluestacks.is_running():
                self.root.after(0, lambda: self.append_log(
                    "✅ BlueStacks запущен", 'success'))
                self.root.after(0, lambda: self.game_status.config(
                    text="✓ Запущен", foreground="green"))
            else:
                msg = "⚠️ BlueStacks не запущен (но можно запустить)"
                self.root.after(0, lambda: self.append_log(msg, 'warning'))
                self.root.after(0, lambda: self.game_status.config(
                    text="⏸ Не запущен", foreground="orange"))

            # Показываем все найденные пути
            all_paths = self.bluestacks.get_all_found_paths()
            if all_paths and len(all_paths) > 1:
                self.root.after(0, lambda: self.append_log(
                    "\n📍 Найдено несколько вариантов:", 'info'))
                for i, path in enumerate(all_paths, 1):
                    self.root.after(0, lambda p=path, n=i: self.append_log(
                        "   {}. {}".format(n, p), 'info'))

            self.root.after(0, lambda: self.append_log("", 'info'))
            self.root.after(0, lambda: self.append_log("=" * 60, 'info'))
            self.root.after(0, lambda: self.append_log(
                "✅ ПРОВЕРКА ЗАВЕРШЕНА", 'success'))
            self.root.after(0, lambda: self.append_log("=" * 60, 'info'))

        except Exception as error:
            error_msg = str(error)
            self.root.after(0, lambda: self.append_log(
                "❌ ОШИБКА: {}".format(error_msg), 'error'))

        finally:
            self.is_checking = False
            self.root.after(0, self.update_ui_checking_end)

    def on_install_button_click(self):
        """ПРОЦЕСС 9: Обработка кнопки 'Установить пакеты' (установка через pip)"""
        if not self.checker or not self.checker.missing_packages:
            messagebox.showinfo("Информация", "Нет недостающих пакетов!")
            return

        thread = threading.Thread(target=self.install_packages_thread)
        thread.daemon = True
        thread.start()

    def install_packages_thread(self):
        """Установка пакетов"""
        self.is_checking = True
        self.root.after(0, self.update_ui_checking_start)

        try:
            self.append_log("Установка пакетов...", 'info')

            if self.checker.install_missing_packages():
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успех", "Пакеты установлены!"))
            else:
                self.root.after(0, lambda: self.append_log(
                    "Ошибка при установке пакетов", 'error'))
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка", "Не удалось установить пакеты!"))

        finally:
            self.is_checking = False
            self.root.after(0, self.update_ui_checking_end)

    def on_clear_logs(self):
        """ПРОЦЕСС 13: Очистка всех логов и сброс статусов"""
        self.log_text.delete(1.0, tk.END)
        self.status_required.config(text="—")
        self.status_installed.config(text="—")
        self.status_missing.config(text="—")
        self.game_status.config(text="—", foreground="gray")
        self.path_status.config(text="—", foreground="gray")

    def on_start_bot(self):
        """ПРОЦЕСС 10: Обработка кнопки СТАРТ """
        thread = threading.Thread(target=self.start_bot_thread)
        thread.daemon = True
        thread.start()

    def start_bot_thread(self):
        """ПРОЦЕСС 11: Запуск бота в потоке (проверка BS -> подключение ADB -> запуск игры)"""
        import time  # Локальный импорт для надежности
        try:
            self.root.after(0, lambda: self.statusbar.config(
                text="🔍 Проверяем BlueStacks...", foreground="blue"
            ))

            if not self.bluestacks.is_installed():
                self.root.after(0, lambda: self.statusbar.config(
                    text="❌ BlueStacks не установлен", foreground="red"
                ))
                return

            if not self.bluestacks.is_running():
                self.root.after(0, lambda: self.statusbar.config(
                    text="⚙️ Запускаем BlueStacks...", foreground="blue"
                ))
                success, message = self.bluestacks.launch()

                if not success:
                    self.root.after(0, lambda: self.statusbar.config(
                        text="❌ Не удалось запустить BlueStacks",
                        foreground="red"
                    ))
                    return

                time.sleep(15)

            self.root.after(0, lambda: self.statusbar.config(
                text="🔌 Подключаемся к ADB...", foreground="blue"
            ))

            # Быстрая проверка - если BlueStacks не запущен, не тратим время
            if not self.bluestacks.is_running():
                self.root.after(0, lambda: self.statusbar.config(
                    text="❌ BlueStacks не запущен", foreground="red"
                ))
                return

            # Если BlueStacks запущен, пробуем подключиться
            success, serial = self.adb.connect_to_bluestacks_with_wait(
                wait_timeout=15,  # Короткий таймаут
                retry_interval=2  # Проверяем чаще
            )

            if not success:
                self.root.after(0, lambda: self.statusbar.config(
                    text="❌ Не удалось подключиться", foreground="red"
                ))
                return

            self.root.after(0, lambda: self.statusbar.config(
                text="🎮 Запускаем Clash of Clans...", foreground="blue"
            ))

            package = "com.supercell.clashofclans"
            activity = "com.supercell.titan.GameApp"

            success = self.adb.launch_app(package, activity)

            if success:
                self.root.after(0, lambda: self.statusbar.config(
                    text="✅ Clash of Clans запущен!", foreground="green"
                ))
            else:
                self.root.after(0, lambda: self.statusbar.config(
                    text="❌ Ошибка при запуске игры", foreground="red"
                ))

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.statusbar.config(
                text="❌ Ошибка: {}".format(error_msg), foreground="red"
            ))

        finally:
            self.root.after(0, lambda: self.start_btn.config(
                state=tk.NORMAL))

    def append_log(self, message: str, tag: str = 'info'):
        """ПРОЦЕСС 12a: Добавление сообщения в логи (с цветовой разметкой)"""
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)

    def update_ui_checking_start(self):
        """ПРОЦЕСС 12b: Обновление UI при начале проверки (блокировка кнопок, прогресс)"""
        self.check_btn.config(state=tk.DISABLED)
        self.install_btn.config(state=tk.DISABLED)
        self.progress.start()

    def update_ui_checking_end(self):
        """ПРОЦЕСС 12c: Обновление UI при завершении проверки (разблокировка кнопок)"""
        self.check_btn.config(state=tk.NORMAL)
        self.progress.stop()

    def update_ui_with_results(self):
        """ПРОЦЕСС 12d: Обновление UI с результатами проверки (статистика пакетов)"""
        if not self.checker:
            return

        self.status_required.config(
            text=str(len(self.checker.required_packages)))
        self.status_installed.config(
            text=str(len(self.checker.installed_packages)))
        self.status_missing.config(
            text=str(len(self.checker.missing_packages)))

        if self.checker.missing_packages:
            self.install_btn.config(state=tk.NORMAL)


def main():
    """Главная функция"""
    root = tk.Tk()
    BotMainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
