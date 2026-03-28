#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎮 GameProcess05LaunchIntent - ПРОЦЕСС 5: Запуск через LAUNCHER INTENT
"""

import subprocess
from pathlib import Path


def _get_adb_path() -> str:
    local_adb = Path(__file__).parent.parent.parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    return str(local_adb) if local_adb.exists() else "adb"


class GameProcess05LaunchIntent:
    """ПРОЦЕСС 5: СПОСОБ 2 - Запуск через LAUNCHER INTENT"""
    
    @staticmethod
    def launch_intent(connected_device: str, package: str, log_callback) -> bool:
        """
        ПРОЦЕСС 5: СПОСОБ 2 - Запуск через LAUNCHER INTENT
        
        Args:
            connected_device: ADB serial устройства
            package: Имя пакета
            log_callback: Функция логирования
            
        Returns:
            bool: True если успешно, False если ошибка
        """
        if not connected_device:
            log_callback("❌ Устройство не подключено!")
            return False

        try:
            log_callback(f"🎮 LAUNCHER INTENT запуск: {package}")
            log_callback("   Используем LAUNCHER INTENT")
            
            cmd = [
                _get_adb_path(),
                "-s",
                connected_device,
                "shell",
                "am",
                "start",
                "-a",
                "android.intent.action.MAIN",
                "-c",
                "android.intent.category.LAUNCHER",
                package]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
                check=False
            )

            if "Error" not in result.stderr and result.returncode == 0:
                log_callback("✅ Запущено через LAUNCHER INTENT!")
                return True
            else:
                log_callback(f"❌ Ошибка LAUNCHER INTENT: {result.stderr}")
                return False

        except Exception as e:
            log_callback(f"❌ Исключение при LAUNCHER INTENT: {e}")
            return False