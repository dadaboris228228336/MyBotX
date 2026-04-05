@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
chcp 65001 >nul
title MyBotX 1.0
color 0A
cls

echo.
echo ════════════════════════════════════════════════════════
echo     MyBotX 1.0
echo ════════════════════════════════════════════════════════
echo.

set "PYTHON_INSTALLER=BOT_APPLICATIONS\python-3.10.11-amd64.exe"
set "BLUESTACKS_INSTALLER=BOT_APPLICATIONS\BlueStacksInstaller_5.22.130.1019_amd64_native.exe"

echo 🔄 Закрываем предыдущие экземпляры MyBotX...
taskkill /IM "python.exe" /F >nul 2>&1
taskkill /IM "pythonw.exe" /F >nul 2>&1
timeout /t 1 /nobreak >nul

echo 🐍 Проверка Python...
python --version >nul 2>&1
if errorlevel 1 goto install_python
echo ✅ Python найден
goto python_ok

:install_python
if not exist "%PYTHON_INSTALLER%" (
    echo ❌ Python не найден и установщик отсутствует!
    echo 💡 Поместите python-3.10.11-amd64.exe в BOT_APPLICATIONS\
    pause
    exit /b 1
)
echo 📦 Установка Python...
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_tcltk=1 Include_pip=1
echo ✅ Python установлен! Перезапустите этот файл.
pause
exit /b 0

:python_ok
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ❌ tkinter недоступен!
    pause
    exit /b 1
)
echo ✅ tkinter доступен

echo.
echo 🔧 Проверка ADB...
if exist "BOT_APPLICATIONS\platform-tools\adb.exe" (
    echo ✅ ADB найден локально
    goto adb_ok
)
if exist "BOT_APPLICATIONS\platform-tools.zip" (
    echo 📦 Распаковка platform-tools...
    powershell -Command "Expand-Archive -Path 'BOT_APPLICATIONS\platform-tools.zip' -DestinationPath 'BOT_APPLICATIONS' -Force" >nul 2>&1
    echo ✅ ADB распакован
    goto adb_ok
)
echo ⚠️ Используем системный ADB

:adb_ok

echo.
echo 📱 Проверка BlueStacks...
if exist "C:\Program Files\BlueStacks_nxt\HD-Player.exe" goto bluestacks_ok
if exist "C:\Program Files (x86)\BlueStacks_nxt\HD-Player.exe" goto bluestacks_ok
if exist "C:\Program Files\BlueStacks\HD-Player.exe" goto bluestacks_ok
if exist "C:\Program Files (x86)\BlueStacks\HD-Player.exe" goto bluestacks_ok

for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\BlueStacks_nxt" /v "InstallDir" 2^>nul') do (
    if exist "%%b\HD-Player.exe" goto bluestacks_ok
)
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\WOW6432Node\BlueStacks_nxt" /v "InstallDir" 2^>nul') do (
    if exist "%%b\HD-Player.exe" goto bluestacks_ok
)

echo ❌ BlueStacks не найден
if not exist "%BLUESTACKS_INSTALLER%" (
    echo 💡 Поместите установщик BlueStacks в BOT_APPLICATIONS\
    pause
    exit /b 1
)
echo 📦 Установка BlueStacks...
start /wait "" "%BLUESTACKS_INSTALLER%" -s
echo ✅ BlueStacks установлен!

:bluestacks_ok
echo ✅ BlueStacks найден

echo.
echo 📦 Установка зависимостей из requirements.txt...
echo ────────────────────────────────────────
python -m pip install -r "%~dp0CORE\requirements.txt"
if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей!
    pause
    exit /b 1
)
echo ────────────────────────────────────────
echo ✅ Все зависимости установлены

if not exist "%~dp0CORE\main.py" (
    echo ❌ Нет CORE\main.py — запускайте из корня проекта MyBotX.
    pause
    exit /b 1
)

cd /d "%~dp0CORE"
echo.
echo ✅ Все проверки пройдены. Запускаем MyBotX...
python main.py
if errorlevel 1 (
    echo.
    echo ❌ Ошибка запуска — смотри текст выше.
    pause
    exit /b 1
)
exit /b 0
