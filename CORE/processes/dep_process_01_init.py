#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📦 DepProcess01Init - ПРОЦЕСС 1-2: Инициализация DependencyChecker
"""

from pathlib import Path


class DepProcess01Init:
    """ПРОЦЕСС 1-2: Инициализация и логирование DependencyChecker"""
    
    @staticmethod
    def initialize(requirements_file: str = "requirements.txt") -> dict:
        """
        ПРОЦЕСС 1: Инициализация проверщика зависимостей
        
        Args:
            requirements_file: Путь к файлу requirements.txt
            
        Returns:
            dict: Инициализированные параметры
        """
        return {
            'requirements_file': Path(requirements_file),
            'required_packages': [],
            'installed_packages': [],
            'missing_packages': [],
            'log_messages': []
        }
    
    @staticmethod
    def add_log(log_messages: list, message: str) -> None:
        """
        ПРОЦЕСС 2: Добавление сообщения в лог (сохранение + вывод)
        
        Args:
            log_messages: Список сообщений лога
            message: Сообщение для добавления
        """
        log_messages.append(message)
        print(message)
    
    @staticmethod
    def get_log(log_messages: list) -> str:
        """
        ПРОЦЕСС 8: Получение всех логов как строка
        
        Args:
            log_messages: Список сообщений лога
            
        Returns:
            str: Все сообщения как строка
        """
        return "\n".join(log_messages)
    
    @staticmethod
    def clear_log(log_messages: list) -> None:
        """
        ПРОЦЕСС 9: Очистка всех логов
        
        Args:
            log_messages: Список сообщений лога
        """
        log_messages.clear()
    
    @staticmethod
    def get_summary(required_packages: list, missing_packages: list) -> dict:
        """
        ПРОЦЕСС 10: Получение сводки (статистика по пакетам)
        
        Args:
            required_packages: Список требуемых пакетов
            missing_packages: Список недостающих пакетов
            
        Returns:
            dict: Статистика по пакетам
        """
        return {
            'total': len(required_packages),
            'installed': len(required_packages) - len(missing_packages),
            'missing': len(missing_packages)
        }