@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
chcp 65001 >nul
title MyBotX 1.0
color 0A
cls

echo.
echo ════════════════════════════════════════════════════════
echo     MyBotX 1.0  —  Запуск
echo ════════════════════════════════════════════════════════
echo.

set "ROOT_DIR=%~dp0"
set "BOT_DIR=%ROOT_DIR%BOT_APPLICATIONS"
set "TOOLS_DIR=%BOT_DIR%\platform-tools"
set "PYTHON_VER=3.10.11"
set "PYTHON_EXE="
set "LAPPDATA=%LOCALAPPDATA%"

if not exist "%BOT_DIR%" mkdir "%BOT_DIR%"

REM ── Закрываем предыдущие экземпляры ──────────────────────
echo Закрываем предыдущие экземпляры MyBotX...
taskkill /IM "python.exe" /F >nul 2>&1
taskkill /IM "pythonw.exe" /F >nul 2>&1
timeout /t 1 /nobreak >nul

REM ══════════════════════════════════════════════════════════
REM  ШАГ 1-3: Проверка компонентов
REM ══════════════════════════════════════════════════════════
echo.
echo ════════════════════════════════════════════════════════
echo   Проверка необходимых компонентов
echo ════════════════════════════════════════════════════════
echo.

set "MISSING=0"

REM ─────────────────────────────────────────────────────────
REM  Python
REM ─────────────────────────────────────────────────────────
echo [1/3] Проверка Python %PYTHON_VER%...

for %%V in (313 312 311 310 39 38) do (
    if exist "!LAPPDATA!\Programs\Python\Python%%V\python.exe" (
        call :check_python "!LAPPDATA!\Programs\Python\Python%%V\python.exe"
        if defined PYTHON_EXE goto :py_done
    )
)

for %%V in (313 312 311 310 39 38) do (
    if exist "C:\Program Files\Python%%V\python.exe" (
        call :check_python "C:\Program Files\Python%%V\python.exe"
        if defined PYTHON_EXE goto :py_done
    )
    if exist "C:\Program Files (x86)\Python%%V\python.exe" (
        call :check_python "C:\Program Files (x86)\Python%%V\python.exe"
        if defined PYTHON_EXE goto :py_done
    )
    if exist "C:\Python%%V\python.exe" (
        call :check_python "C:\Python%%V\python.exe"
        if defined PYTHON_EXE goto :py_done
    )
)

for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Python\PythonCore" /s /v "ExecutablePath" 2^>nul') do (
    if exist "%%b" (
        echo "%%b" | findstr /i "WindowsApps" >nul 2>&1
        if errorlevel 1 (
            call :check_python "%%b"
            if defined PYTHON_EXE goto :py_done
        )
    )
)

for /f "tokens=2*" %%a in ('reg query "HKLM\Software\Python\PythonCore" /s /v "ExecutablePath" 2^>nul') do (
    if exist "%%b" (
        echo "%%b" | findstr /i "WindowsApps" >nul 2>&1
        if errorlevel 1 (
            call :check_python "%%b"
            if defined PYTHON_EXE goto :py_done
        )
    )
)

for /f "delims=" %%p in ('where python 2^>nul') do (
    echo "%%p" | findstr /i "WindowsApps" >nul 2>&1
    if errorlevel 1 (
        call :check_python "%%p"
        if defined PYTHON_EXE goto :py_done
    )
)

:py_done
if not defined PYTHON_EXE (
    echo  [X] Python — НЕ НАЙДЕН
    set "MISSING=1"
    set "MISS_PYTHON=1"
)

REM ─────────────────────────────────────────────────────────
REM  ADB
REM ─────────────────────────────────────────────────────────
echo [2/3] Проверка ADB...
set "ADB_EXE="

if exist "%TOOLS_DIR%\adb.exe" (
    set "ADB_EXE=%TOOLS_DIR%\adb.exe"
    echo  [OK] ADB — найден локально
    goto :adb_done
)

for /f "delims=" %%p in ('where adb 2^>nul') do (
    if exist "%%p" (
        set "ADB_EXE=%%p"
        echo  [OK] ADB — найден в системе
        goto :adb_done
    )
)

echo  [X] ADB — НЕ НАЙДЕН
set "MISSING=1"
set "MISS_ADB=1"
:adb_done

REM ─────────────────────────────────────────────────────────
REM  BlueStacks 5
REM ─────────────────────────────────────────────────────────
echo [3/3] Проверка BlueStacks 5...
set "BS_FOUND=0"

for %%P in (
    "C:\Program Files\BlueStacks_nxt\HD-Player.exe"
    "C:\Program Files (x86)\BlueStacks_nxt\HD-Player.exe"
    "C:\Program Files\BlueStacks\HD-Player.exe"
    "C:\Program Files (x86)\BlueStacks\HD-Player.exe"
) do (
    if exist %%P set "BS_FOUND=1"
)

