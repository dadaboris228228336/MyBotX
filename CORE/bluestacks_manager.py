#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 BlueStacksManager v4.0.0 - Сборщик процессов управления BlueStacks
Использует разбитые процессы из папки processes/
"""

try:
    from .processes import (
        BSProcess01Init,
        BSProcess02Search,
        BSProcess03Status,
        BSProcess04Control
    )
except ImportError:
    from processes import (
        BSProcess01Init,
        BSProcess02Search,
        BSProcess03Status,
        BSProcess04Control
    )


class BlueStacksManager:
    """Менеджер для управления BlueStacks 5 (использует процессы)"""

    def __init__(self):
        """ПРОЦЕСС 1: Инициализация с автоматическим поиском BlueStacks"""
        params = BSProcess01Init.initialize()
        self.config_file = params['config_file']
        self.bluestacks_path = params['bluestacks_path']
        self.all_found_paths = params['all_found_paths']

        # ПРОЦЕСС 2: Автоматически ищем BlueStacks при создании объекта
        self._find_bluestacks()

    def _find_bluestacks(self):
        """ПРОЦЕСС 2: Автоматический поиск BlueStacks (конфиг -> поиск -> сохранение)"""
        self.bluestacks_path, self.all_found_paths = BSProcess02Search.find_bluestacks(self.config_file)

    def _search_all_locations(self) -> list:
        """ПРОЦЕСС 3: Поиск BlueStacks во всех стандартных локациях"""
        return BSProcess02Search.search_all_locations()

    def _load_from_cache(self) -> str | None:
        """ПРОЦЕСС 4: Загрузка пути из config.json"""
        return BSProcess01Init.load_from_config(self.config_file)

    def _save_to_cache(self, path: str):
        """ПРОЦЕСС 5: Сохранение найденного пути в config.json"""
        BSProcess01Init.save_to_config(self.config_file, path)

    def is_installed(self) -> bool:
        """ПРОЦЕСС 6: Проверка установки BlueStacks (есть ли путь)"""
        return BSProcess03Status.is_installed(self.bluestacks_path)

    def get_path(self) -> str | None:
        """ПРОЦЕСС 7: Получение основного пути к BlueStacks"""
        return BSProcess03Status.get_path(self.bluestacks_path)

    def get_all_found_paths(self) -> list:
        """ПРОЦЕСС 8: Получение всех найденных путей BlueStacks"""
        return BSProcess03Status.get_all_found_paths(self.all_found_paths)

    def is_running(self) -> bool:
        """ПРОЦЕСС 9: Проверка запуска BlueStacks (поиск HD-Player.exe в процессах)"""
        return BSProcess03Status.is_running()

    def launch(self) -> tuple:
        """ПРОЦЕСС 10: Запуск BlueStacks через subprocess.Popen"""
        return BSProcess04Control.launch(self.bluestacks_path)

    def kill_all_processes(self) -> bool:
        """ПРОЦЕСС 11: Завершение всех процессов BlueStacks (terminate -> kill)"""
        return BSProcess04Control.kill_all_processes()

    def restart(self) -> tuple:
        """ПРОЦЕСС 12: Перезапуск BlueStacks (завершение + запуск)"""
        return BSProcess04Control.restart(self.bluestacks_path)

    def get_bluestacks_processes(self) -> list:
        """ПРОЦЕСС 13: Получение информации о запущенных процессах BlueStacks"""
        return BSProcess04Control.get_bluestacks_processes()

    def set_fixed_window_size(self, log=None) -> bool:
        """ПРОЦЕСС 14: Фиксирует разрешение Android 1280x720 через ADB"""
        from processes.BLUESTACKS.bs_05_window import set_fixed_resolution
        # device берём из advanced_adb_manager — передаётся снаружи
        return False  # вызывается напрямую из main.py с device

    def set_fixed_resolution(self, device: str, log=None) -> bool:
        """ПРОЦЕСС 14: Фиксирует разрешение Android 1280x720 через ADB"""
        from processes.BLUESTACKS.bs_05_window import set_fixed_resolution
        return set_fixed_resolution(device, log)

    def minimize_window(self, log=None) -> bool:
        """ПРОЦЕСС 15: Сворачивает окно BlueStacks"""
        from processes.BLUESTACKS.bs_05_window import minimize_window
        return minimize_window(log)

    def restore_window(self, log=None) -> bool:
        """ПРОЦЕСС 16: Разворачивает окно BlueStacks"""
        from processes.BLUESTACKS.bs_05_window import restore_window
        return restore_window(log)