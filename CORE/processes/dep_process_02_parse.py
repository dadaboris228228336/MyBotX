#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📦 DepProcess02Parse - ПРОЦЕСС 3: Парсинг requirements.txt
"""

from pathlib import Path


class DepProcess02Parse:
    """ПРОЦЕСС 3: Парсинг requirements.txt (извлечение имен пакетов без версий)"""
    
    @staticmethod
    def parse_requirements(requirements_file: Path, log_callback=None) -> list:
        """
        ПРОЦЕСС 3: Парсинг requirements.txt (извлечение имен пакетов без версий)
        
        Args:
            requirements_file: Путь к файлу requirements.txt
            log_callback: Функция логирования
            
        Returns:
            list: Список имен пакетов без версий
        """
        if not requirements_file.exists():
            if log_callback:
                log_callback(f"❌ Файл {requirements_file} не найден")
            return []

        packages = []
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Извлекаем имя пакета (до == или >= и т.д.)
                        package_name = line.split('==')[0].split('>=')[0]
                        package_name = package_name.split('<=')[0].split('~=')[0]
                        package_name = package_name.strip()
                        if package_name:
                            packages.append(package_name)

            if log_callback:
                log_callback(f"📋 Найдено {len(packages)} пакетов в requirements.txt")
            return packages

        except Exception as e:
            if log_callback:
                log_callback(f"❌ Ошибка чтения {requirements_file}: {e}")
            return []