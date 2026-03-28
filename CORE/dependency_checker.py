#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📦 DependencyChecker v2.0.0 - Сборщик процессов управления зависимостями
Использует разбитые процессы из папки processes/
"""

try:
    from .processes import (
        DepProcess01Init,
        DepProcess02Parse,
        DepProcess03Check,
        DepProcess04Install
    )
except ImportError:
    from processes import (
        DepProcess01Init,
        DepProcess02Parse,
        DepProcess03Check,
        DepProcess04Install
    )


class DependencyChecker:
    """Класс для проверки и установки зависимостей Python (использует процессы)"""

    def __init__(self, requirements_file: str = "requirements.txt"):
        """ПРОЦЕСС 1: Инициализация проверщика зависимостей"""
        params = DepProcess01Init.initialize(requirements_file)
        self.requirements_file = params['requirements_file']
        self.required_packages = params['required_packages']
        self.installed_packages = params['installed_packages']
        self.missing_packages = params['missing_packages']
        self.log_messages = params['log_messages']

    def _add_log(self, message: str) -> None:
        """ПРОЦЕСС 2: Добавление сообщения в лог (сохранение + вывод)"""
        DepProcess01Init.add_log(self.log_messages, message)

    def get_log(self) -> str:
        """ПРОЦЕСС 8: Получение всех логов как строка"""
        return DepProcess01Init.get_log(self.log_messages)

    def clear_log(self) -> None:
        """ПРОЦЕСС 9: Очистка всех логов"""
        DepProcess01Init.clear_log(self.log_messages)

    def get_summary(self) -> dict:
        """ПРОЦЕСС 10: Получение сводки (статистика по пакетам)"""
        return DepProcess01Init.get_summary(self.required_packages, self.missing_packages)

    def _parse_requirements(self) -> list:
        """ПРОЦЕСС 3: Парсинг requirements.txt (извлечение имен пакетов без версий)"""
        return DepProcess02Parse.parse_requirements(self.requirements_file, self._add_log)

    def _get_installed_packages(self) -> list:
        """ПРОЦЕСС 4: Получение установленных пакетов через pip list --format=json"""
        return DepProcess03Check.get_installed_packages(self._add_log)

    def _check_package_installed(self, package: str) -> bool:
        """ПРОЦЕСС 5: Проверка конкретного пакета (точное совпадение + альтернативы)"""
        return DepProcess03Check.check_package_installed(package, self.installed_packages)

    def check_dependencies(self) -> dict:
        """ПРОЦЕСС 6: Полная проверка зависимостей (сравнение требуемых и установленных)"""
        self._add_log("🔍 Начинаем проверку зависимостей...")

        # Читаем requirements.txt
        self.required_packages = self._parse_requirements()
        if not self.required_packages:
            self._add_log("⚠️ Нет пакетов для проверки")
            return {}

        # Получаем список установленных пакетов
        self.installed_packages = self._get_installed_packages()

        # Проверяем зависимости
        check_result = DepProcess03Check.check_dependencies(
            self.required_packages, self.installed_packages, self._add_log
        )
        
        self.missing_packages = check_result['missing_packages']
        return check_result['results']

    def install_missing_packages(self) -> bool:
        """ПРОЦЕСС 7: Установка недостающих пакетов через pip install"""
        return DepProcess04Install.install_missing_packages(self.missing_packages, self._add_log)