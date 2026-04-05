# 🤖 MyBotX

Автоматизация Clash of Clans через BlueStacks 5 с GUI управлением на Python (Windows).

## ⚡ Быстрый старт

1. Запустите `MyBotX_1.0.bat` (старый ярлык `MyBotX_1.0_launcher.bat` тоже работает)
2. Вкладка **ПРОВЕРКА** → Проверить всё
3. Вкладка **ОСНОВНОЕ** → СТАРТ

## 📋 Требования

- Windows 10/11
- Python 3.10+
- BlueStacks 5
- psutil

## 🏗️ Актуальная структура проекта

```
MyBotX/
├── MyBotX_1.0.bat                # Главный запуск (проверки + python main.py)
├── MyBotX_1.0_launcher.bat       # Совместимость: вызывает MyBotX_1.0.bat
├── GIT_COMMANDS.md               # Шпаргалка по Git
├── README.md                     # Описание проекта
├── CONFIG/
│   ├── config.json               # Конфигурация проекта
│   └── config_comments.md        # Комментарии по настройкам
├── CORE/                         # Исходный код
│   ├── main.py                   # GUI интерфейс (tkinter, 3 вкладки)
│   ├── advanced_adb_manager.py   # Менеджер ADB подключений
│   ├── bluestacks_manager.py     # Менеджер BlueStacks
│   ├── game_launcher.py          # Запуск игр
│   ├── dependency_checker.py     # Проверка зависимостей
│   ├── requirements.txt          # Список Python пакетов
│   └── processes/                # Логика разбита по модулям
│       ├── ADB/                  # ADB подключение
│       │   ├── adb_01_init.py        # Инициализация ADB
│       │   ├── adb_02_check_port.py  # Проверка порта через socket
│       │   ├── adb_03_find_port.py   # Поиск порта 5555-5559
│       │   └── adb_04_connect.py     # Подключение к устройству
│       ├── BLUESTACKS/           # Управление BlueStacks
│       │   ├── bs_01_init.py         # Инициализация + кэш пути
│       │   ├── bs_02_search.py       # Поиск через реестр и пути
│       │   ├── bs_03_status.py       # Проверка установки/запуска
│       │   └── bs_04_control.py      # Запуск/остановка/перезапуск
│       ├── GAME/                 # Запуск игры
│       │   ├── game_01_init.py       # Инициализация + список игр
│       │   ├── game_02_check_app.py  # Проверка установки игры
│       │   ├── game_03_play_market.py# Открытие Play Market
│       │   ├── game_04_launch_direct.py # Запуск через activity
│       │   ├── game_05_launch_intent.py # Запуск через LAUNCHER INTENT
│       │   ├── game_06_launch_monkey.py # Запуск через monkey
│       │   └── game_07_auto_launch.py   # Автозапуск (все способы)
│       └── DEPENDENCIES/         # Управление зависимостями
│           ├── dep_01_init.py        # Инициализация
│           ├── dep_02_parse.py       # Парсинг requirements.txt
│           ├── dep_03_check.py       # Проверка пакетов через pip
│           └── dep_04_install.py     # Установка пакетов
│
├── BOT_APPLICATIONS/             # Platform-tools и внешние артефакты
└── TESTS/                        # Тесты всех модулей
    ├── run_all_tests.bat         # Запуск всех тестов с логами
    ├── clear_test_logs.bat       # Очистка логов
    ├── test_game_launcher.py     # Тест запуска игр
    ├── test_advanced_adb_manager.py # Тест ADB
    ├── test_bluestacks_manager.py   # Тест BlueStacks
    ├── test_dependency_checker.py   # Тест зависимостей
    └── test_main_gui.py          # Тест GUI
```

## 🎮 Поддерживаемые игры

- Clash of Clans

## 🔧 Зависимости

Используются пакеты из `CORE/requirements.txt`:
- `psutil==5.9.6`
- `Pillow==10.1.0`
- `opencv-python==4.8.1.78`
- `numpy==1.26.4`

## 📄 Лицензия

MIT
