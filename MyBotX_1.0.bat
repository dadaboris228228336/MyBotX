@echo off
chcp 65001 > nul 2>&1
setlocal enabledelayedexpansion
cd /d "%~dp0"
title MyBotX 1.0
color 0A
cls

echo.
echo ========================================================
echo     MyBotX 1.0  -  Zapusk
echo ========================================================
echo.

set "ROOT_DIR=%~dp0"
set "BOT_DIR=%ROOT_DIR%BOT_APPLICATIONS"
set "TOOLS_DIR=%BOT_DIR%\platform-tools"
set "PYTHON_VER=3.10.11"
set "PYTHON_EXE="
set "LAPPDATA=%LOCALAPPDATA%"

if not exist "%BOT_DIR%" mkdir "%BOT_DIR%"

echo Zakryvaem predydushchie ekzemplyary MyBotX...
taskkill /IM "python.exe" /F >nul 2>&1
taskkill /IM "pythonw.exe" /F >nul 2>&1
timeout /t 1 /nobreak >nul

echo.
echo ========================================================
echo   Proverka neobkhodimykh komponentov
echo ========================================================
echo.

set "MISSING=0"

REM --- Python ---
echo [1/3] Proverka Python %PYTHON_VER%...

if exist "%LAPPDATA%\Programs\Python\Python313\python.exe" call :check_python "%LAPPDATA%\Programs\Python\Python313\python.exe"
if defined PYTHON_EXE goto :py_done
if exist "%LAPPDATA%\Programs\Python\Python312\python.exe" call :check_python "%LAPPDATA%\Programs\Python\Python312\python.exe"
if defined PYTHON_EXE goto :py_done
if exist "%LAPPDATA%\Programs\Python\Python311\python.exe" call :check_python "%LAPPDATA%\Programs\Python\Python311\python.exe"
if defined PYTHON_EXE goto :py_done
if exist "%LAPPDATA%\Programs\Python\Python310\python.exe" call :check_python "%LAPPDATA%\Programs\Python\Python310\python.exe"
if defined PYTHON_EXE goto :py_done
if exist "%LAPPDATA%\Programs\Python\Python39\python.exe"  call :check_python "%LAPPDATA%\Programs\Python\Python39\python.exe"
if defined PYTHON_EXE goto :py_done

if exist "C:\Program Files\Python313\python.exe" call :check_python "C:\Program Files\Python313\python.exe"
if defined PYTHON_EXE goto :py_done
if exist "C:\Program Files\Python312\python.exe" call :check_python "C:\Program Files\Python312\python.exe"
if defined PYTHON_EXE goto :py_done
if exist "C:\Program Files\Python311\python.exe" call :check_python "C:\Program Files\Python311\python.exe"
if defined PYTHON_EXE goto :py_done
if exist "C:\Program Files\Python310\python.exe" call :check_python "C:\Program Files\Python310\python.exe"
if defined PYTHON_EXE goto :py_done
if exist "C:\Python313\python.exe" call :check_python "C:\Python313\python.exe"
if defined PYTHON_EXE goto :py_done
if exist "C:\Python312\python.exe" call :check_python "C:\Python312\python.exe"
if defined PYTHON_EXE goto :py_done
if exist "C:\Python311\python.exe" call :check_python "C:\Python311\python.exe"
if defined PYTHON_EXE goto :py_done
if exist "C:\Python310\python.exe" call :check_python "C:\Python310\python.exe"
if defined PYTHON_EXE goto :py_done

REM Реестр HKCU
for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Python\PythonCore" /s /v "ExecutablePath" 2^>nul') do (
    if exist "%%b" (
        echo "%%b" | findstr /i "WindowsApps" >nul 2>&1
        if errorlevel 1 (
            call :check_python "%%b"
            if defined PYTHON_EXE goto :py_done
        )
    )
)

REM Реестр HKLM
for /f "tokens=2*" %%a in ('reg query "HKLM\Software\Python\PythonCore" /s /v "ExecutablePath" 2^>nul') do (
    if exist "%%b" (
        echo "%%b" | findstr /i "WindowsApps" >nul 2>&1
        if errorlevel 1 (
            call :check_python "%%b"
            if defined PYTHON_EXE goto :py_done
        )
    )
)

REM where python — пропускаем WindowsApps
for /f "delims=" %%p in ('where python 2^>nul') do (
    echo "%%p" | findstr /i "WindowsApps" >nul 2>&1
    if errorlevel 1 (
        call :check_python "%%p"
        if defined PYTHON_EXE goto :py_done
    )
)

