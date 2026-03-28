#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎮 GameProcess03PlayMarket - ПРОЦЕСС 3: Открытие Play Market
"""

import subprocess
from pathlib import Path


def _get_adb_path() -> str:
    local_adb = Path(__file__).parent.parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"
    return str(local_adb) if local_adb.exists() else "adb"


class GameProcess03PlayMarket:
    """ПРОЦЕСС 3: Открытие Play Market через Android Intent"""
    
    @staticmethod
    def open_play_market(connected_device: str, package: str = None, log_callback=None) -> bool:
        """
        ПРОЦЕСС 3: Открытие Play Market через Android Intent
        
        Args:
            connected_device: ADB serial устройства
            package: Пакет для открытия в Play Market (опционально)
            log_callback: Функция логирования
            
        Returns:
            bool: True если успешно, False если ошибка
        """
        if not connected_device:
            log_callback("❌ Устройство не подключено!")
            return False

        try:
            if package:
                log_callback(f"🛒 Play Market для: {package}")
                uri = f"market://details?id={package}"
            else:
                log_callback("🛒 Play Market")
                uri = "market://apps"

            result = subprocess.run([_get_adb_path(),
                                     "-s",
                                     connected_device,
                                     "shell",
                                     "am",
                                     "start",
                                     "-a",
                                     "android.intent.action.VIEW",
                                     "-d",
                                     uri],
                                    capture_output=True,
                                    text=True,
                                    timeout=10,
                                    check=False)

            if result.returncode == 0:
                log_callback("✅ Play Market открыт")
                return True
            else:
                log_callback(f"❌ Ошибка: {result.stderr}")
                return False

        except Exception as e:
            log_callback(f"❌ Исключение: {e}")
            return False