@echo off
cd /d "%~dp0"
if not exist "%~dp0MyBotX_1.0.bat" (
    echo ОШИБКА: не найден MyBotX_1.0.bat рядом с этим файлом.
    echo Папка: %~dp0
    pause
    exit /b 1
)
call "%~dp0MyBotX_1.0.bat" %*