:py_done
if not defined PYTHON_EXE (
    echo  [X] Python - NE NAJDEN
    set "MISSING=1"
    set "MISS_PYTHON=1"
)

REM --- ADB ---
echo [2/3] Proverka ADB...
set "ADB_EXE="

if exist "%TOOLS_DIR%\adb.exe" (
    set "ADB_EXE=%TOOLS_DIR%\adb.exe"
    echo  [OK] ADB - najden lokal'no
    goto :adb_done
)
for /f "delims=" %%p in ('where adb 2^>nul') do (
    if exist "%%p" (
        set "ADB_EXE=%%p"
        echo  [OK] ADB - najden v sisteme
        goto :adb_done
    )
)
echo  [X] ADB - NE NAJDEN
set "MISSING=1"
set "MISS_ADB=1"
:adb_done

REM --- BlueStacks ---
echo [3/3] Proverka BlueStacks 5...
set "BS_FOUND=0"
if exist "C:\Program Files\BlueStacks_nxt\HD-Player.exe"       set "BS_FOUND=1"
if exist "C:\Program Files (x86)\BlueStacks_nxt\HD-Player.exe" set "BS_FOUND=1"
if exist "C:\Program Files\BlueStacks\HD-Player.exe"           set "BS_FOUND=1"
if exist "C:\Program Files (x86)\BlueStacks\HD-Player.exe"     set "BS_FOUND=1"

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
    echo  [OK] BlueStacks 5 - najden
) else (
    echo  [X] BlueStacks 5 - NE NAJDEN
    set "MISSING=1"
    set "MISS_BS=1"
)

REM --- Отсутствующие компоненты ---
if "!MISSING!"=="1" (
    echo.
    echo ========================================================
    echo   Otsutstvuyushchie komponenty:
    echo ========================================================
    echo.
    if defined MISS_PYTHON (
        echo  - Python 3.10.11
        echo    https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
        echo.
        start "" "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
    )
    if defined MISS_ADB (
        echo  - ADB (Android Platform Tools)
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
    echo  Ustanovite komponenty i zapustite MyBotX snova.
    echo.
    timeout /t 60
    exit /b 1
)

echo.
echo  [OK] Vse komponenty najdeny.

REM --- Python пакеты ---
echo.
echo [4/4] Proverka Python paketov...

"!PYTHON_EXE!" "%ROOT_DIR%CORE\check_requirements.py" >nul 2>&1
if not errorlevel 1 (
    echo  [OK] Vse pakety ustanovleny
    goto :packages_ok
)

echo  Ustanavlivaem pakety...

"!PYTHON_EXE!" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo  pip ne najden, vosstanavlivaem...
    "!PYTHON_EXE!" -m ensurepip --upgrade >nul 2>&1
    if errorlevel 1 (
        powershell -Command "& { $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%TEMP%\get-pip.py' }" >nul 2>&1
        "!PYTHON_EXE!" "%TEMP%\get-pip.py" --quiet
        if errorlevel 1 (
            echo  [ERR] Ne udalos' ustanovit' pip!
            timeout /t 30
            exit /b 1
        )
    )
)

"!PYTHON_EXE!" -m pip install --upgrade pip --quiet
"!PYTHON_EXE!" -m pip install -r "%ROOT_DIR%CORE\requirements.txt"
if errorlevel 1 (
    echo  [ERR] Oshibka ustanovki paketov!
    timeout /t 30
    exit /b 1
)

"!PYTHON_EXE!" -c "import win32gui" >nul 2>&1
if errorlevel 1 (
    "!PYTHON_EXE!" -m pywin32_postinstall -install >nul 2>&1
)

echo  [OK] Vse pakety ustanovleny

:packages_ok

echo.
echo ========================================================
echo  Vse proverki projdeny. Zapuskaem MyBotX...
echo ========================================================
echo.

if not exist "%ROOT_DIR%CORE\main.py" (
    echo  [ERR] Fajl CORE\main.py ne najden!
    timeout /t 30
    exit /b 1
)

cd /d "%ROOT_DIR%CORE"
start "" "!PYTHON_EXE!" main.py
timeout /t 2 /nobreak >nul
exit /b 0

REM --- Подпрограмма проверки python.exe ---
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
    )
)
goto :eof
