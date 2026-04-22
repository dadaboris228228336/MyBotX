#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCENARIO/scenario_03_storage.py
Сохранение и загрузка сценариев в JSON файлы.
"""

import json
from pathlib import Path

# Сценарии хранятся в my_bot/scenarios/ — постоянная папка вне temp
SCENARIOS_DIR = Path(__file__).parent.parent.parent.parent / "my_bot" / "scenarios"


class ScenarioStorage:

    @staticmethod
    def ensure_dir():
        SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def list_scenarios() -> list[str]:
        """Возвращает список имён сценариев."""
        ScenarioStorage.ensure_dir()
        return sorted(f.stem for f in SCENARIOS_DIR.glob("*.json"))

    @staticmethod
    def load(name: str) -> list[dict]:
        """Загружает шаги сценария по имени."""
        path = SCENARIOS_DIR / f"{name}.json"
        if not path.exists():
            # GAP Req 4.3: returns [] silently; requirement says caller should log
            # "Файл сценария не найден" to BotLog. The storage layer has no log_callback,
            # so the caller (ScenarioEditor._on_scenario_change) must handle this.
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            # GAP Req 4.4: returns [] silently on bad JSON; requirement says caller should
            # log an error message to BotLog. Same note: caller must handle this.
            return []

    @staticmethod
    def save(name: str, steps: list[dict]):
        """Сохраняет шаги сценария."""
        ScenarioStorage.ensure_dir()
        path = SCENARIOS_DIR / f"{name}.json"
        path.write_text(json.dumps(steps, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    @staticmethod
    def create(name: str):
        """Создаёт пустой сценарий."""
        ScenarioStorage.save(name, [])

    @staticmethod
    def rename(old_name: str, new_name: str):
        """Переименовывает сценарий."""
        old = SCENARIOS_DIR / f"{old_name}.json"
        new = SCENARIOS_DIR / f"{new_name}.json"
        if old.exists():
            old.rename(new)

    @staticmethod
    def delete(name: str):
        """Удаляет сценарий."""
        path = SCENARIOS_DIR / f"{name}.json"
        path.unlink(missing_ok=True)
