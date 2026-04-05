@echo off
setlocal enabledelayedexpansion
REM Двойной щелчок: рабочая папка часто не корень проекта
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
set "WHEELS_DIR=BOT_APPLICATIONS\wheels"

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
echo 📦 Проверка пакетов Python...
echo ────────────────────────────────────────

echo 🔍 Проверка psutil...
python -c "import psutil; print('   ✅ psutil ' + psutil.__version__)" 2>nul
if errorlevel 1 (
    echo    ❌ psutil — устанавливаем...
    python -m pip install psutil==5.9.6
    python -c "import psutil; print('   ✅ psutil установлен')" 2>nul
    if errorlevel 1 ( echo    ❌ Не удалось установить psutil & pause & exit /b 1 )
)

echo 🔍 Проверка Pillow...
python -c "import PIL; print('   ✅ Pillow ' + PIL.__version__)" 2>nul
if errorlevel 1 (
    echo    ❌ Pillow — устанавливаем...
    python -m pip install Pillow==10.1.0
    python -c "import PIL; print('   ✅ Pillow установлен')" 2>nul
    if errorlevel 1 ( echo    ❌ Не удалось установить Pillow & pause & exit /b 1 )
)

echo 🔍 Проверка numpy...
python -c "import numpy; print('   ✅ numpy ' + numpy.__version__)" 2>nul
if errorlevel 1 (
    echo    ❌ numpy — устанавливаем...
    python -m pip install numpy==1.26.4
    python -c "import numpy; print('   ✅ numpy установлен')" 2>nul
    if errorlevel 1 ( echo    ❌ Не удалось установить numpy & pause & exit /b 1 )
)

echo 🔍 Проверка opencv-python...
python -c "import cv2; print('   ✅ opencv ' + cv2.__version__)" 2>nul
if errorlevel 1 (
    echo    ❌ opencv — устанавливаем...
    python -m pip install opencv-python==4.8.1.78
    python -c "import cv2; print('   ✅ opencv установлен')" 2>nul
    if errorlevel 1 ( echo    ❌ Не удалось установить opencv & pause & exit /b 1 )
)

echo 🔍 Проверка pywin32...
python -c "import win32gui; print('   ✅ pywin32 OK')" 2>nul
if errorlevel 1 (
    echo    ❌ pywin32 — устанавливаем...
    python -m pip install pywin32==306
    python -c "import win32gui; print('   ✅ pywin32 установлен')" 2>nul
    if errorlevel 1 ( echo    ❌ Не удалось установить pywin32 & pause & exit /b 1 )
)

echo ────────────────────────────────────────
echo ✅ Пакеты готовы

if not exist "%~dp0CORE\main.py" (
    echo ❌ Нет CORE\main.py — запускайте из корня проекта MyBotX.
    pause
    exit /b 1
)

cd /d "%~dp0CORE"
echo.
echo ✅ Все проверки пройдены. Запускаем MyBotX...
start "" /min cmd /c "python main.py"
exit
