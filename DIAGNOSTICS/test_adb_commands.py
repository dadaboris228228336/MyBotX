#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест ADB команд — проверяет каждую команду и показывает результат.
Запуск: python test_adb_commands.py
"""

import subprocess
import time
import sys
from pathlib import Path

ADB = str(Path(__file__).parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe")
if not Path(ADB).exists():
    ADB = "adb"


def run(device, args, label):
    print(f"\n[TEST] {label}")
    cmd = [ADB, "-s", device] + args
    print(f"  CMD: {' '.join(cmd)}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(f"  EXIT: {r.returncode}")
        if r.stdout.strip():
            print(f"  OUT:  {r.stdout.strip()[:200]}")
        if r.stderr.strip():
            print(f"  ERR:  {r.stderr.strip()[:200]}")
        return r.returncode == 0
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        return False


def get_device():
    r = subprocess.run([ADB, "devices"], capture_output=True, text=True)
    print(r.stdout)
    for line in r.stdout.splitlines()[1:]:
        if "device" in line and "offline" not in line:
            return line.split()[0]
    return None


def main():
    print("=" * 55)
    print("  ADB Commands Diagnostic Test")
    print("=" * 55)

    device = get_device()
    if not device:
        print("❌ Устройство не найдено!")
        input("\nНажмите Enter...")
        return

    print(f"✅ Устройство: {device}")
    print("\nНачинаем тесты через 3 секунды...")
    time.sleep(3)

    # 1. Tap
    print("\n--- TAP ---")
    run(device, ["shell", "input", "tap", "540", "960"], "tap (540, 960)")
    time.sleep(1)

    # 2. Swipe
    print("\n--- SWIPE ---")
    run(device, ["shell", "input", "swipe", "300", "960", "700", "960", "300"],
        "swipe left->right")
    time.sleep(1)

    # 3. HOME
    print("\n--- HOME ---")
    run(device, ["shell", "input", "keyevent", "3"], "keyevent HOME (3)")
    time.sleep(1)

    # 4. BACK
    print("\n--- BACK ---")
    run(device, ["shell", "input", "keyevent", "4"], "keyevent BACK (4)")
    time.sleep(1)

    # 5. ZOOM OUT keyevent
    print("\n--- ZOOM OUT (keyevent 168) ---")
    run(device, ["shell", "input", "keyevent", "168"], "keyevent ZOOM_OUT (168)")
    time.sleep(1)

    # 6. ZOOM IN keyevent
    print("\n--- ZOOM IN (keyevent 169) ---")
    run(device, ["shell", "input", "keyevent", "169"], "keyevent ZOOM_IN (169)")
    time.sleep(1)

    # 7. Pinch out через параллельные свайпы
    print("\n--- PINCH OUT (parallel swipe) ---")
    import threading
    cx, cy, offset = 540, 960, 250

    def s1():
        run(device, ["shell", "input", "swipe",
                     str(cx-50), str(cy), str(cx-offset), str(cy), "400"],
            "swipe left (pinch out)")

    def s2():
        run(device, ["shell", "input", "swipe",
                     str(cx+50), str(cy), str(cx+offset), str(cy), "400"],
            "swipe right (pinch out)")

    t1 = threading.Thread(target=s1)
    t2 = threading.Thread(target=s2)
    t1.start(); t2.start()
    t1.join();  t2.join()
    time.sleep(1)

    # 8. Проверка разрешения экрана
    print("\n--- SCREEN SIZE ---")
    run(device, ["shell", "wm", "size"], "wm size")

    # 9. Проверка текущего приложения
    print("\n--- CURRENT APP ---")
    run(device, ["shell", "dumpsys", "window", "windows"],
        "current focused window (first 500 chars)")

    print("\n" + "=" * 55)
    print("Тест завершён. Проверь какие команды сработали.")
    input("\nНажмите Enter для закрытия...")


if __name__ == "__main__":
    main()
