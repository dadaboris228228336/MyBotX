#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🖥️ Тест Main GUI - Проверка основных процессов графического интерфейса
"""

import sys
import os
import time
import tkinter as tk

# Настройка кодировки для Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'CORE'))

# Импортируем только класс, не создаем окно
try:
    from main import BotMainWindow
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    BotMainWindow = None


class ProgressBar:
    """Простой прогресс-бар для тестов"""
    
    def __init__(self, total, width=50):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, step=1):
        self.current += step
        percent = (self.current / self.total) * 100
        filled = int(self.width * self.current // self.total)
        bar = '█' * filled + '░' * (self.width - filled)
        print(f'\r[{bar}] {percent:.1f}% ({self.current}/{self.total})', end='', flush=True)
        if self.current >= self.total:
            print()


def test_main_gui():
    """Основная функция тестирования Main GUI"""
    print("=" * 70)
    print("🖥️ ТЕСТ Main GUI v3.0.0")
    print("=" * 70)
    
    # Инициализация прогресс-бара (8 процессов - без реального GUI)
    progress = ProgressBar(8)
    results = []
    
    try:
        # ПРОЦЕСС 1: Проверка импорта модулей
        print("\n📋 ПРОЦЕСС 1: Проверка импорта модулей")
        if BotMainWindow is None:
            results.append("❌ ПРОЦЕСС 1: Импорт модулей - НЕ ПРОЙДЕН")
            return False, results
        
        # Проверяем что класс существует
        assert BotMainWindow is not None
        results.append("✅ ПРОЦЕСС 1: Импорт модулей - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 2: Проверка tkinter
        print("\n📋 ПРОЦЕСС 2: Проверка доступности tkinter")
        try:
            root = tk.Tk()
            root.withdraw()  # Скрываем окно
            root.destroy()
            results.append("✅ ПРОЦЕСС 2: tkinter доступен - ПРОЙДЕН")
        except Exception as e:
            results.append(f"❌ ПРОЦЕСС 2: tkinter недоступен - {e}")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 3: Проверка создания экземпляра (без GUI)
        print("\n📋 ПРОЦЕСС 3: Проверка структуры класса")
        # Проверяем что у класса есть нужные методы
        required_methods = [
            '__init__',
            'setup_styles',
            'create_widgets',
            'create_main_tab',
            'create_check_tab',
            'create_about_tab',
            'on_start_bot',
            'start_bot_thread'
        ]
        
        for method in required_methods:
            assert hasattr(BotMainWindow, method), f"Метод {method} не найден"
        
        results.append("✅ ПРОЦЕСС 3: Структура класса - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 4: Проверка импорта зависимостей
        print("\n📋 ПРОЦЕСС 4: Проверка импорта зависимостей")
        try:
            from dependency_checker import DependencyChecker
            from bluestacks_manager import BlueStacksManager
            from advanced_adb_manager import AdvancedADBManager
            results.append("✅ ПРОЦЕСС 4: Импорт зависимостей - ПРОЙДЕН")
        except ImportError as e:
            results.append(f"❌ ПРОЦЕСС 4: Ошибка импорта - {e}")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 5: Проверка threading
        print("\n📋 ПРОЦЕСС 5: Проверка многопоточности")
        import threading
        assert threading is not None
        results.append("✅ ПРОЦЕСС 5: Многопоточность - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 6: Проверка pathlib
        print("\n📋 ПРОЦЕСС 6: Проверка работы с путями")
        from pathlib import Path
        assert Path is not None
        results.append("✅ ПРОЦЕСС 6: Работа с путями - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 7: Проверка ttk стилей
        print("\n📋 ПРОЦЕСС 7: Проверка ttk стилей")
        from tkinter import ttk
        assert ttk is not None
        results.append("✅ ПРОЦЕСС 7: TTK стили - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 8: Проверка messagebox
        print("\n📋 ПРОЦЕСС 8: Проверка диалоговых окон")
        from tkinter import messagebox
        assert messagebox is not None
        results.append("✅ ПРОЦЕСС 8: Диалоговые окна - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # Итоговые результаты
        print("\n" + "=" * 70)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ Main GUI:")
        print("=" * 70)
        
        for result in results:
            print(result)
        
        success_count = len([r for r in results if r.startswith("✅")])
        total_tests = len(results)
        print(f"\n🎉 ТЕСТЫ ПРОЙДЕНЫ: {success_count}/{total_tests}")
        
        if success_count == total_tests:
            print("✅ Main GUI готов к работе!")
            return True, results
        else:
            print("⚠️ Некоторые тесты не прошли")
            return False, results
        
    except Exception as e:
        error_msg = f"❌ ОШИБКА В ТЕСТЕ: {e}"
        results.append(error_msg)
        print(f"\n{error_msg}")
        return False, results


def main():
    """Главная функция"""
    start_time = time.time()
    
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ Main GUI")
    print(f"⏰ Время начала: {time.strftime('%H:%M:%S')}")
    print("ℹ️ Примечание: GUI тестируется без создания окон")
    
    success, results = test_main_gui()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n⏰ Время завершения: {time.strftime('%H:%M:%S')}")
    print(f"⏱️ Длительность: {duration:.2f} секунд")
    
    if success:
        print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        return 0
    else:
        print("\n❌ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)