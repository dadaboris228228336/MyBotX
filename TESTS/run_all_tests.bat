@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Устанавливаем UTF-8 для Python
set PYTHONIOENCODING=utf-8

:: Настройка цветов и переменных
set "LOG_DIR=TESTS\logs"
set "TIMESTAMP=%date:~-4,4%-%date:~-10,2%-%date:~-7,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%"
set "TIMESTAMP=!TIMESTAMP: =0!"
set "MAIN_LOG=%LOG_DIR%\test_results_!TIMESTAMP!.log"

:: Создаем папку для логов
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Заголовок
echo.
echo ===============================================================================
echo 🧪 ЗАПУСК ВСЕХ ТЕСТОВ MyBotX v3.0.0
echo ===============================================================================
echo ⏰ Время начала: %date% %time%
echo 📁 Логи сохраняются в: %MAIN_LOG%
echo.

:: Записываем заголовок в лог
echo =============================================================================== > "%MAIN_LOG%"
echo 🧪 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ MyBotX v3.0.0 >> "%MAIN_LOG%"
echo =============================================================================== >> "%MAIN_LOG%"
echo ⏰ Время начала: %date% %time% >> "%MAIN_LOG%"
echo. >> "%MAIN_LOG%"

:: Список тестов
set "TESTS[0]=test_game_launcher.py"
set "TESTS[1]=test_advanced_adb_manager.py"
set "TESTS[2]=test_bluestacks_manager.py"
set "TESTS[3]=test_dependency_checker.py"
set "TESTS[4]=test_main_gui.py"

set "TEST_NAMES[0]=🎮 GameLauncher"
set "TEST_NAMES[1]=🤖 AdvancedADBManager"
set "TEST_NAMES[2]=🔧 BlueStacksManager"
set "TEST_NAMES[3]=📦 DependencyChecker"
set "TEST_NAMES[4]=🖥️ Main GUI"

:: Счетчики
set "TOTAL_TESTS=5"
set "PASSED_TESTS=0"
set "FAILED_TESTS=0"

:: Переходим в корневую папку проекта
cd /d "%~dp0\.."

:: Запуск тестов
for /L %%i in (0,1,4) do (
    set "CURRENT_TEST=!TESTS[%%i]!"
    set "CURRENT_NAME=!TEST_NAMES[%%i]!"
    
    echo.
    echo ───────────────────────────────────────────────────────────────────────────────
    echo 🚀 ЗАПУСК ТЕСТА %%i/5: !CURRENT_NAME!
    echo ───────────────────────────────────────────────────────────────────────────────
    echo 📄 Файл: !CURRENT_TEST!
    echo ⏰ Время: !time!
    echo.
    
    :: Записываем в лог
    echo. >> "%MAIN_LOG%"
    echo ─────────────────────────────────────────────────────────────────────────────── >> "%MAIN_LOG%"
    echo 🚀 ТЕСТ %%i/5: !CURRENT_NAME! >> "%MAIN_LOG%"
    echo ─────────────────────────────────────────────────────────────────────────────── >> "%MAIN_LOG%"
    echo 📄 Файл: !CURRENT_TEST! >> "%MAIN_LOG%"
    echo ⏰ Время: !time! >> "%MAIN_LOG%"
    echo. >> "%MAIN_LOG%"
    
    :: Запускаем тест и сохраняем результат в отдельный временный файл
    set "TEMP_LOG=%LOG_DIR%\temp_test_%%i.log"
    python -X utf8 "TESTS\!CURRENT_TEST!" > "!TEMP_LOG!" 2>&1
    set "EXIT_CODE=!ERRORLEVEL!"
    
    :: Добавляем результат в основной лог
    type "!TEMP_LOG!" >> "%MAIN_LOG%"
    del "!TEMP_LOG!" >nul 2>&1
    
    :: Проверяем результат
    if !EXIT_CODE! equ 0 (
        echo ✅ ТЕСТ ПРОЙДЕН: !CURRENT_NAME!
        echo ✅ ТЕСТ ПРОЙДЕН: !CURRENT_NAME! >> "%MAIN_LOG%"
        set /a PASSED_TESTS+=1
    ) else (
        echo ❌ ТЕСТ НЕ ПРОЙДЕН: !CURRENT_NAME! ^(Код ошибки: !EXIT_CODE!^)
        echo ❌ ТЕСТ НЕ ПРОЙДЕН: !CURRENT_NAME! ^(Код ошибки: !EXIT_CODE!^) >> "%MAIN_LOG%"
        set /a FAILED_TESTS+=1
    )
    
    :: Небольшая пауза между тестами
    timeout /t 1 /nobreak >nul
)

:: Итоговые результаты
echo.
echo ===============================================================================
echo 📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ
echo ===============================================================================
echo 🎯 Всего тестов: %TOTAL_TESTS%
echo ✅ Пройдено: %PASSED_TESTS%
echo ❌ Не пройдено: %FAILED_TESTS%
echo ⏰ Время завершения: %date% %time%
echo 📁 Подробные логи: %MAIN_LOG%

:: Записываем итоги в лог
echo. >> "%MAIN_LOG%"
echo =============================================================================== >> "%MAIN_LOG%"
echo 📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ >> "%MAIN_LOG%"
echo =============================================================================== >> "%MAIN_LOG%"
echo 🎯 Всего тестов: %TOTAL_TESTS% >> "%MAIN_LOG%"
echo ✅ Пройдено: %PASSED_TESTS% >> "%MAIN_LOG%"
echo ❌ Не пройдено: %FAILED_TESTS% >> "%MAIN_LOG%"
echo ⏰ Время завершения: %date% %time% >> "%MAIN_LOG%"
echo. >> "%MAIN_LOG%"

:: Определяем общий результат
if %FAILED_TESTS% equ 0 (
    echo.
    echo 🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!
    echo 🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! >> "%MAIN_LOG%"
    echo ✅ MyBotX v3.0.0 готов к работе!
    echo ✅ MyBotX v3.0.0 готов к работе! >> "%MAIN_LOG%"
    set "FINAL_EXIT_CODE=0"
) else (
    echo.
    echo ⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!
    echo ⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ! >> "%MAIN_LOG%"
    echo 🔍 Проверьте логи для получения подробной информации
    echo 🔍 Проверьте логи для получения подробной информации >> "%MAIN_LOG%"
    set "FINAL_EXIT_CODE=1"
)

echo.
echo ===============================================================================
echo 📋 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ
echo ===============================================================================
echo 📁 Папка с логами: %LOG_DIR%
echo 📄 Главный лог: %MAIN_LOG%
echo 🔧 Для просмотра логов: notepad "%MAIN_LOG%"
echo.

:: Предлагаем открыть лог
echo 📖 Хотите открыть лог-файл? (y/n):
set /p "OPEN_LOG="
if /i "!OPEN_LOG!"=="y" (
    start notepad "%MAIN_LOG%"
)

echo.
echo 🏁 Тестирование завершено!
echo.
pause

exit /b %FINAL_EXIT_CODE%