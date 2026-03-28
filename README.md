# 🤖 MyBotX

Автоматизация Clash of Clans через BlueStacks 5 с GUI управлением на Python.

## ⚡ Быстрый старт

1. Запустите `MyBotX_1.0_launcher.bat`
2. Вкладка **ПРОВЕРКА** → Проверить всё
3. Вкладка **ОСНОВНОЕ** → СТАРТ

## 📋 Требования

- Windows 10/11
- Python 3.10+
- BlueStacks 5
- psutil

## 🏗️ Структура

```
MyBotX/
├── CORE/
│   ├── main.py                  # GUI (tkinter)
│   ├── bluestacks_manager.py    # Управление BlueStacks
│   ├── advanced_adb_manager.py  # ADB подключение
│   ├── game_launcher.py         # Запуск игр
│   ├── dependency_checker.py    # Проверка зависимостей
│   └── processes/               # Вся логика (19 файлов)
├── CONFIG/
│   └── config.json              # Конфигурация
├── TESTS/                       # Тесты всех модулей
└── MyBotX_1.0_launcher.bat      # Лаунчер
```

## 🎮 Поддерживаемые игры

- Clash of Clans

## 🔧 Установка зависимостей

```bash
pip install psutil
```

## 📄 Лицензия

MIT
