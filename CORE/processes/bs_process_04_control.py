#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 BSProcess04Control - ПРОЦЕСС 10-13: Управление BlueStacks
"""

import subprocess
import time
import psutil


class BSProcess04Control:
    """ПРОЦЕСС 10-13: Запуск, завершение и управление BlueStacks"""
    
    @staticmethod
    def launch(bluestacks_path: str) -> tuple:
        """
        ПРОЦЕСС 10: Запуск BlueStacks через subprocess.Popen
        
        Args:
            bluestacks_path: Путь к BlueStacks
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not bluestacks_path:
            return False, "BlueStacks не найден"

        if BSProcess04Control.is_running():
            return True, "BlueStacks уже запущен"

        try:
            subprocess.Popen([bluestacks_path], shell=True)
            return True, "BlueStacks запущен"
        except Exception as e:
            return False, f"Ошибка запуска: {str(e)}"
    
    @staticmethod
    def is_running() -> bool:
        """Проверка запуска (дублирует bs_process_03_status для удобства)"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'HD-Player.exe' in proc.info['name']:
                    return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def kill_all_processes() -> bool:
        """
        ПРОЦЕСС 11: Завершение всех процессов BlueStacks (terminate -> kill)
        
        Returns:
            bool: True если процессы были завершены
        """
        try:
            killed_count = 0
            bluestacks_processes = [
                'HD-Player.exe',
                'BlueStacks.exe',
                'BstkSVC.exe',
                'HD-Agent.exe',
                'HD-LogRotatorService.exe'
            ]

            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] in bluestacks_processes:
                    try:
                        proc.terminate()
                        killed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

            # Ждем немного и принудительно завершаем оставшиеся
            time.sleep(2)

            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] in bluestacks_processes:
                    try:
                        proc.kill()
                        killed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

            return killed_count > 0

        except Exception:
            return False
    
    @staticmethod
    def restart(bluestacks_path: str) -> tuple:
        """
        ПРОЦЕСС 12: Перезапуск BlueStacks (завершение + запуск)
        
        Args:
            bluestacks_path: Путь к BlueStacks
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Завершаем все процессы
        if BSProcess04Control.is_running():
            if not BSProcess04Control.kill_all_processes():
                return False, "Не удалось завершить процессы BlueStacks"

            # Ждем полного завершения
            time.sleep(3)

        # Запускаем заново
        return BSProcess04Control.launch(bluestacks_path)
    
    @staticmethod
    def get_bluestacks_processes() -> list:
        """
        ПРОЦЕСС 13: Получение информации о запущенных процессах BlueStacks
        
        Returns:
            list: Список процессов с информацией
        """
        processes = []
        bluestacks_names = [
            'HD-Player.exe',
            'BlueStacks.exe',
            'BstkSVC.exe',
            'HD-Agent.exe'
        ]

        try:
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                if proc.info['name'] in bluestacks_names:
                    memory_mb = proc.info['memory_info'].rss // (1024 * 1024)
                    processes.append({
                        'name': proc.info['name'],
                        'pid': proc.info['pid'],
                        'memory': f"{memory_mb}MB"
                    })
        except Exception:
            pass

        return processes