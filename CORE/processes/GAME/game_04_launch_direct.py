#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎮 GameProcess04LaunchDirect - ПРОЦЕСС 4: Прямой запуск через activity
"""

import subprocess
from pathlib import Path


def _get_adb_path() -> str:
    local_adb = Path(__file__).parent.parent.parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    return str(local_adb) if local_adb.exists() else "adb"


class GameProcess04LaunchDirect:
    """ПРОЦЕСС 4: СПОСОБ 1 - Прямой запуск через activity"""
    
    @staticmethod
    def launch_direct(connected_device: str, package: str, activity: str, log_callback) -> bool:
        """
        ПРОЦЕСС 4: СПОСОБ 1 - Прямой запуск через activity
        
        Args:
            connected_device: ADB serial устройства
            package: Имя пакета
            activity: Активность для запуска
            log_callback: Функция логирования
            
        Returns:
            bool: True если успешно, False если ошибка
        """
        if not connected_device:
            log_callback("❌ Устройство не подключено!")
            return False

        try:
            log_callback(f"🎮 Прямой запуск: {package}")
            log_callback(f"   Используем активность: {activity}")
            
            cmd = [_get_adb_path(), "-s", connected_device, "shell",
                   "am", "start", "-n", f"{package}/{activity}"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if "Error" not in result.stderr and result.returncode == 0:
                log_callback("✅ Запущено через прямой запуск!")
                return True
            else:
                log_callback(f"❌ Ошибка прямого запуска: {result.stderr}")
                return False

        except Exception as e:
            log_callback(f"❌ Исключение при прямом запуске: {e}")
            return False