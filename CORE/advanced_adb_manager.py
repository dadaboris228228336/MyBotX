#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AdvancedADBManager v3.0.0 - Сборщик процессов ADB подключения
Использует разбитые процессы из папки processes/
"""

try:
    from .processes import (
        ADBProcess01Init,
        ADBProcess02CheckPort,
        ADBProcess03FindPort,
        ADBProcess05Connect
    )
    from .game_launcher import GameLauncher
except ImportError:
    from processes import (
        ADBProcess01Init,
        ADBProcess02CheckPort,
        ADBProcess03FindPort,
        ADBProcess05Connect
    )
    from game_launcher import GameLauncher


class AdvancedADBManager:
    """Продвинутый менеджер для работы с ADB и BlueStacks 5 (использует процессы)"""

    def __init__(self):
        """ПРОЦЕСС 1: Инициализация AdvancedADBManager"""
        params = ADBProcess01Init.initialize()
        self.connected_device = params['connected_device']
        self.log_messages = params['log_messages']
        self.game_launcher = params['game_launcher']

    def _add_log(self, message: str):
        """ПРОЦЕСС 10a: Добавление сообщения в логи"""
        ADBProcess01Init.add_log(self.log_messages, message)

    def get_log(self) -> str:
        """ПРОЦЕСС 10b: Получение всех логов как строка"""
        return ADBProcess01Init.get_log(self.log_messages)

    def clear_log(self):
        """ПРОЦЕСС 10c: Очистка всех логов"""
        ADBProcess01Init.clear_log(self.log_messages)

    def _is_port_open(self, host: str = "127.0.0.1", port: int = 5555) -> bool:
        """ПРОЦЕСС 2: Быстрая проверка открытого порта через socket (1 сек таймаут)"""
        return ADBProcess02CheckPort.is_port_open(host, port)

    def find_available_adb_port(self, ports: list = None) -> int | None:
        """ПРОЦЕСС 3: Поиск доступного ADB порта (проверка 5555-5559)"""
        return ADBProcess03FindPort.find_available_adb_port(ports, self._add_log)

    def get_all_open_ports(self) -> list:
        """ПРОЦЕСС 4: Получение списка всех открытых ADB портов"""
        return ADBProcess03FindPort.get_all_open_ports(self._add_log)

    def _connect_to_device(self, serial: str) -> bool:
        """ПРОЦЕСС 5: Подключение к ADB устройству + создание GameLauncher"""
        success = ADBProcess05Connect.connect_to_device(serial, self._add_log)
        if success:
            self.connected_device = serial
            # Создаем game_launcher после успешного подключения
            self.game_launcher = GameLauncher(self.connected_device, self._add_log)
        return success

    def disconnect(self) -> bool:
        """ПРОЦЕСС 6: Отключение от устройства + очистка GameLauncher"""
        if self.connected_device:
            success = ADBProcess05Connect.disconnect(self.connected_device, self._add_log)
            if success:
                self.connected_device = None
                self.game_launcher = None
            return success
        return False

    def connect_to_bluestacks_with_wait(self, wait_timeout: int = 120, retry_interval: int = 3) -> tuple:
        """ПРОЦЕСС 7: Ожидание запуска BlueStacks (циклическая проверка портов)"""
        success, serial = ADBProcess05Connect.connect_to_bluestacks_with_wait(
            wait_timeout, retry_interval, self._add_log
        )
        if success and serial:
            self.connected_device = serial
            self.game_launcher = GameLauncher(self.connected_device, self._add_log)
        return success, serial

    def is_app_installed(self, package: str) -> bool:
        """ПРОЦЕСС 8a: Делегирование проверки установки в GameLauncher"""
        if not self.game_launcher:
            self._add_log("❌ GameLauncher не инициализирован!")
            return False
        return self.game_launcher.is_app_installed(package)

    def open_play_market(self, package: str = None) -> bool:
        """ПРОЦЕСС 8b: Делегирование открытия Play Market в GameLauncher"""
        if not self.game_launcher:
            self._add_log("❌ GameLauncher не инициализирован!")
            return False
        return self.game_launcher.open_play_market(package)

    def launch_app(self, package: str, activity: str = None) -> bool:
        """ПРОЦЕСС 8c: Делегирование запуска приложения в GameLauncher"""
        if not self.game_launcher:
            self._add_log("❌ GameLauncher не инициализирован!")
            return False
        return self.game_launcher.launch_app(package, activity)

    def launch_game_auto(self, game: str = 'clash_of_clans', wait_for_bluestacks: bool = True,
                        wait_timeout: int = 120, auto_install: bool = True) -> bool:
        """ПРОЦЕСС 9: Автоматический запуск игры (подключение + делегирование в GameLauncher)"""
        self._add_log(f"🚀 Запуск игры: {game}")

        # ШАГ 1: Подключение
        if wait_for_bluestacks:
            self._add_log("📋 Режим: АВТОМАТИЧЕСКИЙ (ждём BS)")
            success, serial = self.connect_to_bluestacks_with_wait(wait_timeout)
        else:
            self._add_log("📋 Режим: БЫСТРЫЙ (BS уже работает)")
            port = self.find_available_adb_port()
            if port:
                serial = f"127.0.0.1:{port}"
                success = self._connect_to_device(serial)
            else:
                success = False

        # ШАГ 2: Проверка подключения
        if not success:
            self._add_log("❌ Не подключено")
            return False

        # ШАГ 3: Запуск игры через GameLauncher
        if not self.game_launcher:
            self._add_log("❌ GameLauncher не инициализирован!")
            return False
            
        return self.game_launcher.launch_game_auto(game, auto_install)