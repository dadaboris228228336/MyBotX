#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📦 DepProcess04Install - ПРОЦЕСС 7: Установка пакетов
"""

import subprocess
import sys
from pathlib import Path


def _get_python() -> str:
    exe = Path(sys.executable)
    if exe.name.lower() == "python.exe":
        return str(exe)
    for candidate in [exe.parent / "python.exe", exe.parent / "python" / "python.exe"]:
        if candidate.exists():
            return str(candidate)
    for path in [
        Path(r"C:\Program Files\Python310\python.exe"),
        Path(r"C:\Program Files (x86)\Python310\python.exe"),
    ]:
        if path.exists():
            return str(path)
    return "python"


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
                    [_get_python(), "-m", "pip", "install", package],
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