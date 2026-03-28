@echo off
chcp 65001 >nul
title Скачивание BlueStacks 5
color 0A

echo.
echo ════════════════════════════════════════════════════════
echo     📱 Скачивание BlueStacks 5 для MyBotX
echo ════════════════════════════════════════════════════════
echo.

REM Create BOT_APPLICATIONS directory if not exists
if not exist "BOT_APPLICATIONS" mkdir "BOT_APPLICATIONS"

echo 🔍 Попытка скачивания BlueStacks 5...
echo.

REM Try to download BlueStacks 5 from official source
echo 📥 Скачивание с официального сайта BlueStacks...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://cdn3.bluestacks.com/downloads/windows/nxt/5.22.130.1019/03f0020b47ac3b5affd5d7ea53661c44/FullInstaller/x64/BlueStacksFullInstaller_5.22.130.1019_amd64_native.exe' -OutFile 'BOT_APPLICATIONS\BlueStacksInstaller_5.22.130.1019_amd64_native.exe' -UserAgent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}"

if exist "BOT_APPLICATIONS\BlueStacksInstaller_5.22.130.1019_amd64_native.exe" (
    echo ✅ BlueStacks 5.22.130.1019 скачан успешно!
    echo 📊 Размер файла:
    dir "BOT_APPLICATIONS\BlueStacksInstaller_5.22.130.1019_amd64_native.exe" | find "BlueStacksInstaller"
) else (
    echo ❌ Не удалось скачать BlueStacks
    echo.
    echo 💡 Альтернативные варианты:
    echo 1. Скачайте вручную с https://www.bluestacks.com/download.html
    echo 2. Поместите файл в папку BOT_APPLICATIONS\
    echo 3. Переименуйте в BlueStacksInstaller_5.22.130.1019_amd64_native.exe
)

echo.
echo 📁 Содержимое папки BOT_APPLICATIONS:
dir BOT_APPLICATIONS\ /b

echo.
echo ✅ Готово!
echo.
pause