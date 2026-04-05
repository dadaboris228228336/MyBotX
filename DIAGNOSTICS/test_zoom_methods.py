#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест альтернативных методов zoom в BlueStacks.
Запуск: python test_zoom_methods.py
"""

import time
import sys
from pathlib import Path

ADB = str(Path(__file__).parent.parent / "BOT_APPLICATIONS" / "platform-tools" / "adb.exe")


def get_device():
    import subprocess
    r = subprocess.run([ADB, "devices"], capture_output=True, text=True)
    for line in r.stdout.splitlines()[1:]:
        if "device" in line and "offline" not in line:
            return line.split()[0]
    return None


def find_bs_window():
    try:
        import win32gui
        BS_TITLES = ["BlueStacks App Player", "BlueStacks", "HD-Player"]
        hwnd = None
        def cb(h, _):
            nonlocal hwnd
            t = win32gui.GetWindowText(h)
            if any(s.lower() in t.lower() for s in BS_TITLES) and win32gui.IsWindowVisible(h):
                hwnd = h
        win32gui.EnumWindows(cb, None)
        return hwnd
    except Exception as e:
        print(f"win32gui error: {e}")
        return None


def test_method_1_ctrl_scroll(zoom_in: bool, seconds: float = 2.0):
    """Метод 1: Ctrl + scroll (текущий)"""
    print(f"\n[Метод 1] Ctrl+scroll {'IN' if zoom_in else 'OUT'} {seconds}с")
    try:
        import pyautogui, win32gui
        hwnd = find_bs_window()
        if not hwnd:
            print("  ❌ Окно не найдено")
            return
        rect = win32gui.GetWindowRect(hwnd)
        cx = (rect[0] + rect[2]) // 2
        cy = (rect[1] + rect[3]) // 2
        print(f"  Окно: {rect}, центр: ({cx}, {cy})")
        pyautogui.moveTo(cx, cy, duration=0.2)
        time.sleep(0.2)
        pyautogui.keyDown("ctrl")
        ticks = int(seconds / 0.05)
        for _ in range(ticks):
            pyautogui.scroll(3 if zoom_in else -3, x=cx, y=cy)
            time.sleep(0.05)
        pyautogui.keyUp("ctrl")
        print("  ✅ Выполнено")
    except Exception as e:
        print(f"  ❌ {e}")


def test_method_2_win32_scroll(zoom_in: bool, times: int = 10):
    """Метод 2: win32api WM_MOUSEWHEEL с Ctrl напрямую в окно"""
    print(f"\n[Метод 2] win32api WM_MOUSEWHEEL {'IN' if zoom_in else 'OUT'} x{times}")
    try:
        import win32gui, win32api, win32con
        hwnd = find_bs_window()
        if not hwnd:
            print("  ❌ Окно не найдено")
            return
        rect = win32gui.GetWindowRect(hwnd)
        cx = (rect[0] + rect[2]) // 2
        cy = (rect[1] + rect[3]) // 2
        lparam = (cy << 16) | (cx & 0xFFFF)
        delta = 120 if zoom_in else -120
        for _ in range(times):
            wparam = (win32con.MK_CONTROL << 16) | (delta & 0xFFFF)
            win32api.SendMessage(hwnd, win32con.WM_MOUSEWHEEL, wparam, lparam)
            time.sleep(0.1)
        print("  ✅ Выполнено")
    except Exception as e:
        print(f"  ❌ {e}")


def test_method_3_adb_keyevent(device: str, zoom_in: bool, times: int = 5):
    """Метод 3: ADB keyevent ZOOM_IN/OUT"""
    print(f"\n[Метод 3] ADB keyevent {'ZOOM_IN(169)' if zoom_in else 'ZOOM_OUT(168)'} x{times}")
    import subprocess
    keycode = 169 if zoom_in else 168
    for _ in range(times):
        r = subprocess.run([ADB, "-s", device, "shell", "input", "keyevent", str(keycode)],
                           capture_output=True)
        time.sleep(0.3)
    print(f"  ✅ Выполнено (exit: {r.returncode})")


def main():
    print("=" * 55)
    print("  BlueStacks Zoom Methods Test")
    print("=" * 55)
    print("\nУбедись что BlueStacks открыт с игрой CoC")
    input("Нажми Enter для начала теста...\n")

    device = get_device()
    if device:
        print(f"✅ ADB устройство: {device}")
    else:
        print("⚠ ADB устройство не найдено")

    print("\n--- ZOOM OUT (отдаление) ---")
    print("Смотри на экран BlueStacks — должно отдалиться")

    input("\nТест 1: Ctrl+scroll (2 сек). Enter...")
    test_method_1_ctrl_scroll(zoom_in=False, seconds=2.0)
    time.sleep(2)

    input("\nТест 2: win32 WM_MOUSEWHEEL. Enter...")
    test_method_2_win32_scroll(zoom_in=False, times=10)
    time.sleep(2)

    if device:
        input("\nТест 3: ADB keyevent. Enter...")
        test_method_3_adb_keyevent(device, zoom_in=False, times=5)
        time.sleep(2)

    print("\n--- ZOOM IN (приближение) ---")
    input("\nТест 1: Ctrl+scroll (2 сек). Enter...")
    test_method_1_ctrl_scroll(zoom_in=True, seconds=2.0)

    print("\n✅ Тест завершён. Какой метод сработал?")
    input("Enter для закрытия...")


if __name__ == "__main__":
    main()
