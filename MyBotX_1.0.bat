@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title MyBotX 1.0
color 0A
cls

echo.
echo ========================================================
echo     MyBotX 1.0  -  Starting...
echo ========================================================
echo.

set "ROOT_DIR=%~dp0"
set "BOT_DIR=%ROOT_DIR%BOT_APPLICATIONS"
set "TOOLS_DIR=%BOT_DIR%\platform-tools"
set "PYTHON_VER=3.10.11"
set "PYTHON_EXE="
set "LAPPDATA=%LOCALAPPDATA%"
set "MISSING=0"
set "MISS_PYTHON="
set "MISS_ADB="
set "MISS_BS="

if not exist "%BOT_DIR%" mkdir "%BOT_DIR%"

echo Closing previous MyBotX instances...
taskkill /IM "python.exe" /F >nul 2>&1
taskkill /IM "pythonw.exe" /F >nul 2>&1
timeout /t 1 /nobreak >nul

echo.
echo ========================================================
echo   Checking required components...
echo ========================================================
echo.

REM --- Python ---
echo [1/3] Checking Python %PYTHON_VER%...

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
    echo  [X] Python - NOT FOUND
    set "MISSING=1"
    set "MISS_PYTHON=1"
)

REM --- ADB ---
echo [2/3] Checking ADB...
set "ADB_EXE="

if exist "%TOOLS_DIR%\adb.exe" (
    set "ADB_EXE=%TOOLS_DIR%\adb.exe"
    echo  [OK] ADB - found locally
    goto :adb_done
)
for /f "delims=" %%p in ('where adb 2^>nul') do (
    if exist "%%p" (
        set "ADB_EXE=%%p"
        echo  [OK] ADB - found in system
        goto :adb_done
    )
)
echo  [X] ADB - NOT FOUND
set "MISSING=1"
set "MISS_ADB=1"
:adb_done

REM --- BlueStacks ---
echo [3/3] Checking BlueStacks 5...
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
    echo  [OK] BlueStacks 5 - found
) else (
    echo  [X] BlueStacks 5 - NOT FOUND
    set "MISSING=1"
    set "MISS_BS=1"
)

REM --- Missing components ---
if "!MISSING!"=="1" (
    echo.
    echo ========================================================
    echo   Missing components. Opening download pages...
    echo ========================================================
    echo.
    if defined MISS_PYTHON (
        echo  - Python 3.10.11
        echo    https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
        echo.
        start "" "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
    )
    if defined MISS_BS (
        echo  - BlueStacks 5
        echo    https://cdn3.bluestacks.com/public/BlueStacksInstaller_5.exe
        echo.
        start "" "https://cdn3.bluestacks.com/public/BlueStacksInstaller_5.exe"
    )
    echo.
    echo  Install missing components and run MyBotX again.
    echo.
    pause
    exit /b 1
)

echo.
echo  [OK] All components found.

REM --- Python packages ---
echo.
echo [4/4] Checking Python packages...

"!PYTHON_EXE!" "%ROOT_DIR%CORE\check_requirements.py" >nul 2>&1
if not errorlevel 1 (
    echo  [OK] All packages installed
    goto :packages_ok
)

echo  Installing packages...

"!PYTHON_EXE!" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo  pip not found, restoring...
    "!PYTHON_EXE!" -m ensurepip --upgrade >nul 2>&1
    if errorlevel 1 (
        powershell -Command "& { $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%TEMP%\get-pip.py' }" >nul 2>&1
        "!PYTHON_EXE!" "%TEMP%\get-pip.py" --quiet
        if errorlevel 1 (
            echo  [ERR] Failed to install pip. Reinstall Python with pip checkbox.
            pause
            exit /b 1
        )
    )
)

"!PYTHON_EXE!" -m pip install --upgrade pip --quiet
"!PYTHON_EXE!" -m pip install -r "%ROOT_DIR%CORE\requirements.txt"
if errorlevel 1 (
    echo  [ERR] Package installation failed!
    pause
    exit /b 1
)

"!PYTHON_EXE!" -c "import win32gui" >nul 2>&1
if errorlevel 1 (
    "!PYTHON_EXE!" -m pywin32_postinstall -install >nul 2>&1
)

echo  [OK] All packages installed

:packages_ok

echo.
echo ========================================================
echo  All checks passed. Starting MyBotX...
echo ========================================================
echo.

if not exist "%ROOT_DIR%CORE\main.py" (
    echo  [ERR] File CORE\main.py not found!
    pause
    exit /b 1
)

cd /d "%ROOT_DIR%CORE"
start "" "!PYTHON_EXE!" main.py
timeout /t 2 /nobreak >nul
exit /b 0

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
