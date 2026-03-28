#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 BSProcess02Search - ПРОЦЕСС 2-3: Поиск BlueStacks
"""

import winreg
from pathlib import Path
from .bs_process_01_init import BSProcess01Init


class BSProcess02Search:
    """ПРОЦЕСС 2-3: Автоматический поиск BlueStacks"""

    @staticmethod
    def find_bluestacks(config_file: Path) -> tuple:
        """
        ПРОЦЕСС 2: Автоматический поиск BlueStacks (конфиг -> поиск -> сохранение)
        """
        # Сначала пробуем загрузить из конфига
        cached_path = BSProcess01Init.load_from_config(config_file)
        if cached_path and Path(cached_path).exists():
            return cached_path, [cached_path]

        # Если конфиг не помог, ищем заново
        all_found_paths = BSProcess02Search.search_all_locations()

        if all_found_paths:
            bluestacks_path = all_found_paths[0]
            BSProcess01Init.save_to_config(config_file, bluestacks_path)
            return bluestacks_path, all_found_paths

        return None, []

    @staticmethod
    def search_all_locations() -> list:
        """
        ПРОЦЕСС 3: Поиск BlueStacks — реестр Windows + стандартные пути
        """
        found_paths = []

        # ШАГ 1: Поиск через реестр Windows
        registry_paths = BSProcess02Search._search_registry()
        for p in registry_paths:
            if p not in found_paths:
                found_paths.append(p)

        # ШАГ 2: Поиск по стандартным путям
        hardcoded_paths = [
            "C:/Program Files/BlueStacks_nxt/HD-Player.exe",
            "C:/Program Files (x86)/BlueStacks_nxt/HD-Player.exe",
            "C:/Program Files/BlueStacks/HD-Player.exe",
            "C:/Program Files (x86)/BlueStacks/HD-Player.exe",
            "D:/Program Files/BlueStacks_nxt/HD-Player.exe",
            "D:/Program Files/BlueStacks/HD-Player.exe",
        ]

        for path_str in hardcoded_paths:
            path = Path(path_str)
            if path.exists() and path.is_file():
                if str(path) not in found_paths:
                    found_paths.append(str(path))

        return found_paths

    @staticmethod
    def _search_registry() -> list:
        """
        Поиск пути BlueStacks через реестр Windows
        """
        found = []
        registry_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\BlueStacks_nxt"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\BlueStacks_nxt"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\BlueStacks"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\BlueStacks"),
        ]

        for hive, key_path in registry_keys:
            try:
                with winreg.OpenKey(hive, key_path) as key:
                    # Пробуем получить InstallDir
                    try:
                        install_dir, _ = winreg.QueryValueEx(key, "InstallDir")
                        player = Path(install_dir) / "HD-Player.exe"
                        if player.exists():
                            found.append(str(player))
                            continue
                    except FileNotFoundError:
                        pass

                    # Пробуем DataDir
                    try:
                        data_dir, _ = winreg.QueryValueEx(key, "DataDir")
                        # DataDir обычно рядом с InstallDir
                        player = Path(data_dir).parent / "HD-Player.exe"
                        if player.exists():
                            found.append(str(player))
                    except FileNotFoundError:
                        pass

            except (FileNotFoundError, OSError):
                continue

        return found