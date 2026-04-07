#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎮 GameProcess06LaunchMonkey - ПРОЦЕСС 6: Приоритетный запуск через monkey
"""

import subprocess
from pathlib import Path


def _get_adb_path() -> str:
    local_adb = Path(__file__).parent.parent.parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    return str(local_adb) if local_adb.exists() else "adb"


class GameProcess06LaunchMonkey:
    """ПРОЦЕСС 6: СПОСОБ 1 - Приоритетный запуск через monkey"""
    
    @staticmethod
    def launch_monkey(connected_device: str, package: str, log_callback) -> bool:
        """
        ПРОЦЕСС 6: СПОСОБ 1 - Приоритетный запуск через monkey (только для Clash of Clans)
        
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

        # Monkey только для Clash of Clans
        if package != 'com.supercell.clashofclans':
            log_callback("⚠️ Monkey доступен только для Clash of Clans")
            return False

        try:
            log_callback("🐒 Пробуем monkey способ...")

            monkey_cmd = [
                _get_adb_path(),
                "-s",
                connected_device,
                "shell",
                "monkey",
                "-p",
                package,
                "-c",
                "android.intent.category.LAUNCHER",
                "1"]

            result = subprocess.run(
                monkey_cmd,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if (result.returncode == 0 and
                    "Events injected: 1" in result.stdout):
                log_callback("✅ Запущено через monkey!")
                return True
            else:
                log_callback(f"❌ Monkey не сработал: {result.stderr}")
                return False

        except Exception as e:
            log_callback(f"❌ Исключение при monkey: {e}")
            return False