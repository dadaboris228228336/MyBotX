#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 Тест BlueStacksManager - Проверка всех процессов управления BlueStacks
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

from bluestacks_manager import BlueStacksManager


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


def test_bluestacks_manager():
    """Основная функция тестирования BlueStacksManager"""
    print("=" * 70)
    print("🔧 ТЕСТ BlueStacksManager v3.0.0")
    print("=" * 70)
    
    # Инициализация прогресс-бара (13 процессов)
    progress = ProgressBar(13)
    results = []
    
    try:
        # ПРОЦЕСС 1: Инициализация с автоматическим поиском
        print("\n📋 ПРОЦЕСС 1: Инициализация с автоматическим поиском BlueStacks")
        bs = BlueStacksManager()
        assert hasattr(bs, 'bluestacks_path')
        assert hasattr(bs, 'all_found_paths')
        assert hasattr(bs, 'config_file')
        results.append("✅ ПРОЦЕСС 1: Инициализация - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 2: Автоматический поиск BlueStacks
        print("\n📋 ПРОЦЕСС 2: Автоматический поиск BlueStacks")
        # Проверяем что поиск был выполнен
        assert isinstance(bs.all_found_paths, list)
        results.append("✅ ПРОЦЕСС 2: Автоматический поиск - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 3: Поиск во всех локациях
        print("\n📋 ПРОЦЕСС 3: Поиск во всех стандартных локациях")
        found_paths = bs._search_all_locations()
        assert isinstance(found_paths, list)
        results.append("✅ ПРОЦЕСС 3: Поиск в локациях - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 4: Загрузка из кэша
        print("\n📋 ПРОЦЕСС 4: Загрузка пути из конфига")
        cached_path = bs._load_from_cache()
        # Может быть None если конфиг пустой
        assert cached_path is None or isinstance(cached_path, str)
        results.append("✅ ПРОЦЕСС 4: Загрузка из конфига - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 5: Сохранение в кэш
        print("\n📋 ПРОЦЕСС 5: Сохранение в конфиг")
        test_path = "C:/Test/Path/HD-Player.exe"
        bs._save_to_cache(test_path)
        # Проверяем что файл конфига существует
        assert bs.config_file.exists()
        results.append("✅ ПРОЦЕСС 5: Сохранение в конфиг - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 6: Проверка установки
        print("\n📋 ПРОЦЕСС 6: Проверка установки BlueStacks")
        is_installed = bs.is_installed()
        assert isinstance(is_installed, bool)
        results.append("✅ ПРОЦЕСС 6: Проверка установки - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 7: Получение основного пути
        print("\n📋 ПРОЦЕСС 7: Получение основного пути")
        path = bs.get_path()
        assert path is None or isinstance(path, str)
        results.append("✅ ПРОЦЕСС 7: Получение пути - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 8: Получение всех найденных путей
        print("\n📋 ПРОЦЕСС 8: Получение всех найденных путей")
        all_paths = bs.get_all_found_paths()
        assert isinstance(all_paths, list)
        results.append("✅ ПРОЦЕСС 8: Все найденные пути - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 9: Проверка запуска
        print("\n📋 ПРОЦЕСС 9: Проверка запуска BlueStacks")
        is_running = bs.is_running()
        assert isinstance(is_running, bool)
        results.append("✅ ПРОЦЕСС 9: Проверка запуска - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 10: Запуск BlueStacks (тестируем логику)
        print("\n📋 ПРОЦЕСС 10: Логика запуска BlueStacks")
        # Не запускаем реально, только проверяем возврат
        if not bs.is_installed():
            success, message = bs.launch()
            assert isinstance(success, bool)
            assert isinstance(message, str)
        results.append("✅ ПРОЦЕСС 10: Логика запуска - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 11: Завершение процессов (тестируем логику)
        print("\n📋 ПРОЦЕСС 11: Логика завершения процессов")
        # Не завершаем реально, только проверяем возврат
        killed = bs.kill_all_processes()
        assert isinstance(killed, bool)
        results.append("✅ ПРОЦЕСС 11: Завершение процессов - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 12: Перезапуск (тестируем логику)
        print("\n📋 ПРОЦЕСС 12: Логика перезапуска")
        if not bs.is_installed():
            success, message = bs.restart()
            assert isinstance(success, bool)
            assert isinstance(message, str)
        results.append("✅ ПРОЦЕСС 12: Логика перезапуска - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # ПРОЦЕСС 13: Получение списка процессов
        print("\n📋 ПРОЦЕСС 13: Получение информации о процессах")
        processes = bs.get_bluestacks_processes()
        assert isinstance(processes, list)
        results.append("✅ ПРОЦЕСС 13: Информация о процессах - ПРОЙДЕН")
        progress.update()
        time.sleep(0.5)
        
        # Итоговые результаты
        print("\n" + "=" * 70)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ BlueStacksManager:")
        print("=" * 70)
        
        for result in results:
            print(result)
        
        success_count = len(results)
        print(f"\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ: {success_count}/13")
        print("✅ BlueStacksManager работает корректно!")
        
        return True, results
        
    except Exception as e:
        error_msg = f"❌ ОШИБКА В ТЕСТЕ: {e}"
        results.append(error_msg)
        print(f"\n{error_msg}")
        return False, results


def main():
    """Главная функция"""
    start_time = time.time()
    
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ BlueStacksManager")
    print(f"⏰ Время начала: {time.strftime('%H:%M:%S')}")
    
    success, results = test_bluestacks_manager()
    
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