if "!BS_FOUND!"=="0" (
    for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\BlueStacks_nxt" /v "InstallDir" 2^>nul') do (
        if exist "%%b\HD-Player.exe" set "BS_FOUND=1"
    )
)
if "!BS_FOUND!"=="0" (
    for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\WOW6432Node\BlueStacks_nxt" /v "InstallDir" 2^>nul') do (
        if exist "%%b\HD-Player.exe" set "BS_FOUND=1"
    )
)
if "!BS_FOUND!"=="0" (
    for /f "tokens=2*" %%a in ('reg query "HKCU\SOFTWARE\BlueStacks_nxt" /v "InstallDir" 2^>nul') do (
        if exist "%%b\HD-Player.exe" set "BS_FOUND=1"
    )
)

if "!BS_FOUND!"=="1" (
    echo  [OK] BlueStacks 5 — найден
) else (
    echo  [X] BlueStacks 5 — НЕ НАЙДЕН
    set "MISSING=1"
    set "MISS_BS=1"
)

REM ─────────────────────────────────────────────────────────
REM  Если что-то отсутствует — показываем список и открываем ссылки
REM ─────────────────────────────────────────────────────────
if "!MISSING!"=="1" (
    echo.
    echo ════════════════════════════════════════════════════════
    echo   Отсутствующие компоненты. Открываем страницы загрузки:
    echo ════════════════════════════════════════════════════════
    echo.
    if defined MISS_PYTHON (
        echo  - Python 3.10.11
        echo    https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
        echo.
        start "" "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
    )
    if defined MISS_ADB (
        echo  - ADB ^(Android Platform Tools^)
        echo    https://dl.google.com/android/repository/platform-tools-latest-windows.zip
        echo.
        start "" "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    )
    if defined MISS_BS (
        echo  - BlueStacks 5
        echo    https://www.bluestacks.com/download.html
        echo.
        start "" "https://www.bluestacks.com/download.html"
    )
    echo.
    echo  Установите компоненты и запустите MyBotX снова.
    echo.
    echo  Это окно закроется через 60 секунд...
    timeout /t 60
    exit /b 1
)

echo.
echo  [OK] Все компоненты найдены.

REM ══════════════════════════════════════════════════════════
REM  ШАГ 4: Python пакеты
REM ══════════════════════════════════════════════════════════
echo.
echo [4/4] Проверка Python пакетов...

"!PYTHON_EXE!" "%ROOT_DIR%CORE\check_requirements.py" >nul 2>&1
if not errorlevel 1 (
    echo  [OK] Все пакеты установлены
    goto :packages_ok
)

echo  Устанавливаем пакеты...

"!PYTHON_EXE!" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo  pip не найден, восстанавливаем...
    "!PYTHON_EXE!" -m ensurepip --upgrade >nul 2>&1
    if errorlevel 1 (
        echo  Скачиваем get-pip.py...
        powershell -Command "& { $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%TEMP%\get-pip.py' }" >nul 2>&1
        "!PYTHON_EXE!" "%TEMP%\get-pip.py" --quiet
        if errorlevel 1 (
            echo  [ERR] Не удалось установить pip. Переустановите Python с галочкой pip.
            timeout /t 30
            exit /b 1
        )
    )
)

"!PYTHON_EXE!" -m pip install --upgrade pip --quiet
"!PYTHON_EXE!" -m pip install -r "%ROOT_DIR%CORE\requirements.txt"
if errorlevel 1 (
    echo  [ERR] Ошибка установки пакетов!
    timeout /t 30
    exit /b 1
)

"!PYTHON_EXE!" -c "import win32gui" >nul 2>&1
if errorlevel 1 (
    echo  Настройка pywin32...
    "!PYTHON_EXE!" -m pywin32_postinstall -install >nul 2>&1
)

echo  [OK] Все пакеты установлены

:packages_ok

REM ══════════════════════════════════════════════════════════
REM  ЗАПУСК
REM ══════════════════════════════════════════════════════════
echo.
echo ════════════════════════════════════════════════════════
echo  Все проверки пройдены. Запускаем MyBotX...
echo ════════════════════════════════════════════════════════
echo.

if not exist "%ROOT_DIR%CORE\main.py" (
    echo  [ERR] Файл CORE\main.py не найден!
    timeout /t 30
    exit /b 1
)

cd /d "%ROOT_DIR%CORE"
start "" "!PYTHON_EXE!" main.py
timeout /t 2 /nobreak >nul
exit /b 0

REM ══════════════════════════════════════════════════════════
REM  ПОДПРОГРАММА: проверка python.exe
REM ══════════════════════════════════════════════════════════
:check_python
set "_PY_TMP="
for /f "tokens=2" %%v in ('"%~1" --version 2^>^&1') do set "_PY_TMP=%%v"
echo !_PY_TMP! | findstr /r "^[0-9][0-9]*\.[0-9]" >nul 2>&1
if errorlevel 1 goto :eof
for /f "tokens=1,2 delims=." %%a in ("!_PY_TMP!") do (
    if %%a GEQ 3 if %%b GEQ 10 (
        set "PYTHON_EXE=%~1"
        set "PY_VER=!_PY_TMP!"
        echo  [OK] Python !_PY_TMP!
    ) else (
        echo  [X] Python !_PY_TMP! — версия ниже 3.10, пропускаем
    )
)
goto :eof
