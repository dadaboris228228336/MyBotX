# CONFIG/config.json - пояснения

## application
- `name`, `version`, `description`, `author`: метаданные приложения.
- `python_version`, `platform`: целевая среда выполнения.

## technical_config.adb_settings
- `ports`: список ADB-портов BlueStacks для перебора.
- `timeout`: таймаут проверки порта (сек).
- `max_wait`: максимальное ожидание подключения (сек).

## gui_settings
- `window_size`, `theme`: базовые параметры интерфейса.
- `log_colors`: цвета статусов в логах GUI.

## bluestacks
- `path`: путь к `HD-Player.exe`.
- `cached_at`, `auto_detected`: служебные поля кэширования.

## bot_settings
- `threshold`: порог совпадения шаблонов OpenCV (0..1).
- `action_delay`: задержка между действиями бота (сек).

## usage
- Подсказки по быстрому запуску через лаунчер и GUI.
