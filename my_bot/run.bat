@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title MyBotX
cls

echo.
echo ════════════════════════════════════════════════════════
echo     🚀 MyBotX Launcher
echo ════════════════════════════════════════════════════════
echo.

REM ══════════════════════════════════════
REM STEP 1: Validate Python
REM ══════════════════════════════════════
echo 🐍 Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not installed or not in PATH
    echo.
    echo Solution:
    echo   1. Download Python 3.10+ from https://python.org
    echo   2. During installation, CHECK "Add Python to PATH"
    echo   3. Restart this launcher
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo ✅ %%v

REM ══════════════════════════════════════
REM STEP 2: Validate tkinter
REM ══════════════════════════════════════
echo 🖼️  Checking tkinter...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: tkinter not available
    echo.
    echo Solution:
    echo   Reinstall Python and ensure "tcl/tk and IDLE" is checked during setup.
    echo.
    pause
    exit /b 1
)
echo ✅ tkinter: OK

REM ══════════════════════════════════════
REM STEP 3: Validate project files
REM (run.bat is already inside my_bot/, so paths are relative)
REM ══════════════════════════════════════
echo 📁 Checking project files...
set "MISSING="

if not exist "%~dp0main.py"               set "MISSING=%MISSING% main.py"
if not exist "%~dp0dependency_checker.py" set "MISSING=%MISSING% dependency_checker.py"
if not exist "%~dp0requirements.txt"      set "MISSING=%MISSING% requirements.txt"

if not "%MISSING%"=="" (
    echo ❌ Error: Required files are missing:
    for %%f in (%MISSING%) do echo   ❌ %%f
    echo.
    pause
    exit /b 1
)
echo ✅ main.py: OK
echo ✅ dependency_checker.py: OK
echo ✅ requirements.txt: OK

REM ══════════════════════════════════════
REM STEP 4: Launch application
REM ══════════════════════════════════════
echo.
echo ════════════════════════════════════════════════════════
echo ✅ All checks passed! Launching application...
echo ════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo ❌ Error: Application failed to launch
    pause
    exit /b 1
)
