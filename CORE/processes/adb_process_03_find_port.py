#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ADBProcess03FindPort - ПРОЦЕСС 3: Поиск доступного ADB порта
"""

from .adb_process_02_check_port import ADBProcess02CheckPort


class ADBProcess03FindPort:
    """ПРОЦЕСС 3: Поиск доступного ADB порта (проверка 5555-5559)"""
    
    @staticmethod
    def find_available_adb_port(ports: list = None, log_callback=None) -> int | None:
        """
        ПРОЦЕСС 3: Поиск доступного ADB порта (проверка 5555-5559)
        
        Args:
            ports: Список портов для проверки
            log_callback: Функция логирования
            
        Returns:
            int | None: Номер найденного порта или None
        """
        if ports is None:
            ports = [5555, 5556, 5557, 5558, 5559]
        
        if log_callback:
            log_callback("🔍 Быстрая проверка портов: {}".format(ports))

        for port in ports:
            if ADBProcess02CheckPort.is_port_open("127.0.0.1", port):
                if log_callback:
                    log_callback("✅ Найден открытый порт: {}".format(port))
                return port

        if log_callback:
            log_callback("❌ Доступные порты не найдены")
        return None
    
    @staticmethod
    def get_all_open_ports(log_callback=None) -> list:
        """
        ПРОЦЕСС 4: Получение списка всех открытых ADB портов
        
        Args:
            log_callback: Функция логирования
            
        Returns:
            list: Список открытых портов
        """
        ports = [5555, 5556, 5557, 5558, 5559]
        open_ports = []
        
        for port in ports:
            if ADBProcess02CheckPort.is_port_open("127.0.0.1", port):
                open_ports.append(port)
        
        if log_callback:
            log_callback(f"📋 Найдено открытых портов: {len(open_ports)}")
            
        return open_ports