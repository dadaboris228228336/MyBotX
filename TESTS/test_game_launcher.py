#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎮 Тест GameLauncher - Проверка всех процессов запуска игр
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

from game_launcher import GameLauncher


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
            print()  # Новая строка в конце


def test_game_launcher():
    """Основная функция тестирования GameLauncher"""
    print("=" * 70)
    print("🎮 ТЕСТ GameLauncher v1.0.0")
    print("=" * 70)
    
    # Инициализация прогресс-бара (7 процессов)
    progress = ProgressBar(7)
    results = []
    
    try:
        # ПРОЦЕСС 1: Инициализация
        print("\n📋 ПРОЦЕСС 1: Инициализация GameLauncher")
        launcher = GameLauncher()
        assert launcher.connected_device is None
        assert launcher.log_callback is not None
        results.append("✅ ПРОЦЕСС 1: Инициализация - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 2: Проверка поддерживаемых игр
        print("\n📋 ПРОЦЕСС 2: Проверка поддерживаемых игр")
        assert 'clash_of_clans' in launcher.APPS
        assert launcher.APPS['clash_of_clans']['package'] == 'com.supercell.clashofclans'
        assert launcher.APPS['clash_of_clans']['activity'] == 'com.supercell.titan.GameApp'
        results.append("✅ ПРОЦЕСС 2: Поддерживаемые игры - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 3: Проверка логирования
        print("\n📋 ПРОЦЕСС 3: Проверка системы логирования")
        test_message = "Тестовое сообщение"
        launcher._add_log(test_message)
        results.append("✅ ПРОЦЕСС 3: Система логирования - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 4: Проверка установки приложения (без подключения)
        print("\n📋 ПРОЦЕСС 4: Проверка установки приложения")
        result = launcher.is_app_installed("com.test.package")
        assert result == False  # Должно вернуть False без подключения
        results.append("✅ ПРОЦЕСС 4: Проверка установки - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 5: Открытие Play Market (без подключения)
        print("\n📋 ПРОЦЕСС 5: Открытие Play Market")
        result = launcher.open_play_market("com.test.package")
        assert result == False  # Должно вернуть False без подключения
        results.append("✅ ПРОЦЕСС 5: Play Market - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 6: Запуск приложения (без подключения)
        print("\n📋 ПРОЦЕСС 6: Запуск приложения")
        result = launcher.launch_app("com.test.package", "TestActivity")
        assert result == False  # Должно вернуть False без подключения
        results.append("✅ ПРОЦЕСС 6: Запуск приложения - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 7: Автоматический запуск игры
        print("\n📋 ПРОЦЕСС 7: Автоматический запуск игры")
        result = launcher.launch_game_auto('clash_of_clans')
        assert result == False  # Должно вернуть False без подключения
        results.append("✅ ПРОЦЕСС 7: Автоматический запуск - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # Итоговые результаты
        print("\n" + "=" * 70)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ GameLauncher:")
        print("=" * 70)
        
        for result in results:
            print(result)
        
        success_count = len(results)
        print(f"\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ: {success_count}/7")
        print("✅ GameLauncher работает корректно!")
        
        return True, results
        
    except Exception as e:
        error_msg = f"❌ ОШИБКА В ТЕСТЕ: {e}"
        results.append(error_msg)
        print(f"\n{error_msg}")
        return False, results


def main():
    """Главная функция"""
    start_time = time.time()
    
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ GameLauncher")
    print(f"⏰ Время начала: {time.strftime('%H:%M:%S')}")
    
    success, results = test_game_launcher()
    
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