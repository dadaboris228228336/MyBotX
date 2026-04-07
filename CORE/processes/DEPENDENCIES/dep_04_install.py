#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📦 DepProcess04Install - ПРОЦЕСС 7: Установка пакетов
"""

import subprocess
import sys


class DepProcess04Install:
    """ПРОЦЕСС 7: Установка недостающих пакетов через pip install"""
    
    @staticmethod
    def install_missing_packages(missing_packages: list, log_callback=None) -> bool:
        """
        ПРОЦЕСС 7: Установка недостающих пакетов через pip install
        
        Args:
            missing_packages: Список недостающих пакетов
            log_callback: Функция логирования
            
        Returns:
            bool: True если все пакеты успешно установлены
        """
        if not missing_packages:
            if log_callback:
                log_callback("✅ Нет пакетов для установки")
            return True

        if log_callback:
            log_callback(f"📦 Установка {len(missing_packages)} пакетов...")

        success_count = 0

        for package in missing_packages:
            if log_callback:
                log_callback(f"📦 Устанавливаем {package}...")

            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                if log_callback:
                    log_callback(f"  ✅ {package} установлен успешно")
                success_count += 1

            except subprocess.TimeoutExpired:
                if log_callback:
                    log_callback(f"  ⏱️ Timeout при установке {package}")
            except subprocess.CalledProcessError as e:
                if log_callback:
                    log_callback(f"  ❌ Ошибка установки {package}: {e}")
                    if e.stderr:
                        log_callback(f"     Детали: {e.stderr}")
            except Exception as e:
                if log_callback:
                    log_callback(f"  ❌ Неожиданная ошибка при установке {package}: {e}")

        # Итоговая статистика
        total = len(missing_packages)
        if log_callback:
            log_callback("\n📊 Результат установки:")
            log_callback(f"  • Всего к установке: {total}")
            log_callback(f"  • Успешно установлено: {success_count}")
            log_callback(f"  • Ошибок: {total - success_count}")

        return success_count == total