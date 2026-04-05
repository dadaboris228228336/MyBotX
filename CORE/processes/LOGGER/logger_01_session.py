#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOGGER/logger_01_session.py
Логирование текущей сессии в файл logs/session.log.
- При старте: папка logs/ очищается, создаётся новый файл
- При закрытии: файл удаляется
"""

import atexit
from pathlib import Path
from datetime import datetime

LOGS_DIR = Path(__file__).parent.parent.parent.parent / "logs"
LOG_FILE = LOGS_DIR / "session.log"

_log_file_handle = None


def init():
    """Инициализация логгера — вызывать при старте приложения."""
    global _log_file_handle

    LOGS_DIR.mkdir(exist_ok=True)
    for f in LOGS_DIR.glob("*.log"):
        try:
            f.unlink()
        except Exception:
            pass

    _log_file_handle = open(LOG_FILE, "w", encoding="utf-8", buffering=1)
    _log_file_handle.write(
        f"=== MyBotX Session Log — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n"
    )
    atexit.register(cleanup)


def write(message: str, tag: str = "info"):
    """Записывает строку в лог-файл."""
    if _log_file_handle and not _log_file_handle.closed:
        ts  = datetime.now().strftime("%H:%M:%S")
        lvl = tag.upper().ljust(7)
        try:
            _log_file_handle.write(f"[{ts}] [{lvl}] {message}\n")
        except Exception:
            pass


def cleanup():
    """Закрывает и удаляет лог-файл при выходе."""
    global _log_file_handle
    if _log_file_handle and not _log_file_handle.closed:
        _log_file_handle.close()
    try:
        if LOG_FILE.exists():
            LOG_FILE.unlink()
    except Exception:
        pass
