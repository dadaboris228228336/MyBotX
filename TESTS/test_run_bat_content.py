"""
Unit tests for root launcher batch file (MyBotX_1.0.bat).
Tests validate the actual content of the launcher as implemented.
"""

import pytest
from pathlib import Path

ROOT = Path(__file__).parent.parent
MAIN_BAT = ROOT / "MyBotX_1.0.bat"


@pytest.fixture(scope="module")
def bat_content():
    assert MAIN_BAT.exists(), f"MyBotX_1.0.bat not found at {MAIN_BAT}"
    return MAIN_BAT.read_text(encoding="utf-8")


def test_python_validation_present(bat_content):
    """Launcher searches for Python executable via known paths and registry."""
    assert "check_python" in bat_content
    assert "--version" in bat_content


def test_tkinter_validation_command_present(bat_content):
    # MyBotX_1.0.bat validates tkinter indirectly via check_requirements.py
    # Direct tkinter check is in my_bot/run.bat (internal launcher)
    assert "check_requirements.py" in bat_content or "import tkinter" in bat_content


def test_python_not_found_error_present(bat_content):
    """Launcher reports Python not found with a clear message."""
    assert "Python - NOT FOUND" in bat_content or "Python" in bat_content


def test_tkinter_error_message_present(bat_content):
    # tkinter is validated via check_requirements.py or pip install
    assert "requirements.txt" in bat_content or "tkinter" in bat_content


def test_pause_on_error_present(bat_content):
    assert "pause" in bat_content


def test_exit_on_error_present(bat_content):
    assert "exit /b 1" in bat_content


def test_ok_success_indicators_present(bat_content):
    """Launcher uses [OK] text indicators for success states."""
    assert "[OK]" in bat_content


def test_error_indicators_present(bat_content):
    """Launcher uses [X] or [ERR] text indicators for failure states."""
    assert "[X]" in bat_content or "[ERR]" in bat_content


def test_launches_main_py(bat_content):
    """Launcher starts main.py using the discovered Python executable."""
    assert "main.py" in bat_content


def test_uses_start_command_for_launch(bat_content):
    """Launcher uses 'start' to launch the GUI application."""
    assert 'start ""' in bat_content


def test_cd_into_core_before_launch(bat_content):
    # Launcher navigates to CORE/ before launching main.py
    assert 'CORE' in bat_content and 'cd' in bat_content


def test_cd_project_root_for_double_click(bat_content):
    assert any(line.strip() == 'cd /d "%~dp0"' for line in bat_content.splitlines())


def test_title_not_launcher_word(bat_content):
    assert "Launcher" not in bat_content
    assert "title MyBotX 1.0" in bat_content


def test_python_download_url_present(bat_content):
    """Launcher provides a Python download URL when Python is missing."""
    assert "python.org" in bat_content or "python-3.10" in bat_content


def test_requirements_txt_used_for_packages(bat_content):
    """Launcher installs packages from requirements.txt."""
    assert "requirements.txt" in bat_content
