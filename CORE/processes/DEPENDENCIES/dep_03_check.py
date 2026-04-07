#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📦 DepProcess03Check - ПРОЦЕСС 4-6: Проверка пакетов
"""

import json
import subprocess
import sys
from pathlib import Path


def _get_python() -> str:
    """
    Возвращает путь к реальному python.exe.
    В PyInstaller-сборке sys.executable указывает на MyBotX.exe,
    поэтому ищем python.exe через where и стандартные пути.
    """
    # Если запущены как обычный скрипт — sys.executable это python.exe
    exe = Path(sys.executable)
    if exe.name.lower() == "python.exe":
        return str(exe)

    # Ищем через where (работает если Python в PATH)
    try:
        result = subprocess.run(
            ["where", "python"],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                p = Path(line.strip())
                if p.exists() and p.name.lower() == "python.exe":
                    return str(p)
    except Exception:
        pass

    # Стандартные пути установки Python 3.10
    username = Path.home().name
    candidates = [
        Path(r"C:\Program Files\Python310\python.exe"),
        Path(r"C:\Program Files (x86)\Python310\python.exe"),
        Path.home() / r"AppData\Local\Programs\Python\Python310\python.exe",
        Path.home() / r"AppData\Local\Programs\Python\Python311\python.exe",
        Path.home() / r"AppData\Local\Programs\Python\Python312\python.exe",
    ]
    for p in candidates:
        if p.exists():
            return str(p)

    return "python"


class DepProcess03Check:
    """ПРОЦЕСС 4-6: Получение и проверка установленных пакетов"""
    
    @staticmethod
    def get_installed_packages(log_callback=None) -> list:
        """
        ПРОЦЕСС 4: Получение установленных пакетов через pip list --format=json
        """
        # Если запущены из PyInstaller EXE — все пакеты уже встроены, проверка не нужна
        if getattr(sys, 'frozen', False):
            if log_callback:
                log_callback("✅ Запущено из EXE — все пакеты встроены")
            return ["psutil", "pillow", "opencv-python", "numpy", "pywin32", "pyautogui"]

        try:
            if log_callback:
                log_callback("🔍 Проверка наших пакетов...")

            result = subprocess.run(
                [_get_python(), "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            packages_info = json.loads(result.stdout)
            # Возвращаем только имена — проверка идёт по required_packages
            installed = [pkg['name'].lower() for pkg in packages_info]

            if log_callback:
                log_callback(f"📦 pip list получен ({len(installed)} пакетов в системе)")
            return installed

        except subprocess.TimeoutExpired:
            if log_callback:
                log_callback("⏱️ Timeout при получении списка пакетов")
            return []
        except subprocess.CalledProcessError as e:
            if log_callback:
                log_callback(f"❌ Ошибка pip list: {e}")
            return []
        except json.JSONDecodeError as e:
            if log_callback:
                log_callback(f"❌ Ошибка парсинга JSON: {e}")
            return []
        except Exception as e:
            if log_callback:
                log_callback(f"❌ Неожиданная ошибка: {e}")
            return []
    
    @staticmethod
    def check_package_installed(package: str, installed_packages: list) -> bool:
        """
        ПРОЦЕСС 5: Проверка конкретного пакета (точное совпадение + альтернативы)
        
        Args:
            package: Имя пакета для проверки
            installed_packages: Список установленных пакетов
            
        Returns:
            bool: True если пакет установлен
        """
        package_lower = package.lower()

        # Проверяем точное совпадение
        if package_lower in installed_packages:
            return True

        # Проверяем альтернативные имена для некоторых пакетов
        alternatives = {
            'pillow': ['pil'],
            'beautifulsoup4': ['bs4'],
            'pyyaml': ['yaml'],
            'python-dateutil': ['dateutil'],
        }

        if package_lower in alternatives:
            for alt in alternatives[package_lower]:
                if alt in installed_packages:
                    return True

        return False
    
    @staticmethod
    def check_dependencies(required_packages: list, installed_packages: list, log_callback=None) -> dict:
        """
        ПРОЦЕСС 6: Полная проверка зависимостей (сравнение требуемых и установленных)
        
        Args:
            required_packages: Список требуемых пакетов
            installed_packages: Список установленных пакетов
            log_callback: Функция логирования
            
        Returns:
            dict: Результаты проверки и список недостающих пакетов
        """
        if log_callback:
            log_callback("🔍 Начинаем проверку зависимостей...")

        if not required_packages:
            if log_callback:
                log_callback("⚠️ Нет пакетов для проверки")
            return {'results': {}, 'missing_packages': []}

        results = {}
        missing_packages = []

        if log_callback:
            log_callback(f"📋 Проверяем {len(required_packages)} пакетов из requirements.txt:")

        for package in required_packages:
            is_installed = DepProcess03Check.check_package_installed(package, installed_packages)
            results[package] = is_installed
            if is_installed:
                if log_callback:
                    log_callback(f"  ✅ {package}")
            else:
                if log_callback:
                    log_callback(f"  ❌ {package}")
                missing_packages.append(package)

        installed_count = len(required_packages) - len(missing_packages)
        if log_callback:
            log_callback(f"\n📊 Наших пакетов: {len(required_packages)} | Установлено: {installed_count} | Нет: {len(missing_packages)}")
            if not missing_packages:
                log_callback("🎉 Все пакеты установлены!")

        return {'results': results, 'missing_packages': missing_packages}