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

REM ── Версии ───────────────────────────────────────────────
set "PYTHON_VER=3.10.11"

REM ── Создаём папку BOT_APPLICATIONS если нет ──────────────
if not exist "%BOT_DIR%" mkdir "%BOT_DIR%"

REM ── Закрываем предыдущие экземпляры ─────────────────────
echo Закрываем предыдущие экземпляры MyBotX...
taskkill /IM "python.exe" /F >nul 2>&1
taskkill /IM "pythonw.exe" /F >nul 2>&1
timeout /t 1 /nobreak >nul

REM ══════════════════════════════════════════════════════════
REM  ШАГ 1-3: Проверка наличия компонентов
REM ══════════════════════════════════════════════════════════
echo.
echo ════════════════════════════════════════════════════════
echo   Проверка необходимых компонентов
echo ════════════════════════════════════════════════════════
echo.

set "MISSING=0"

REM --- Python ---
echo [1/3] Проверка Python %PYTHON_VER%...
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
if "!PY_VER!"=="" (
    echo  [X] Python — НЕ НАЙДЕН
    set "MISSING=1"
    set "MISS_PYTHON=1"
) else (
    for /f "tokens=1,2 delims=." %%a in ("!PY_VER!") do (
        set "PY_MAJOR=%%a"
        set "PY_MINOR=%%b"
    )
    if !PY_MAJOR! GEQ 3 if !PY_MINOR! GEQ 10 (
        echo  [OK] Python !PY_VER!
    ) else (
        echo  [X] Python — найдена версия !PY_VER!, требуется 3.10+
        set "MISSING=1"
        set "MISS_PYTHON=1"
    )
)

REM --- ADB ---
echo [2/3] Проверка ADB...
if exist "%TOOLS_DIR%\adb.exe" (
    echo  [OK] ADB — найден в %TOOLS_DIR%
    goto adb_ok
)
where adb >nul 2>&1
if not errorlevel 1 (
    echo  [OK] ADB — найден в системе
    goto adb_ok
)
echo  [X] ADB — НЕ НАЙДЕН
set "MISSING=1"
set "MISS_ADB=1"
:adb_ok

REM --- BlueStacks ---
echo [3/3] Проверка BlueStacks 5...
set "BS_FOUND=0"
if exist "C:\Program Files\BlueStacks_nxt\HD-Player.exe"       set "BS_FOUND=1"
if exist "C:\Program Files (x86)\BlueStacks_nxt\HD-Player.exe" set "BS_FOUND=1"
if exist "C:\Program Files\BlueStacks\HD-Player.exe"           set "BS_FOUND=1"
if exist "C:\Program Files (x86)\BlueStacks\HD-Player.exe"     set "BS_FOUND=1"
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\BlueStacks_nxt" /v "InstallDir" 2^>nul') do (
    if exist "%%b\HD-Player.exe" set "BS_FOUND=1"
)
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\WOW6432Node\BlueStacks_nxt" /v "InstallDir" 2^>nul') do (
    if exist "%%b\HD-Player.exe" set "BS_FOUND=1"
)
if "!BS_FOUND!"=="1" (
    echo  [OK] BlueStacks 5 — найден
) else (
    echo  [X] BlueStacks 5 — НЕ НАЙДЕН
    set "MISSING=1"
    set "MISS_BS=1"
)

REM --- Если что-то отсутствует — показываем список со ссылками и выходим ---
if "!MISSING!"=="1" (
    echo.
    echo ════════════════════════════════════════════════════════
    echo   Отсутствующие компоненты. Скачайте и установите:
    echo ════════════════════════════════════════════════════════
    echo.
    if defined MISS_PYTHON (
        echo  - Python 3.10.11
        echo    https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
        echo.
    )
    if defined MISS_ADB (
        echo  - ADB ^(Android Platform Tools^)
        echo    https://dl.google.com/android/repository/platform-tools-latest-windows.zip
        echo.
    )
    if defined MISS_BS (
        echo  - BlueStacks 5
        echo    https://www.bluestacks.com/download.html
        echo.
    )
    pause
    exit /b 1
)

echo.
echo  Все компоненты найдены.

REM ══════════════════════════════════════════════════════════
REM  ШАГ 4: Python пакеты
REM ══════════════════════════════════════════════════════════
echo.
echo [4/4] Проверка Python пакетов...
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
