@echo off
chcp 65001 >nul
setlocal

set REQUIRED_PYTHON=3.10.11
set MISSING=0

echo ==========================================
echo   Проверка необходимых компонентов
echo ==========================================
echo.

:: --- Проверка Python ---
for /f "tokens=2" %%V in ('python --version 2^>^&1') do set CURRENT_PYTHON=%%V

if "%CURRENT_PYTHON%"=="" (
    echo [X] Python       — НЕ НАЙДЕН
    set MISSING=1
    set MISS_PYTHON=1
) else if "%CURRENT_PYTHON%"=="%REQUIRED_PYTHON%" (
    echo [OK] Python %CURRENT_PYTHON%  — найден
) else (
    echo [X] Python       — найдена версия %CURRENT_PYTHON%, требуется %REQUIRED_PYTHON%
    set MISSING=1
    set MISS_PYTHON=1
)

:: --- Проверка ADB ---
adb version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] ADB          — НЕ НАЙДЕН
    set MISSING=1
    set MISS_ADB=1
) else (
    echo [OK] ADB          — найден
)

:: --- Проверка BlueStacks ---
set BS_FOUND=0
if exist "C:\Program Files\BlueStacks_nxt\HD-Player.exe" set BS_FOUND=1
if exist "C:\Program Files (x86)\BlueStacks_nxt\HD-Player.exe" set BS_FOUND=1

if "%BS_FOUND%"=="1" (
    echo [OK] BlueStacks   — найден
) else (
    echo [X] BlueStacks   — НЕ НАЙДЕН
    set MISSING=1
    set MISS_BS=1
)

echo.

:: --- Если всё установлено ---
if "%MISSING%"=="0" (
    echo Все компоненты установлены. Можно запускать бот.
    goto END
)

:: --- Список отсутствующих с ссылками ---
echo ==========================================
echo   Отсутствующие компоненты:
echo ==========================================
echo.

if defined MISS_PYTHON (
    echo  - Python 3.10.11
    echo    Скачать: https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    echo.
)

if defined MISS_ADB (
    echo  - ADB ^(Android Platform Tools^)
    echo    Скачать: https://dl.google.com/android/repository/platform-tools-latest-windows.zip
    echo.
)

if defined MISS_BS (
    echo  - BlueStacks 5
    echo    Скачать: https://www.bluestacks.com/download.html
    echo.
)

:END
echo.
pause
endlocal
