#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚔️ BOT/bot_04_actions.py
Логика: Готовые действия для Clash of Clans.
        Объединяет screenshot + find_pattern + tap в одну цепочку.
        Пауза между действиями берётся из CONFIG/config.json → bot_settings.action_delay
"""

import time
import json
from pathlib import Path
from .bot_01_screenshot import BotScreenshot
from .bot_02_find_pattern import BotFindPattern
from .bot_03_tap import BotTap


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
    """Готовые действия для Clash of Clans"""

    def __init__(self, device_serial: str, log_callback=None):
        self.device = device_serial
        self.log = log_callback or print
        self.screenshot = BotScreenshot(device_serial, log_callback)
        self.finder = BotFindPattern(log_callback)
        self.tap = BotTap(device_serial, log_callback)

        # Загружаем настройки
        settings = _load_settings()
        self.threshold = float(settings.get("threshold", 0.8))
        self.action_delay = float(settings.get("action_delay", 1.0))
        self.log(f"⚙️ Настройки бота: порог={self.threshold}, пауза={self.action_delay}с")

    def find_and_tap(self, pattern_name: str, threshold: float = 0.8, wait_after: float = 1.0) -> bool:
        """
        Универсальный метод: скриншот → найти паттерн → нажать.

        Args:
            pattern_name: имя паттерна из папки patterns/
            threshold:    порог совпадения (0.8 = 80%)
            wait_after:   пауза после нажатия в секундах

        Returns:
            True если нашёл и нажал, False если не нашёл
        """
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
        """
        Ждёт появления паттерна на экране.

        Returns:
            (x, y) когда паттерн появился, None если timeout
        """
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

    # ─────────────────────────────────────────────
    # ДЕЙСТВИЯ CLASH OF CLANS
    # ─────────────────────────────────────────────

    def collect_resources(self) -> bool:
        """Сбор ресурсов — нажать на все шахты/фермы"""
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
        """Начать атаку — нажать кнопку Attack"""
        self.log("⚔️ Начинаем атаку...")
        return self.find_and_tap("btn_attack", wait_after=2.0)

    def close_popup(self) -> bool:
        """Закрыть всплывающее окно"""
        return self.find_and_tap("btn_close", threshold=0.75, wait_after=0.5)
