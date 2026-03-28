@echo off
chcp 65001 >nul

echo.
echo 🗑️ ОЧИСТКА ЛОГОВ ТЕСТИРОВАНИЯ
echo ===============================================================================

if exist "TESTS\logs\*.*" (
    echo 📁 Найдены файлы логов в папке TESTS\logs\
    echo.
    dir "TESTS\logs\" /b
    echo.
    echo ❓ Удалить все лог-файлы? (y/n):
    set /p "CONFIRM="
    
    if /i "!CONFIRM!"=="y" (
        del /q "TESTS\logs\*.*"
        echo ✅ Все лог-файлы удалены!
    ) else (
        echo ℹ️ Очистка отменена
    )
) else (
    echo ℹ️ Лог-файлы не найдены
)

echo.
pause