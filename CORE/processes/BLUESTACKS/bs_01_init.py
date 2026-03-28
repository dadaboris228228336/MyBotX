#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 BSProcess01Init - ПРОЦЕСС 1: Инициализация BlueStacksManager
"""

import json
import time
from pathlib import Path


class BSProcess01Init:
    """ПРОЦЕСС 1: Инициализация с автоматическим поиском BlueStacks"""
    
    @staticmethod
    def initialize():
        """
        ПРОЦЕСС 1: Инициализация с автоматическим поиском BlueStacks
        
        Returns:
            dict: Инициализированные параметры
        """
        # Используем общий config.json вместо отдельного кэша
        config_file = Path(__file__).parent.parent.parent.parent / "CONFIG" / "config.json"
        
        return {
            'config_file': config_file,
            'bluestacks_path': None,
            'all_found_paths': []
        }
    
    @staticmethod
    def load_from_config(config_file: Path) -> str | None:
        """
        ПРОЦЕСС 4: Загрузка пути из config.json
        
        Args:
            config_file: Путь к файлу config.json
            
        Returns:
            str | None: Путь из конфига или None
        """
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ищем путь BlueStacks в конфиге
                    return data.get('bluestacks', {}).get('path')
        except Exception:
            pass
        return None
    
    @staticmethod
    def save_to_config(config_file: Path, path: str):
        """
        ПРОЦЕСС 5: Сохранение найденного пути в config.json
        
        Args:
            config_file: Путь к файлу config.json
            path: Путь для сохранения
        """
        try:
            # Читаем существующий конфиг
            config_data = {}
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            
            # Добавляем/обновляем секцию BlueStacks
            if 'bluestacks' not in config_data:
                config_data['bluestacks'] = {}
            
            config_data['bluestacks']['path'] = path
            config_data['bluestacks']['cached_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            config_data['bluestacks']['auto_detected'] = True
            
            # Сохраняем обновленный конфиг
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception:
            pass