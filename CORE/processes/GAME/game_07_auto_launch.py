#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎮 GameProcess07AutoLaunch - ПРОЦЕСС 7: Автоматический запуск игры
"""

import time
from .game_01_init import GameProcess01Init
from .game_04_launch_direct import GameProcess04LaunchDirect
from .game_05_launch_intent import GameProcess05LaunchIntent
from .game_06_launch_monkey import GameProcess06LaunchMonkey


class GameProcess07AutoLaunch:
    """ПРОЦЕСС 7: Автоматический запуск игры (объединяет все способы)"""
    
    @staticmethod
    def launch_game_auto(connected_device: str, game: str = 'clash_of_clans', 
                        auto_install: bool = True, log_callback=None) -> bool:
        """
        ПРОЦЕСС 7: Автоматический запуск игры (объединяет все способы)
        
        Args:
            connected_device: ADB serial устройства
            game: Название игры
            auto_install: Автоустановка (пока не используется)
            log_callback: Функция логирования
            
        Returns:
            bool: True если успешно, False если ошибка
        """
        if not log_callback:
            log_callback = print

        # Получаем данные игры
        apps = GameProcess01Init.APPS
        
        if game not in apps:
            log_callback(f"❌ Игра не поддерживается: {game}")
            return False

        if not connected_device:
            log_callback("❌ Устройство не подключено!")
            return False

        log_callback(f"🚀 Запуск игры: {game}")

        # Небольшая пауза для стабильности
        time.sleep(1)
        
        # Получаем данные приложения
        app = apps[game]
        package = app['package']
        activity = app['activity']
        
        # СПОСОБ 1: Monkey (только для Clash of Clans) - ПРИОРИТЕТНЫЙ
        if GameProcess06LaunchMonkey.launch_monkey(connected_device, package, log_callback):
            return True
        
        # СПОСОБ 2: Прямой запуск через activity
        if GameProcess04LaunchDirect.launch_direct(connected_device, package, activity, log_callback):
            return True
        
        # СПОСОБ 3: LAUNCHER INTENT
        if GameProcess05LaunchIntent.launch_intent(connected_device, package, log_callback):
            return True
        
        log_callback("❌ Все способы запуска не сработали")
        return False