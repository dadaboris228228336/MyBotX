@echo off
cd /d "%~dp0"
chcp 65001 >nul
title BlueStacks Monitor
color 0B

echo.
echo ════════════════════════════════════════
echo     BlueStacks Crash Monitor
echo ════════════════════════════════════════
echo.
echo Лог пишется в: %~dp0bs_monitor.log
echo Для остановки нажмите Ctrl+C
echo.

REM Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден в PATH!
    echo Запустите сначала MyBotX_1.0.bat для установки Python.
    pause
    exit /b 1
)

REM Устанавливаем psutil если нет
python -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo Устанавливаем psutil...
    python -m pip install psutil --quiet
)

REM Запускаем монитор
python "%~dp0bs_monitor.py"

REM Если скрипт завершился — держим окно
echo.
echo Монитор завершил работу.
pause
