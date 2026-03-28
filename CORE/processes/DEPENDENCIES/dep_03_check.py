#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📦 DepProcess03Check - ПРОЦЕСС 4-6: Проверка пакетов
"""

import json
import subprocess
import sys


class DepProcess03Check:
    """ПРОЦЕСС 4-6: Получение и проверка установленных пакетов"""
    
    @staticmethod
    def get_installed_packages(log_callback=None) -> list:
        """
        ПРОЦЕСС 4: Получение установленных пакетов через pip list --format=json
        
        Args:
            log_callback: Функция логирования
            
        Returns:
            list: Список имен установленных пакетов
        """
        try:
            if log_callback:
                log_callback("🔍 Получение списка установленных пакетов...")

            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )

            packages_info = json.loads(result.stdout)
            installed = [pkg['name'].lower() for pkg in packages_info]

            if log_callback:
                log_callback(f"📦 Установлено {len(installed)} пакетов")
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

        # Проверяем каждый пакет
        results = {}
        missing_packages = []

        if log_callback:
            log_callback("📋 Проверка каждого пакета:")

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

        # Итоговая статистика
        total = len(required_packages)
        installed_count = len(required_packages) - len(missing_packages)

        if log_callback:
            log_callback("\n📊 Результат проверки:")
            log_callback(f"  • Всего пакетов: {total}")
            log_callback(f"  • Установлено: {installed_count}")
            log_callback(f"  • Недостаёт: {len(missing_packages)}")

            if missing_packages:
                log_callback("\n❌ Недостающие пакеты:")
                for pkg in missing_packages:
                    log_callback(f"  • {pkg}")
            else:
                log_callback("\n🎉 Все пакеты установлены!")

        return {
            'results': results,
            'missing_packages': missing_packages
        }