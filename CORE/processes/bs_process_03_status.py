#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 BSProcess03Status - ПРОЦЕСС 6-9: Проверка статуса BlueStacks
"""

import psutil


class BSProcess03Status:
    """ПРОЦЕСС 6-9: Проверка установки и запуска BlueStacks"""
    
    @staticmethod
    def is_installed(bluestacks_path: str) -> bool:
        """
        ПРОЦЕСС 6: Проверка установки BlueStacks (есть ли путь)
        
        Args:
            bluestacks_path: Путь к BlueStacks
            
        Returns:
            bool: True если установлен
        """
        return bluestacks_path is not None
    
    @staticmethod
    def get_path(bluestacks_path: str) -> str | None:
        """
        ПРОЦЕСС 7: Получение основного пути к BlueStacks
        
        Args:
            bluestacks_path: Путь к BlueStacks
            
        Returns:
            str | None: Путь к BlueStacks
        """
        return bluestacks_path
    
    @staticmethod
    def get_all_found_paths(all_found_paths: list) -> list:
        """
        ПРОЦЕСС 8: Получение всех найденных путей BlueStacks
        
        Args:
            all_found_paths: Список всех найденных путей
            
        Returns:
            list: Копия списка путей
        """
        return all_found_paths.copy()
    
    @staticmethod
    def is_running() -> bool:
        """
        ПРОЦЕСС 9: Проверка запуска BlueStacks (поиск HD-Player.exe в процессах)
        
        Returns:
            bool: True если запущен
        """
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'HD-Player.exe' in proc.info['name']:
                    return True
            return False
        except Exception:
            return False