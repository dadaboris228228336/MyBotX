#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверяет установленные пакеты из requirements.txt.
Выводит статус каждого пакета.
Возвращает exit code 1 если есть недостающие пакеты.
"""
import subprocess
import sys
from pathlib import Path

req_file = Path(__file__).parent / "requirements.txt"

if not req_file.exists():
    print("ERROR: requirements.txt not found!")
    sys.exit(1)

missing = []

for line in req_file.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue

    pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].strip()

    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", pkg_name],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        ver = ""
        for l in result.stdout.splitlines():
            if l.startswith("Version:"):
                ver = l.split(":", 1)[1].strip()
                break
        print(f"   OK  {pkg_name} {ver}")
    else:
        print(f"   MISS {pkg_name} -- not installed")
        missing.append(pkg_name)

if missing:
    print(f"\nMISSING: {len(missing)} package(s)")
    sys.exit(1)
else:
    print("\nALL OK")
    sys.exit(0)
