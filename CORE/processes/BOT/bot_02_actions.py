#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚔️ BOT/bot_02_actions.py
Оркестрация действий Clash of Clans.
Делегирует захват экрана → SCREENSHOT, поиск паттернов → OPENCV, нажатия → BotTap.
"""

import time
import json
from pathlib import Path

from ..SCREENSHOT import ScreenshotCapture
from ..OPENCV import TemplateMatch
from .bot_01_tap import BotTap

PATTERNS_DIR = Path(__file__).parent / "patterns"


def _load_settings() -> dict:
    """Загружает настройки из config.json"""
    config_path = Path(__file__).parent.parent.parent.parent / "CONFIG" / "config.json"
    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg.get("bot_settings", {})
    except Exception:
        return {}


class BotActions:
    """Готовые действия для Clash of Clans."""

    def __init__(self, device_serial: str, log_callback=None):
        self.device = device_serial
        self.log = log_callback or print
        self.screenshot = ScreenshotCapture(device_serial, log_callback)
        self.finder = TemplateMatch(PATTERNS_DIR, log_callback)
        self.tap = BotTap(device_serial, log_callback)

        settings = _load_settings()
        self.threshold = float(settings.get("threshold", 0.8))
        self.action_delay = float(settings.get("action_delay", 1.0))
        self.log(f"⚙️ Настройки бота: порог={self.threshold}, пауза={self.action_delay}с")

    def find_and_tap(self, pattern_name: str, threshold: float = 0.8,
                     wait_after: float = 1.0) -> bool:
        """Скриншот → найти паттерн → нажать. True если нашёл и нажал."""
        self.log(f"🔍 Ищем: {pattern_name}")
        screen = self.screenshot.capture()
        if screen is None:
            return False

        coords = self.finder.find(screen, pattern_name, threshold)
        if coords is None:
            return False

        return self.tap.tap_and_wait(coords[0], coords[1], wait_after)

    def wait_for_pattern(self, pattern_name: str, timeout: float = 30.0,
                         interval: float = 2.0, threshold: float = 0.8) -> tuple | None:
        """Ждёт появления паттерна. Возвращает (x,y) или None при таймауте."""
        self.log(f"⏳ Ждём появления: {pattern_name} (макс {timeout}с)")
        elapsed = 0
        while elapsed < timeout:
            screen = self.screenshot.capture()
            if screen is not None:
                coords = self.finder.find(screen, pattern_name, threshold)
                if coords:
                    self.log(f"✅ Паттерн появился: {pattern_name}")
                    return coords
            time.sleep(interval)
            elapsed += interval

        self.log(f"❌ Паттерн не появился за {timeout}с: {pattern_name}")
        return None

    def collect_resources(self) -> bool:
        """Сбор ресурсов — нажать на все шахты/фермы."""
        self.log("💰 Сбор ресурсов...")
        screen = self.screenshot.capture()
        if screen is None:
            return False

        collected = 0
        for pattern in ["gold_mine_full", "elixir_collector_full", "dark_elixir_full"]:
            points = self.finder.find_all(screen, pattern)
            for pt in points:
                self.tap.tap_and_wait(pt[0], pt[1], 0.5)
                collected += 1

        self.log(f"✅ Собрано ресурсов: {collected}")
        return collected > 0

    def start_attack(self) -> bool:
        """Начать атаку."""
        self.log("⚔️ Начинаем атаку...")
        return self.find_and_tap("btn_attack", wait_after=2.0)

    def close_popup(self) -> bool:
        """Закрыть всплывающее окно."""
        return self.find_and_tap("btn_close", threshold=0.75, wait_after=0.5)
