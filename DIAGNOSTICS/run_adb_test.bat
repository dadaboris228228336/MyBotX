@echo off
cd /d "%~dp0"
chcp 65001 >nul
title ADB Commands Test
color 0B
python "%~dp0test_adb_commands.py"
