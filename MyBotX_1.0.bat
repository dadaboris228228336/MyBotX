@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
chcp 65001 >nul
title MyBotX 1.0
color 0A
cls

echo.
echo ════════════════════════════════════════════════════════
echo     MyBotX 1.0  —  Автоматическая установка
echo ════════════════════════════════════════════════════════
echo.

set "ROOT_DIR=%~dp0"
set "BOT_DIR=%ROOT_DIR%BOT_APPLICATIONS"
set "TOOLS_DIR=%BOT_DIR%\platform-tools"

REM ── Версии и URL ─────────────────────────────────────────
REM Python 3.10.11 — зафиксирована, код использует синтаксис 3.10+
set "PYTHON_VER=3.10.11"
set "PYTHON_URL=https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
set "PYTHON_INSTALLER=%BOT_DIR%\python-3.10.11-amd64.exe"

REM BlueStacks 5 (latest) — любая версия BS5 совместима с ботом
REM Бот использует только: HD-Player.exe, реестр BlueStacks_nxt, ADB порты 5555-5559
set "BLUESTACKS_URL=https://cdn3.bluestacks.com/public/BlueStacksInstaller_5.exe"
set "BLUESTACKS_INSTALLER=%BOT_DIR%\BlueStacksInstaller_5.exe"

REM ADB platform-tools (latest) — Google гарантирует обратную совместимость
REM Используем только: adb connect, adb shell, adb exec-out screencap
set "ADB_URL=https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
set "ADB_ZIP=%BOT_DIR%\platform-tools.zip"

REM ── Создаём папку BOT_APPLICATIONS если нет ──────────────
if not exist "%BOT_DIR%" mkdir "%BOT_DIR%"

REM ── Закрываем предыдущие экземпляры ─────────────────────
echo 🔄 Закрываем предыдущие экземпляры MyBotX...
taskkill /IM "python.exe" /F >nul 2>&1
taskkill /IM "pythonw.exe" /F >nul 2>&1
timeout /t 1 /nobreak >nul

REM ══════════════════════════════════════════════════════════
REM  ШАГ 1: Python 3.10.11
REM ══════════════════════════════════════════════════════════
echo.
echo 🐍 [1/4] Проверка Python %PYTHON_VER%...

python --version >nul 2>&1
if not errorlevel 1 (
    REM Python найден — проверяем что версия >= 3.10
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
    for /f "tokens=1,2 delims=." %%a in ("!PY_VER!") do (
        set "PY_MAJOR=%%a"
        set "PY_MINOR=%%b"
    )
    if !PY_MAJOR! GEQ 3 if !PY_MINOR! GEQ 10 goto python_ok
    echo ⚠️  Найден Python !PY_VER!, нужен 3.10+. Устанавливаем 3.10.11...
)

REM Python не найден или версия старая — скачиваем 3.10.11
if not exist "%PYTHON_INSTALLER%" (
    echo 📥 Скачиваем Python %PYTHON_VER% ^(~28 MB^)...
    powershell -Command "& { $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' }"
    if not exist "%PYTHON_INSTALLER%" (
        echo ❌ Не удалось скачать Python. Проверьте интернет-соединение.
        pause
        exit /b 1
    )
    echo ✅ Python %PYTHON_VER% скачан
)

echo 📦 Устанавливаем Python %PYTHON_VER%...
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_tcltk=1 Include_pip=1 Include_launcher=1
if errorlevel 1 (
    echo ❌ Ошибка установки Python!
    pause
    exit /b 1
)
echo ✅ Python %PYTHON_VER% установлен!

REM Обновляем PATH из реестра в текущей сессии
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v "Path" 2^>nul') do set "SYS_PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v "Path" 2^>nul') do set "USR_PATH=%%b"
set "PATH=%SYS_PATH%;%USR_PATH%;%PATH%"

python --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Перезапускаем скрипт с обновлённым PATH...
    start "" cmd /c ""%~f0""
    exit /b 0
)

:python_ok
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo ✅ %%v

python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ❌ tkinter недоступен! Переустановите Python с галочкой tcl/tk.
    pause
    exit /b 1
)
echo ✅ tkinter доступен

REM ══════════════════════════════════════════════════════════
REM  ШАГ 2: ADB platform-tools
REM ══════════════════════════════════════════════════════════
echo.
echo 🔧 [2/4] Проверка ADB...

if exist "%TOOLS_DIR%\adb.exe" (
    for /f "tokens=5" %%v in ('"%TOOLS_DIR%\adb.exe" version 2^>^&1 ^| findstr "Version"') do echo ✅ ADB %%v
    goto adb_ok
)

where adb >nul 2>&1
if not errorlevel 1 (
    echo ✅ Используем системный ADB
    goto adb_ok
)

