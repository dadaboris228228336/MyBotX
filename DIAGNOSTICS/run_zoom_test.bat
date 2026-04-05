@echo off
cd /d "%~dp0"
chcp 65001 >nul
title Zoom Methods Test
color 0B
python "%~dp0test_zoom_methods.py"
