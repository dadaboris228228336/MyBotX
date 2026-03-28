#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎮 GameLauncher v2.0.0 - Сборщик процессов запуска игр
Использует разбитые процессы из папки processes/
"""

try:
    from .processes import (
        GameProcess01Init,
        GameProcess02CheckApp,
        GameProcess03PlayMarket,
        GameProcess04LaunchDirect,
        GameProcess05LaunchIntent,
        GameProcess06LaunchMonkey,
        GameProcess07AutoLaunch
    )
except ImportError:
    from processes import (
        GameProcess01Init,
        GameProcess02CheckApp,
        GameProcess03PlayMarket,
        GameProcess04LaunchDirect,
        GameProcess05LaunchIntent,
        GameProcess06LaunchMonkey,
        GameProcess07AutoLaunch
    )


class GameLauncher:
    """Класс для запуска игр через ADB (использует процессы)"""

    def __init__(self, connected_device: str = None, log_callback=None):
        """ПРОЦЕСС 1: Инициализация GameLauncher"""
        params = GameProcess01Init.initialize(connected_device, log_callback)
        self.connected_device = params['connected_device']
        self.log_callback = params['log_callback']
        self.APPS = params['apps']

    def _add_log(self, message: str):
        """Добавляет сообщение в логи"""
        GameProcess01Init.add_log(self.log_callback, message)

    def is_app_installed(self, package: str) -> bool:
        """ПРОЦЕСС 2: Проверка установки приложения через adb shell pm list packages"""
        return GameProcess02CheckApp.is_app_installed(
            self.connected_device, package, self._add_log
        )

    def open_play_market(self, package: str = None) -> bool:
        """ПРОЦЕСС 3: Открытие Play Market через Android Intent"""
        return GameProcess03PlayMarket.open_play_market(
            self.connected_device, package, self._add_log
        )

    def launch_app(self, package: str, activity: str = None) -> bool:
        """ПРОЦЕССЫ 4-6: Запуск приложения (3 способа по очереди)"""
        if not self.connected_device:
            self._add_log("❌ Устройство не подключено!")
            return False

        # ПРОЦЕСС 4: СПОСОБ 1 - Прямой запуск через activity
        if activity:
            if GameProcess04LaunchDirect.launch_direct(
                self.connected_device, package, activity, self._add_log
            ):
                return True

        # ПРОЦЕСС 5: СПОСОБ 2 - LAUNCHER INTENT
        if GameProcess05LaunchIntent.launch_intent(
            self.connected_device, package, self._add_log
        ):
            return True

        # ПРОЦЕСС 6: СПОСОБ 3 - Monkey (резервный)
        if GameProcess06LaunchMonkey.launch_monkey(
            self.connected_device, package, self._add_log
        ):
            return True

        self._add_log("❌ Все способы запуска не сработали")
        return False

    def launch_game_auto(self, game: str = 'clash_of_clans', auto_install: bool = True) -> bool:
        """ПРОЦЕСС 7: Автоматический запуск игры (объединяет все способы)"""
        return GameProcess07AutoLaunch.launch_game_auto(
            self.connected_device, game, auto_install, self._add_log
        )