if not exist "%ADB_ZIP%" (
    echo 📥 Скачиваем Android platform-tools ^(~10 MB^)...
    powershell -Command "& { $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri '%ADB_URL%' -OutFile '%ADB_ZIP%' }"
    if not exist "%ADB_ZIP%" (
        echo ❌ Не удалось скачать ADB. Проверьте интернет-соединение.
        pause
        exit /b 1
    )
)

echo 📦 Распаковываем platform-tools...
powershell -Command "Expand-Archive -Path '%ADB_ZIP%' -DestinationPath '%BOT_DIR%' -Force" >nul 2>&1
if not exist "%TOOLS_DIR%\adb.exe" (
    echo ❌ Не удалось распаковать ADB!
    pause
    exit /b 1
)
echo ✅ ADB установлен

:adb_ok

REM ══════════════════════════════════════════════════════════
REM  ШАГ 3: BlueStacks 5
REM ══════════════════════════════════════════════════════════
echo.
echo 📱 [3/4] Проверка BlueStacks 5...

REM Проверяем стандартные пути
if exist "C:\Program Files\BlueStacks_nxt\HD-Player.exe" goto bluestacks_ok
if exist "C:\Program Files (x86)\BlueStacks_nxt\HD-Player.exe" goto bluestacks_ok
if exist "C:\Program Files\BlueStacks\HD-Player.exe" goto bluestacks_ok
if exist "C:\Program Files (x86)\BlueStacks\HD-Player.exe" goto bluestacks_ok

REM Проверяем реестр
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\BlueStacks_nxt" /v "InstallDir" 2^>nul') do (
    if exist "%%b\HD-Player.exe" goto bluestacks_ok
)
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\WOW6432Node\BlueStacks_nxt" /v "InstallDir" 2^>nul') do (
    if exist "%%b\HD-Player.exe" goto bluestacks_ok
)

REM BlueStacks не найден — ищем локальный установщик
echo ❌ BlueStacks 5 не найден
for %%f in ("%BOT_DIR%\BlueStacks*.exe") do (
    set "BLUESTACKS_INSTALLER=%%f"
    goto bs_install
)

REM Скачиваем онлайн-установщик (~2 MB, сам докачивает ~1.5 GB при установке)
echo 📥 Скачиваем установщик BlueStacks 5 ^(~2 MB, затем ~1.5 GB при установке^)...
powershell -Command "& { $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri '%BLUESTACKS_URL%' -OutFile '%BLUESTACKS_INSTALLER%' }"
if not exist "%BLUESTACKS_INSTALLER%" (
    echo ❌ Не удалось скачать BlueStacks. Проверьте интернет-соединение.
    pause
    exit /b 1
)

:bs_install
echo 📦 Устанавливаем BlueStacks 5 ^(это займёт несколько минут^)...
start /wait "" "%BLUESTACKS_INSTALLER%" -s
echo ✅ BlueStacks 5 установлен!

:bluestacks_ok
REM Показываем версию из реестра
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\BlueStacks_nxt" /v "Version" 2^>nul') do echo ✅ BlueStacks %%b
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\WOW6432Node\BlueStacks_nxt" /v "Version" 2^>nul') do echo ✅ BlueStacks %%b

REM ══════════════════════════════════════════════════════════
REM  ШАГ 4: Python пакеты
REM ══════════════════════════════════════════════════════════
echo.
echo 📦 [4/4] Проверка Python пакетов...
echo     psutil==5.9.6  Pillow==10.1.0  opencv-python==4.8.1.78
echo     numpy==1.26.4  pywin32==306    pyautogui==0.9.54

python "%ROOT_DIR%CORE\check_requirements.py" >nul 2>&1
if not errorlevel 1 (
    echo ✅ Все пакеты уже установлены
    goto packages_ok
)

echo ⚙️  Устанавливаем пакеты...
python -m pip install --upgrade pip --quiet
python -m pip install -r "%ROOT_DIR%CORE\requirements.txt"
if errorlevel 1 (
    echo ❌ Ошибка установки пакетов!
    pause
    exit /b 1
)

REM pywin32 требует post-install шаг
python -c "import win32gui" >nul 2>&1
if errorlevel 1 (
    echo ⚙️  Настройка pywin32...
    python -m pywin32_postinstall -install >nul 2>&1
)

echo ✅ Все пакеты установлены

:packages_ok

REM ══════════════════════════════════════════════════════════
REM  ЗАПУСК
REM ══════════════════════════════════════════════════════════
echo.
echo ════════════════════════════════════════════════════════
echo  ✅ Все проверки пройдены. Запускаем MyBotX...
echo ════════════════════════════════════════════════════════
echo.

if not exist "%ROOT_DIR%CORE\main.py" (
    echo ❌ Файл CORE\main.py не найден!
    pause
    exit /b 1
)

cd /d "%ROOT_DIR%CORE"
start "" python main.py
timeout /t 2 /nobreak >nul
exit /b 0
