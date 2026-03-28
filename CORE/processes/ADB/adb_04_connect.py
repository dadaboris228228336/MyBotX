#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ADBProcess05Connect - ПРОЦЕСС 5: Подключение к ADB устройству
"""

import subprocess
import time
import os
from pathlib import Path
from .adb_03_find_port import ADBProcess03FindPort


def _get_adb_path() -> str:
    """Возвращает путь к adb: сначала локальный, потом системный"""
    # Ищем локальный adb в BOT_APPLICATIONS
    local_adb = Path(__file__).parent.parent.parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    if local_adb.exists():
        return str(local_adb)
    return "adb"  # системный PATH


class ADBProcess05Connect:
    """ПРОЦЕСС 5: Подключение к ADB устройству + создание GameLauncher"""
    
    @staticmethod
    def connect_to_device(serial: str, log_callback=None) -> bool:
        """
        ПРОЦЕСС 5: Подключение к ADB устройству + создание GameLauncher
        
        Args:
            serial: ADB serial (например "127.0.0.1:5555")
            log_callback: Функция логирования
            
        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            if log_callback:
                log_callback("🔌 Подключение к {}...".format(serial))

            result = subprocess.run(
                [_get_adb_path(), "connect", serial],
                capture_output=True,
                text=True,
                timeout=15,  # ✅ Увеличили до 15 сек
                check=False
            )

            if result.returncode == 0:
                if log_callback:
                    log_callback("✅ Подключено к {}".format(serial))
                return True
            else:
                if log_callback:
                    log_callback("❌ Ошибка подключения: {}".format(result.stderr))
                return False

        except subprocess.TimeoutExpired:
            if log_callback:
                log_callback("⏱️ Timeout при подключении к {}".format(serial))
            return False
        except Exception as e:
            if log_callback:
                log_callback(f"❌ Исключение при подключении: {e}")
            return False
    
    @staticmethod
    def disconnect(serial: str, log_callback=None) -> bool:
        """
        ПРОЦЕСС 6: Отключение от устройства + очистка GameLauncher
        
        Args:
            serial: ADB serial устройства
            log_callback: Функция логирования
            
        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            if not serial:
                return False

            result = subprocess.run(
                [_get_adb_path(), "disconnect", serial],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )

            if log_callback:
                log_callback("✅ Отключено")
            return result.returncode == 0

        except Exception as e:
            if log_callback:
                log_callback(f"❌ Ошибка отключения: {e}")
            return False
    
    @staticmethod
    def connect_to_bluestacks_with_wait(wait_timeout: int = 120, retry_interval: int = 3, 
                                       log_callback=None) -> tuple:
        """
        ПРОЦЕСС 7: Ожидание запуска BlueStacks (циклическая проверка портов)
        
        Args:
            wait_timeout: Максимальное время ожидания в секундах
            retry_interval: Интервал между попытками в секундах
            log_callback: Функция логирования
            
        Returns:
            tuple: (success: bool, serial: str | None)
        """
        if log_callback:
            log_callback(f"⏳ Ожидание запуска BlueStacks (макс {wait_timeout} сек)...")
            log_callback(f"   Проверяем каждые {retry_interval} сек")

        elapsed = 0
        attempt = 0

        while elapsed < wait_timeout:
            attempt += 1
            if log_callback:
                log_callback(f"📍 Попытка {attempt}: Проверяем портов...")

            port = ADBProcess03FindPort.find_available_adb_port(log_callback=log_callback)

            if port is not None:
                serial = f"127.0.0.1:{port}"
                if log_callback:
                    log_callback("🎯 Найден порт! Подключаемся...")

                if ADBProcess05Connect.connect_to_device(serial, log_callback):
                    if log_callback:
                        log_callback("✅ Успешно подключились!")
                    return True, serial

            time.sleep(retry_interval)
            elapsed += retry_interval

            remaining = wait_timeout - elapsed
            if remaining > 0 and log_callback:
                log_callback(f"⏱️  Осталось: {remaining} сек")

        if log_callback:
            log_callback(f"❌ Timeout! BlueStacks не запустился за {wait_timeout} сек")
        return False, None