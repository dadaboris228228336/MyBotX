#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ADBProcess01Init - ПРОЦЕСС 1: Инициализация AdvancedADBManager
"""


class ADBProcess01Init:
    """ПРОЦЕСС 1: Инициализация AdvancedADBManager"""
    
    @staticmethod
    def initialize():
        """
        ПРОЦЕСС 1: Инициализация AdvancedADBManager
        
        Returns:
            dict: Инициализированные параметры
        """
        return {
            'connected_device': None,
            'log_messages': [],
            'game_launcher': None
        }
    
    @staticmethod
    def add_log(log_messages: list, message: str):
        """Добавляет сообщение в логи"""
        log_messages.append(message)
        print(message)
    
    @staticmethod
    def get_log(log_messages: list) -> str:
        """Получает всё содержимое логов"""
        return "\n".join(log_messages)
    
    @staticmethod
    def clear_log(log_messages: list):
        """Очищает логи"""
        log_messages.clear()