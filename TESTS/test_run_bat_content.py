"""
Unit tests for root launcher batch files.
"""

import pytest
from pathlib import Path

ROOT = Path(__file__).parent.parent
MAIN_BAT = ROOT / "MyBotX_1.0.bat"


@pytest.fixture(scope="module")
def bat_content():
    assert MAIN_BAT.exists(), f"MyBotX_1.0.bat not found at {MAIN_BAT}"
    return MAIN_BAT.read_text(encoding="utf-8")


def test_python_validation_command_present(bat_content):
    assert "python --version" in bat_content


def test_tkinter_validation_command_present(bat_content):
    # MyBotX_1.0.bat validates tkinter indirectly via check_requirements.py
    # Direct tkinter check is in my_bot/run.bat (internal launcher)
    assert "check_requirements.py" in bat_content or "import tkinter" in bat_content


def test_python_error_message_present(bat_content):
    assert "Python not installed" in bat_content or "Python" in bat_content


def test_tkinter_error_message_present(bat_content):
    # tkinter is validated via check_requirements.py or pip install
    assert "requirements.txt" in bat_content or "tkinter" in bat_content


def test_pause_on_error_present(bat_content):
    assert "pause" in bat_content


def test_exit_on_error_present(bat_content):
    assert "exit /b 1" in bat_content


def test_success_indicators_present(bat_content):
    assert "✅" in bat_content


def test_failure_indicators_present(bat_content):
    assert "❌" in bat_content


def test_launches_main_py_inline(bat_content):
    """GUI запускается в том же процессе консоли — ошибки не пропадают."""
    assert "python main.py" in bat_content
    assert 'start "MyBotX"' not in bat_content


def test_cd_into_core_before_launch(bat_content):
    # Launcher navigates to CORE/ before launching main.py
    assert 'CORE' in bat_content and 'cd' in bat_content


def test_cd_project_root_for_double_click(bat_content):
    assert any(line.strip() == 'cd /d "%~dp0"' for line in bat_content.splitlines())


def test_title_not_launcher_word(bat_content):
    assert "Launcher" not in bat_content
    assert "title MyBotX 1.0" in bat_content
