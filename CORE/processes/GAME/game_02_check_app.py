#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎮 GameProcess02CheckApp - ПРОЦЕСС 2: Проверка установки приложения
"""

import subprocess
from pathlib import Path


def _get_adb_path() -> str:
    local_adb = Path(__file__).parent.parent.parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    return str(local_adb) if local_adb.exists() else "adb"


class GameProcess02CheckApp:
    """ПРОЦЕСС 2: Проверка установки приложения через adb shell pm list packages"""
    
    @staticmethod
    def is_app_installed(connected_device: str, package: str, log_callback) -> bool:
        """
        ПРОЦЕСС 2: Проверка установки приложения через adb shell pm list packages
        
        Args:
            connected_device: ADB serial устройства
            package: Имя пакета для проверки
            log_callback: Функция логирования
            
        Returns:
            bool: True если установлено, False если нет
        """
        if not connected_device:
            log_callback("❌ Устройство не подключено!")
            return False

        try:
            log_callback(f"🔍 Проверка установки: {package}")

            result = subprocess.run([_get_adb_path(),
                                     "-s",
                                     connected_device,
                                     "shell",
                                     "pm",
                                     "list",
                                     "packages",
                                     package],
                                    capture_output=True,
                                    text=True,
                                    timeout=10,
                                    check=False,
                                    creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0 and package in result.stdout:
                log_callback("✅ Установлено")
                return True
            else:
                log_callback("❌ Не установлено")
                return False

        except Exception as e:
            log_callback(f"❌ Ошибка проверки: {e}")
            return False