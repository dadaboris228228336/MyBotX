#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCENARIO/scenario_03_storage.py
Сохранение и загрузка сценариев в JSON файлы.
"""

import json
from pathlib import Path

SCENARIOS_DIR = Path(__file__).parent.parent.parent / "temp" / "scenarios"


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
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
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
