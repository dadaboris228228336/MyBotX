@echo off
cd /d "%~dp0"
chcp 65001 >nul
title Pattern Search Test
color 0A
python "%~dp0test_pattern_search.py"
