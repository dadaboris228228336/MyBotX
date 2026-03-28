#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎮 GameProcess01Init - ПРОЦЕСС 1: Инициализация GameLauncher
"""


class GameProcess01Init:
    """ПРОЦЕСС 1: Инициализация GameLauncher"""
    
    # Поддерживаемые игры
    APPS = {
        'clash_of_clans': {
            'package': 'com.supercell.clashofclans',
            'activity': 'com.supercell.titan.GameApp'  # ✅ ПРАВИЛЬНАЯ АКТИВНОСТЬ
        }
    }
    
    @staticmethod
    def initialize(connected_device: str = None, log_callback=None):
        """
        ПРОЦЕСС 1: Инициализация GameLauncher
        
        Args:
            connected_device: ADB serial устройства (например "127.0.0.1:5555")
            log_callback: Функция для логирования (например self._add_log)
            
        Returns:
            dict: Инициализированные параметры
        """
        return {
            'connected_device': connected_device,
            'log_callback': log_callback or print,
            'apps': GameProcess01Init.APPS
        }
    
    @staticmethod
    def add_log(log_callback, message: str):
        """Добавляет сообщение в логи"""
        if log_callback:
            log_callback(message)
        else:
            print(message)