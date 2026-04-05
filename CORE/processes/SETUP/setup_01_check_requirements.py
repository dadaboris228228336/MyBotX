#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SETUP/setup_01_check_requirements.py
Проверка и установка Python-зависимостей из requirements.txt.
"""

import subprocess
import sys
from pathlib import Path

REQ_FILE = Path(__file__).parent.parent.parent / "requirements.txt"


def check_all() -> tuple[list[str], list[str]]:
    """
    Проверяет все пакеты из requirements.txt.
    Возвращает (installed, missing) — списки имён пакетов.
    """
    if not REQ_FILE.exists():
        return [], []

    installed = []
    missing   = []

    for line in REQ_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        pkg = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", pkg],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            ver = ""
            for l in result.stdout.splitlines():
                if l.startswith("Version:"):
                    ver = l.split(":", 1)[1].strip()
                    break
            installed.append(f"{pkg} {ver}")
        else:
            missing.append(pkg)

    return installed, missing


def install_missing(packages: list[str]) -> bool:
    """Устанавливает недостающие пакеты. Возвращает True если успешно."""
    if not packages:
        return True
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(REQ_FILE)],
        capture_output=False
    )
    return result.returncode == 0


if __name__ == "__main__":
    # Запуск напрямую — как check_requirements.py
    installed, missing = check_all()
    for p in installed:
        print(f"   OK  {p}")
    for p in missing:
        print(f"   MISS {p} -- not installed")
    if missing:
        print(f"\nMISSING: {len(missing)} package(s)")
        sys.exit(1)
    else:
        print("\nALL OK")
        sys.exit(0)
