@echo off
chcp 65001 >nul
title MyBotX 1.0 Launcher
color 0A
cls

echo.
echo ════════════════════════════════════════════════════════
echo     🚀 MyBotX 1.0 Launcher
echo ════════════════════════════════════════════════════════
echo.

set "PYTHON_INSTALLER=BOT_APPLICATIONS\python-3.10.11-amd64.exe"
set "BLUESTACKS_INSTALLER=BOT_APPLICATIONS\BlueStacksInstaller_5.22.130.1019_amd64_native.exe"
set "WHEELS_DIR=BOT_APPLICATIONS\wheels"

REM ══════════════════════════════════════
REM ЭТАП 1: PYTHON
REM ══════════════════════════════════════
echo 🐍 ЭТАП 1: Проверка Python...
python --version >nul 2>&1
if errorlevel 1 goto install_python
echo ✅ Python найден
goto python_ok

:install_python
if not exist "%PYTHON_INSTALLER%" (
    echo ❌ Python не найден и установщик отсутствует!
    echo � Поместите python-3.10.11-amd64.exe в BOT_APPLICATIONS\
    pause
    exit /b 1
)
echo 📦 Установка Python...
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_tcltk=1 Include_pip=1
echo ✅ Python установлен! Перезапустите лаунчер.
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

REM ══════════════════════════════════════
REM ЭТАП 2: ADB
REM ══════════════════════════════════════
echo.
echo � ЭТАП 2: Проверка ADB...
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

REM ══════════════════════════════════════
REM ЭТАП 3: BLUESTACKS
REM ══════════════════════════════════════
echo.
echo � ЭТАП 3: Проверка BlueStacks...

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

REM ══════════════════════════════════════
REM ЭТАП 4: PYTHON ПАКЕТЫ
REM ══════════════════════════════════════
echo.
echo � ЭТАП 4: Проверка пакетов...
python -c "import psutil" >nul 2>&1
if not errorlevel 1 (
    echo ✅ Пакеты установлены
    goto packages_ok
)
if exist "%WHEELS_DIR%" (
    python -m pip install --find-links "%WHEELS_DIR%" --no-index psutil >nul 2>&1
) else (
    python -m pip install psutil >nul 2>&1
)
echo ✅ Пакеты установлены

:packages_ok

REM ══════════════════════════════════════
REM ЭТАП 5: ЗАПУСК
REM ══════════════════════════════════════
echo.
echo ════════════════════════════════════════════════════════
echo ✅ Все проверки пройдены! Запуск MyBotX...
echo ════════════════════════════════════════════════════════
echo.

cd /d "%~dp0CORE"
start /min python main.py

echo ✅ MyBotX запущен!
echo.

REM Свернуть окно командной строки
powershell -window minimized -command "Start-Sleep 1"
exit
