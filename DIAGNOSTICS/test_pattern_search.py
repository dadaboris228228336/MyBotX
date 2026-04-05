#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест поиска паттерна на экране BlueStacks.
Запуск: python test_pattern_search.py
Делает скриншот, ищет все паттерны из patterns/ и показывает результат.
"""

import sys
import subprocess
import time
from pathlib import Path

# Пути
ROOT         = Path(__file__).parent.parent
PATTERNS_DIR = ROOT / "CORE" / "processes" / "BOT" / "patterns"
ADB_PATH     = ROOT / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe"

sys.path.insert(0, str(ROOT / "CORE"))


def get_adb():
    return str(ADB_PATH) if ADB_PATH.exists() else "adb"


def get_device() -> str | None:
    """Находит подключённое устройство ADB."""
    result = subprocess.run([get_adb(), "devices"], capture_output=True, text=True)
    for line in result.stdout.splitlines()[1:]:
        if "device" in line and "offline" not in line:
            return line.split()[0]
    return None


def take_screenshot(device: str):
    """Делает скриншот через ADB."""
    import numpy as np
    from PIL import Image
    import io

    result = subprocess.run(
        [get_adb(), "-s", device, "exec-out", "screencap", "-p"],
        capture_output=True, timeout=15
    )
    if result.returncode != 0:
        print(f"❌ Ошибка скриншота: {result.stderr}")
        return None

    img = Image.open(io.BytesIO(result.stdout)).convert("RGB")
    arr = __import__("numpy").array(img)
    return arr[:, :, ::-1]  # RGB → BGR


def test_pattern(screen, pattern_path: Path, threshold: float = 0.8):
    """Тестирует один паттерн на скриншоте."""
    import cv2

    template = cv2.imread(str(pattern_path))
    if template is None:
        return None, 0.0

    if (template.shape[0] > screen.shape[0] or
            template.shape[1] > screen.shape[1]):
        return None, 0.0

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2
        return (cx, cy), max_val

    return None, max_val


def main():
    print("=" * 55)
    print("  Тест поиска паттернов на экране BlueStacks")
    print("=" * 55)

    # Проверяем паттерны
    patterns = list(PATTERNS_DIR.glob("*.png"))
    if not patterns:
        print(f"❌ Нет паттернов в {PATTERNS_DIR}")
        print("   Сначала создайте паттерны через вкладку БОТ → Вырезать паттерн")
        input("\nНажмите Enter...")
        return

    print(f"Найдено паттернов: {len(patterns)}")
    for p in patterns:
        print(f"  • {p.name}")

    # Подключение ADB
    print("\nПодключение к ADB...")
    device = get_device()
    if not device:
        print("❌ Устройство не найдено. Запустите BlueStacks и нажмите СТАРТ в боте.")
        input("\nНажмите Enter...")
        return

    print(f"✅ Устройство: {device}")

    # Скриншот
    print("\nДелаем скриншот...")
    screen = take_screenshot(device)
    if screen is None:
        input("\nНажмите Enter...")
        return

    h, w = screen.shape[:2]
    print(f"✅ Скриншот: {w}x{h} px")

    # Тестируем каждый паттерн
    print("\n" + "-" * 55)
    print(f"{'Паттерн':<25} {'Совпадение':>10}  {'Координаты'}")
    print("-" * 55)

    found_count = 0
    threshold = 0.8

    for pattern_path in sorted(patterns):
        coords, score = test_pattern(screen, pattern_path, threshold)
        name = pattern_path.stem

        if coords:
            print(f"  ✅ {name:<23} {score:.3f}      ({coords[0]}, {coords[1]})")
            found_count += 1
        else:
            status = "слишком большой" if score == 0.0 else f"{score:.3f}"
            print(f"  ❌ {name:<23} {status}")

    print("-" * 55)
    print(f"Найдено: {found_count}/{len(patterns)} паттернов (порог: {threshold})")

    # Сохраняем скриншот с отмеченными паттернами
    try:
        import cv2
        import numpy as np
        debug_img = screen.copy()

        for pattern_path in patterns:
            coords, score = test_pattern(screen, pattern_path, threshold)
            if coords:
                template = cv2.imread(str(pattern_path))
                h_t, w_t = template.shape[:2]
                x, y = coords
                cv2.rectangle(debug_img,
                              (x - w_t//2, y - h_t//2),
                              (x + w_t//2, y + h_t//2),
                              (0, 255, 0), 2)
                cv2.putText(debug_img, pattern_path.stem,
                            (x - w_t//2, y - h_t//2 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        out_path = Path(__file__).parent / "test_result.png"
        cv2.imwrite(str(out_path), debug_img)
        print(f"\n📸 Результат сохранён: {out_path}")
        print("   Зелёные прямоугольники = найденные паттерны")
    except Exception as e:
        print(f"\n⚠ Не удалось сохранить debug-скриншот: {e}")

    input("\nНажмите Enter для закрытия...")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"\n❌ ОШИБКА: {e}")
        print(traceback.format_exc())
        input("Нажмите Enter...")
