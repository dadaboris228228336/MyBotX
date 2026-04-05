#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
session_logger.py — обёртка для обратной совместимости.
Логика перенесена в processes/LOGGER/logger_01_session.py
"""
from processes.LOGGER.logger_01_session import init, write, cleanup as _cleanup


def _cleanup_compat():
    _cleanup()
