#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ADBProcess02CheckPort - ПРОЦЕСС 2: Проверка открытого порта
"""

import socket


class ADBProcess02CheckPort:
    """ПРОЦЕСС 2: Быстрая проверка открытого порта через socket (1 сек таймаут)"""
    
    @staticmethod
    def is_port_open(host: str = "127.0.0.1", port: int = 5555) -> bool:
        """
        ПРОЦЕСС 2: Быстрая проверка открытого порта через socket (1 сек таймаут)
        
        Args:
            host: IP адрес хоста
            port: Номер порта
            
        Returns:
            bool: True если порт открыт, False если закрыт
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)  # ✅ Уменьшили таймаут до 1 сек
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False