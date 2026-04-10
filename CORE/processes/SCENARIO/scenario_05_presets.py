#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCENARIO/scenario_05_presets.py
Работа с пресет-сценариями (только чтение в обычном режиме,
редактирование доступно только при dev_mode=true).
"""

import json
from pathlib import Path

PRESETS_DIR = Path(__file__).parent.parent.parent.parent / "my_bot" / "presets"
CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "CONFIG" / "config.json"


def _is_dev_mode() -> bool:
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return bool(data.get("dev_mode", False))
    except Exception:
        return False


class PresetStorage:

    @staticmethod
    def ensure_dir():
        PRESETS_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def list_presets() -> list[dict]:
        """Возвращает список пресетов: [{name, description, version}]."""
        PresetStorage.ensure_dir()
        result = []
        for f in sorted(PRESETS_DIR.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                result.append({
                    "name":        data.get("name", f.stem),
                    "description": data.get("description", ""),
                    "version":     data.get("version", "1.0"),
                    "file":        f.stem,
                })
            except Exception:
                pass
        return result

    @staticmethod
    def load_steps(file_stem: str) -> list[dict]:
        """Загружает шаги пресета по имени файла (без .json)."""
        path = PRESETS_DIR / f"{file_stem}.json"
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("steps", [])
        except Exception:
            return []

    @staticmethod
    def load_meta(file_stem: str) -> dict:
        """Загружает метаданные пресета."""
        path = PRESETS_DIR / f"{file_stem}.json"
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return {k: v for k, v in data.items() if k != "steps"}
        except Exception:
            return {}

    @staticmethod
    def save(file_stem: str, meta: dict, steps: list[dict]):
        """Сохраняет пресет. Только в dev_mode."""
        if not _is_dev_mode():
            raise PermissionError("Редактирование пресетов доступно только в режиме разработчика.")
        PresetStorage.ensure_dir()
        path = PRESETS_DIR / f"{file_stem}.json"
        data = dict(meta)
        data["steps"] = steps
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def delete(file_stem: str):
        """Удаляет пресет. Только в dev_mode."""
        if not _is_dev_mode():
            raise PermissionError("Удаление пресетов доступно только в режиме разработчика.")
        path = PRESETS_DIR / f"{file_stem}.json"
        path.unlink(missing_ok=True)

    @staticmethod
    def is_dev_mode() -> bool:
        return _is_dev_mode()
