@echo off
cd /d "%~dp0.."
chcp 65001 >nul
title MyBotX Builder
color 0A

echo.
echo ================================================
echo     MyBotX 1.0.0 - Builder
echo ================================================
echo.

python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [*] Устанавливаем PyInstaller...
    python -m pip install pyinstaller --quiet
)

echo [*] Собираем MyBotX.exe...
echo.

python -m PyInstaller BUILDER\MyBotX.spec --noconfirm --distpath BUILDER\dist --workpath BUILDER\work

if errorlevel 1 (
    echo [!] Ошибка сборки!
    pause
    exit /b 1
)

echo.
echo [OK] Готово: BUILDER\dist\MyBotX.exe
echo.

if not exist "BUILDER\dist\CONFIG"   mkdir "BUILDER\dist\CONFIG"
if not exist "BUILDER\dist\my_bot"   mkdir "BUILDER\dist\my_bot"

xcopy /E /I /Y "CONFIG" "BUILDER\dist\CONFIG" >nul
xcopy /E /I /Y "my_bot" "BUILDER\dist\my_bot" >nul

echo [OK] Папки скопированы
pause
