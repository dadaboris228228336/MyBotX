@echo off
chcp 65001 >nul
title MyBotX 1.0 Портативный Лаунчер
color 0A

cls

echo.
echo ════════════════════════════════════════════════════════
echo     🚀 MyBotX 1.0 Портативный Лаунчер
echo ════════════════════════════════════════════════════════
echo     📦 Автономная установка всех компонентов
echo ════════════════════════════════════════════════════════
echo.

REM Variables
set "PYTHON_INSTALLER=BOT_APPLICATIONS\python-3.10.11-amd64.exe"
set "BLUESTACKS_INSTALLER=BOT_APPLICATIONS\BlueStacksInstaller_5.22.130.1019_amd64_native.exe"
set "WHEELS_DIR=BOT_APPLICATIONS\wheels"

REM ═══════════════════════════════════════════════════════════════════════════════
REM ЭТАП 1: ПРОВЕРКА И УСТАНОВКА PYTHON
REM ═══════════════════════════════════════════════════════════════════════════════

echo 🐍 ЭТАП 1: Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден в системе
    
    if exist "%PYTHON_INSTALLER%" (
        echo 📦 Найден локальный установщик Python
        echo 🔧 Запуск автоматической установки Python...
        echo.
        echo [████████████████████████████████████████████████] 0%%
        
        REM Install Python silently with all features
        "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_launcher=1 Include_tcltk=1 Include_pip=1
        
        echo [████████████████████████████████████████████████] 100%%
        echo ✅ Python установлен успешно!
        
        REM Refresh PATH
        call refreshenv >nul 2>&1
        
        REM Verify installation
        python --version >nul 2>&1
        if errorlevel 1 (
            echo ⚠️ Требуется перезапуск командной строки
            echo 💡 Закройте это окно и запустите лаунчер заново
            pause
            exit /b 1
        )
    ) else (
        echo ❌ Локальный установщик Python не найден!
        echo 📁 Ожидается: %PYTHON_INSTALLER%
        echo 💡 Поместите python-3.10.11-amd64.exe в папку BOT_APPLICATIONS\
        pause
        exit /b 1
    )
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python найден: %PYTHON_VERSION%
)

REM Check tkinter
echo 🔍 Проверка tkinter...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ❌ tkinter недоступен!
    echo 💡 Переустановите Python с полным набором компонентов
    pause
    exit /b 1
) else (
    echo ✅ tkinter доступен
)

REM ═══════════════════════════════════════════════════════════════════════════════
REM ЭТАП 1.5: РАСПАКОВКА ADB (platform-tools)
REM ═══════════════════════════════════════════════════════════════════════════════

echo.
echo 🔧 ЭТАП 1.5: Проверка ADB...

if exist "BOT_APPLICATIONS\platform-tools\adb.exe" (
    echo ✅ ADB найден локально
) else (
    if exist "BOT_APPLICATIONS\platform-tools.zip" (
        echo 📦 Распаковка platform-tools...
        powershell -Command "Expand-Archive -Path 'BOT_APPLICATIONS\platform-tools.zip' -DestinationPath 'BOT_APPLICATIONS' -Force" >nul 2>&1
        if exist "BOT_APPLICATIONS\platform-tools\adb.exe" (
            echo ✅ ADB распакован успешно
        ) else (
            echo ⚠️ Не удалось распаковать, используем системный ADB
        )
    ) else (
        REM ═══════════════════════════════════════════════════════════════════════════════
REM ЭТАП 2: ПРОВЕРКА И УСТАНОВКА BLUESTACKS
REM ═══════════════════════════════════════════════════════════════════════════════

echo.
echo 📱 ЭТАП 2: Проверка BlueStacks...

REM Check if BlueStacks is already installed (standard paths)
if exist "C:\Program Files\BlueStacks_nxt\HD-Player.exe" (
    echo ✅ BlueStacks 5 найден
    goto bluestacks_found
)
if exist "C:\Program Files (x86)\BlueStacks_nxt\HD-Player.exe" (
    echo ✅ BlueStacks 5 найден
    goto bluestacks_found
)
if exist "C:\Program Files\BlueStacks\HD-Player.exe" (
    echo ✅ BlueStacks 4 найден
    goto bluestacks_found
)
if exist "C:\Program Files (x86)\BlueStacks\HD-Player.exe" (
    echo ✅ BlueStacks 4 найден
    goto bluestacks_found
)

REM Check registry
echo 🔍 Поиск BlueStacks в реестре...
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\BlueStacks_nxt" /v "InstallDir" 2^>nul') do (
    if exist "%%b\HD-Player.exe" (
        echo ✅ BlueStacks найден через реестр: %%b
        goto bluestacks_found
    )
)
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\WOW6432Node\BlueStacks_nxt" /v "InstallDir" 2^>nul') do (
    if exist "%%b\HD-Player.exe" (
        echo ✅ BlueStacks найден через реестр: %%b
        goto bluestacks_found
    )
)

echo ❌ BlueStacks не найден в системе

if exist "%BLUESTACKS_INSTALLER%" (
    echo 📦 Найден локальный установщик BlueStacks
    echo 🔧 Запуск установки BlueStacks...
    echo ⚠️ Это может занять несколько минут...
    echo.
    echo [████████████████████████████████████████████████] 0%%
    
    REM Install BlueStacks silently
    start /wait "" "%BLUESTACKS_INSTALLER%" -s
    
    echo [████████████████████████████████████████████████] 100%%
    echo ✅ BlueStacks установлен успешно!
) else (
    echo ❌ Локальный установщик BlueStacks не найден!
    echo 📁 Ожидается: %BLUESTACKS_INSTALLER%
    echo 💡 Поместите BlueStacks установщик в папку BOT_APPLICATIONS\
    pause
    exit /b 1
)

:bluestacks_found

REM ═══════════════════════════════════════════════════════════════════════════════
REM ЭТАП 3: УСТАНОВКА PYTHON ПАКЕТОВ
REM ═══════════════════════════════════════════════════════════════════════════════

echo.
echo 📦 ЭТАП 3: Установка Python пакетов...

REM Check if psutil already installed
python -c "import psutil" >nul 2>&1
if not errorlevel 1 (
    echo ✅ Пакеты уже установлены
    goto packages_done
)

if exist "%WHEELS_DIR%" (
    echo 📁 Установка из локальных wheel файлов...
    python -m pip install --find-links "%WHEELS_DIR%" --no-index psutil >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ Не удалось из wheels, пробуем онлайн...
        python -m pip install psutil >nul 2>&1
    )
) else (
    echo 🌐 Установка онлайн...
    python -m pip install psutil >nul 2>&1
)

python -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo ❌ Не удалось установить psutil!
    pause
    exit /b 1
)
echo ✅ Пакеты установлены успешно!

:packages_done

REM ═══════════════════════════════════════════════════════════════════════════════
REM ЭТАП 4: ЗАПУСК MYBOTX
REM ═══════════════════════════════════════════════════════════════════════════════

echo.
echo ✅ ВСЕ КОМПОНЕНТЫ УСТАНОВЛЕНЫ УСПЕШНО!
echo ════════════════════════════════════════════════════════
echo 🎉 MyBotX готов к запуску!
echo ════════════════════════════════════════════════════════
echo 🚀 Запуск MyBotX...
echo 📱 Приложение будет свернуто в системный трей...
echo.

REM Go to CORE folder
cd /d "%~dp0CORE"

REM Launch main.py minimized
start /min python main.py

echo ✅ MyBotX запущен в фоновом режиме
echo 💡 Найдите иконку в системном трее для управления
echo.

REM Exit launcher immediately (MyBotX runs in background)
exit