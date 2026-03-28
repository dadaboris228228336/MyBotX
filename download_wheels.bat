@echo off
chcp 65001 >nul
title Скачивание Python пакетов
color 0A

echo.
echo ════════════════════════════════════════════════════════
echo     📦 Скачивание Python пакетов для MyBotX
echo ════════════════════════════════════════════════════════
echo.

REM Create wheels directory
if not exist "BOT_APPLICATIONS\wheels" mkdir "BOT_APPLICATIONS\wheels"

echo 🔧 Скачивание всех необходимых пакетов...
echo.

REM Download all packages with dependencies
pip download requests==2.31.0 psutil==5.9.6 Pillow==10.1.0 autopep8==2.0.4 python-dotenv==1.0.0 --dest BOT_APPLICATIONS\wheels\

if errorlevel 1 (
    echo ❌ Ошибка при скачивании пакетов
    pause
    exit /b 1
) else (
    echo ✅ Все пакеты скачаны успешно!
)

echo.
echo 📊 Содержимое папки wheels:
dir BOT_APPLICATIONS\wheels\ /b

echo.
echo ✅ Готово! Теперь скачайте:
echo 1. Python 3.10.11: https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
echo 2. BlueStacks 5.22.130.1020: https://cdn3.bluestacks.com/downloads/windows/nxt/5.22.130.1020/x64/BlueStacksInstaller_5.22.130.1020_amd64_native.exe
echo.
echo Поместите их в папку BOT_APPLICATIONS\
echo.
pause