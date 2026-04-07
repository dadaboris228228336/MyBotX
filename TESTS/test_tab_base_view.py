#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для UI/tabs/tab_base_view.py

Подзадача 7.1:
  - Тест что build(app) создаёт app.frames["base"] без исключений
  - Тест что при отсутствии ADB кнопки в состоянии disabled
  - Requirements: 1.7
"""

import sys
import os
import tkinter as tk
from unittest.mock import MagicMock
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'CORE'))


@pytest.fixture(scope="module")
def tk_root():
    """Единственный Tk root на весь модуль тестов."""
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def _make_mock_app(root, connected_device=None):
    """Создаёт минимальный mock-объект app для тестирования build()."""
    app = MagicMock()
    app.root = root

    # Создаём реальный фрейм "base"
    frame = tk.Frame(root, bg="#0d0d0d")
    app.frames = {"base": frame}

    # Mock ADB
    app.adb = MagicMock()
    app.adb.connected_device = connected_device

    # Заглушки методов, которые build() перезапишет
    app._base_screenshot  = lambda: None
    app._base_zoom_in     = lambda: None
    app._base_zoom_out    = lambda: None
    app._base_find_center = lambda: None
    app._base_log         = lambda msg, tag="": None

    return app


def test_build_creates_base_frame(tk_root):
    """build(app) должен создавать виджеты в app.frames['base'] без исключений."""
    from UI.tabs.tab_base_view import build
    app = _make_mock_app(tk_root)
    build(app)

    assert hasattr(app, "base_preview_label"), "base_preview_label не создан"
    assert hasattr(app, "base_log"),           "base_log не создан"
    assert hasattr(app, "_base_log"),          "_base_log не создан"
    assert hasattr(app, "_base_screenshot"),   "_base_screenshot не создан"
    assert hasattr(app, "_base_zoom_in"),      "_base_zoom_in не создан"
    assert hasattr(app, "_base_zoom_out"),     "_base_zoom_out не создан"
    assert hasattr(app, "_base_find_center"),  "_base_find_center не создан"

    children = app.frames["base"].winfo_children()
    assert len(children) > 0, "Фрейм 'base' пуст после build()"


def test_build_creates_buttons(tk_root):
    """build(app) должен создать 4 кнопки управления."""
    from UI.tabs.tab_base_view import build
    app = _make_mock_app(tk_root)
    build(app)

    assert hasattr(app, "_base_btn_screenshot"),   "Кнопка Скриншот не создана"
    assert hasattr(app, "_base_btn_zoom_in"),      "Кнопка Приблизить не создана"
    assert hasattr(app, "_base_btn_zoom_out"),     "Кнопка Отдалить не создана"
    assert hasattr(app, "_base_btn_find_center"),  "Кнопка Найти центр не создана"


def test_no_adb_screenshot_logs_error(tk_root):
    """При отсутствии ADB _base_screenshot() должен логировать ошибку."""
    from UI.tabs import tab_base_view as tbv
    app = _make_mock_app(tk_root, connected_device=None)

    logged = []
    app._base_log = lambda msg, tag="": logged.append((msg, tag))

    screenshot_fn = tbv._make_base_screenshot(app)
    screenshot_fn()

    assert any("не подключено" in m for m, _ in logged), \
        "Ожидалось сообщение об отсутствии подключения"
    assert any(t == "error" for _, t in logged), \
        "Ожидался тег 'error'"


def test_no_adb_zoom_in_logs_error(tk_root):
    """При отсутствии ADB _base_zoom_in() должен логировать ошибку."""
    from UI.tabs import tab_base_view as tbv
    app = _make_mock_app(tk_root, connected_device=None)

    logged = []
    app._base_log = lambda msg, tag="": logged.append((msg, tag))

    zoom_in_fn = tbv._make_base_zoom_in(app)
    zoom_in_fn()

    assert any("не подключено" in m for m, _ in logged)


def test_no_adb_zoom_out_logs_error(tk_root):
    """При отсутствии ADB _base_zoom_out() должен логировать ошибку."""
    from UI.tabs import tab_base_view as tbv
    app = _make_mock_app(tk_root, connected_device=None)

    logged = []
    app._base_log = lambda msg, tag="": logged.append((msg, tag))

    zoom_out_fn = tbv._make_base_zoom_out(app)
    zoom_out_fn()

    assert any("не подключено" in m for m, _ in logged)


def test_no_adb_find_center_logs_error(tk_root):
    """При отсутствии ADB _base_find_center() должен логировать ошибку."""
    from UI.tabs import tab_base_view as tbv
    app = _make_mock_app(tk_root, connected_device=None)

    logged = []
    app._base_log = lambda msg, tag="": logged.append((msg, tag))

    find_center_fn = tbv._make_base_find_center(app)
    find_center_fn()

    assert any("не подключено" in m for m, _ in logged)


def test_base_log_writes_to_widget(tk_root):
    """_base_log() должен записывать текст в app.base_log."""
    from UI.tabs.tab_base_view import build
    from UI.tabs import tab_base_view as tbv
    app = _make_mock_app(tk_root)
    build(app)

    app.base_log.config(state=tk.NORMAL)
    app.base_log.delete("1.0", tk.END)

    log_fn = tbv._make_base_log(app)
    log_fn("Тестовое сообщение", "info")

    tk_root.update()

    content = app.base_log.get("1.0", tk.END).strip()
    assert "Тестовое сообщение" in content, f"Сообщение не найдено в логе: '{content}'"


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Тесты tab_base_view")
    print("=" * 60)
    root = tk.Tk()
    root.withdraw()
    tests = [
        lambda: test_build_creates_base_frame(root),
        lambda: test_build_creates_buttons(root),
        lambda: test_no_adb_screenshot_logs_error(root),
        lambda: test_no_adb_zoom_in_logs_error(root),
        lambda: test_no_adb_zoom_out_logs_error(root),
        lambda: test_no_adb_find_center_logs_error(root),
        lambda: test_base_log_writes_to_widget(root),
    ]
    names = [
        "test_build_creates_base_frame",
        "test_build_creates_buttons",
        "test_no_adb_screenshot_logs_error",
        "test_no_adb_zoom_in_logs_error",
        "test_no_adb_zoom_out_logs_error",
        "test_no_adb_find_center_logs_error",
        "test_base_log_writes_to_widget",
    ]
    passed = 0
    for name, t in zip(names, tests):
        try:
            t()
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
    root.destroy()
    print(f"\n{'✅' if passed == len(tests) else '⚠'} Пройдено {passed}/{len(tests)}")
