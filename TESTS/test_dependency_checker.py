#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📦 Тест DependencyChecker - Проверка всех процессов управления зависимостями
"""

import sys
import os
import time

# Настройка кодировки для Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'CORE'))

from dependency_checker import DependencyChecker


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


def test_dependency_checker():
    """Основная функция тестирования DependencyChecker"""
    print("=" * 70)
    print("📦 ТЕСТ DependencyChecker")
    print("=" * 70)
    
    # Инициализация прогресс-бара (10 процессов)
    progress = ProgressBar(10)
    results = []
    
    try:
        # ПРОЦЕСС 1: Инициализация
        print("\n📋 ПРОЦЕСС 1: Инициализация DependencyChecker")
        checker = DependencyChecker("requirements.txt")
        assert hasattr(checker, 'requirements_file')
        assert hasattr(checker, 'required_packages')
        assert hasattr(checker, 'installed_packages')
        assert hasattr(checker, 'missing_packages')
        assert hasattr(checker, 'log_messages')
        results.append("✅ ПРОЦЕСС 1: Инициализация - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 2: Система логирования
        print("\n📋 ПРОЦЕСС 2: Система логирования")
        initial_count = len(checker.log_messages)
        checker._add_log("Тестовое сообщение")
        assert len(checker.log_messages) == initial_count + 1
        results.append("✅ ПРОЦЕСС 2: Логирование - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 3: Парсинг requirements.txt
        print("\n📋 ПРОЦЕСС 3: Парсинг requirements.txt")
        packages = checker._parse_requirements()
        assert isinstance(packages, list)
        results.append("✅ ПРОЦЕСС 3: Парсинг requirements - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 4: Получение установленных пакетов
        print("\n📋 ПРОЦЕСС 4: Получение установленных пакетов")
        installed = checker._get_installed_packages()
        assert isinstance(installed, list)
        results.append("✅ ПРОЦЕСС 4: Установленные пакеты - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 5: Проверка конкретного пакета
        print("\n📋 ПРОЦЕСС 5: Проверка конкретного пакета")
        checker.installed_packages = ['requests', 'pillow', 'psutil']
        result1 = checker._check_package_installed('requests')
        result2 = checker._check_package_installed('nonexistent-package')
        assert result1 == True
        assert result2 == False
        results.append("✅ ПРОЦЕСС 5: Проверка пакета - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 6: Полная проверка зависимостей
        print("\n📋 ПРОЦЕСС 6: Полная проверка зависимостей")
        check_results = checker.check_dependencies()
        assert isinstance(check_results, dict)
        results.append("✅ ПРОЦЕСС 6: Полная проверка - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 7: Установка пакетов (тестируем логику)
        print("\n📋 ПРОЦЕСС 7: Логика установки пакетов")
        # Не устанавливаем реально, только проверяем что функция работает
        if not checker.missing_packages:
            success = checker.install_missing_packages()
            assert isinstance(success, bool)
        results.append("✅ ПРОЦЕСС 7: Логика установки - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 8: Получение логов
        print("\n📋 ПРОЦЕСС 8: Получение логов")
        log_content = checker.get_log()
        assert isinstance(log_content, str)
        assert len(log_content) > 0  # Должны быть логи
        results.append("✅ ПРОЦЕСС 8: Получение логов - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 9: Очистка логов
        print("\n📋 ПРОЦЕСС 9: Очистка логов")
        checker.clear_log()
        assert len(checker.log_messages) == 0
        results.append("✅ ПРОЦЕСС 9: Очистка логов - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 10: Получение сводки
        print("\n📋 ПРОЦЕСС 10: Получение сводки")
        summary = checker.get_summary()
        assert isinstance(summary, dict)
        assert 'total' in summary
        assert 'installed' in summary
        assert 'missing' in summary
        results.append("✅ ПРОЦЕСС 10: Сводка - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # Итоговые результаты
        print("\n" + "=" * 70)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ DependencyChecker:")
        print("=" * 70)
        
        for result in results:
            print(result)
        
        success_count = len(results)
        print(f"\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ: {success_count}/10")
        print("✅ DependencyChecker работает корректно!")
        
        return True, results
        
    except Exception as e:
        error_msg = f"❌ ОШИБКА В ТЕСТЕ: {e}"
        results.append(error_msg)
        print(f"\n{error_msg}")
        return False, results


def main():
    """Главная функция"""
    start_time = time.time()
    
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ DependencyChecker")
    print(f"⏰ Время начала: {time.strftime('%H:%M:%S')}")
    
    success, results = test_dependency_checker()
    
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