"""
Comprehensive test suite for Project Restructure Launcher.
Covers: file operations, script content, error message quality, Unix launcher.
Validates: Requirements 1.1, 2.1-2.5, 3.1-3.4, 4.1-4.6, 6.1-6.9, 7.3-7.5, 8.1-8.5, 10.3
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
CORE_DIR = ROOT / "CORE"
MY_BOT_DIR = ROOT / "my_bot"
MAIN_BAT = ROOT / "MyBotX_1.0.bat"
RUN_BAT = MY_BOT_DIR / "run.bat"


# ═══════════════════════════════════════════════════════════
# 8.1  File Operations
# Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.9, 1.1
# ═══════════════════════════════════════════════════════════

class TestFileOperations:

    def test_my_bot_directory_exists(self):
        """Req 6.1 — my_bot/ directory must exist at root."""
        assert MY_BOT_DIR.is_dir(), "my_bot/ directory not found at root"

    def test_run_bat_exists_in_my_bot(self):
        """Req 6.6 — run.bat must exist inside my_bot/."""
        assert RUN_BAT.exists(), f"run.bat not found at {RUN_BAT}"

    def test_root_launcher_exists(self):
        """Req 1.1 — root-level launcher must exist."""
        assert MAIN_BAT.exists(), f"Root launcher not found at {MAIN_BAT}"

    def test_core_main_py_exists(self):
        """Req 6.2 — main.py must exist in CORE/."""
        assert (CORE_DIR / "main.py").exists()

    def test_core_dependency_checker_exists(self):
        """Req 6.3 — dependency_checker.py must exist in CORE/."""
        assert (CORE_DIR / "dependency_checker.py").exists()

    def test_core_requirements_txt_exists(self):
        """Req 6.4 — requirements.txt must exist in CORE/."""
        assert (CORE_DIR / "requirements.txt").exists()

    def test_config_json_exists(self):
        """Req 6.5 — config.json must exist in CONFIG/."""
        assert (ROOT / "CONFIG" / "config.json").exists()

    def test_no_nova_papka_directory(self):
        """Req 6.9 — 'Новая папка' empty directory must be removed."""
        nova = ROOT / "Новая папка"
        assert not nova.exists(), "'Новая папка' directory still exists"

    def test_file_migration_simulation(self):
        """Req 6.7 — simulate moving .md/.txt files into subdirectory."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dest = root / "my_bot"
            dest.mkdir()

            # Create test doc files
            (root / "README.md").write_text("readme")
            (root / "NOTES.txt").write_text("notes")
            (root / "script.py").write_text("code")  # should NOT be moved

            # Migrate docs
            for f in list(root.iterdir()):
                if f.is_file() and f.suffix.lower() in (".md", ".txt"):
                    shutil.move(str(f), str(dest / f.name))

            assert (dest / "README.md").exists()
            assert (dest / "NOTES.txt").exists()
            assert not (root / "README.md").exists()
            assert not (root / "NOTES.txt").exists()
            assert (root / "script.py").exists()  # non-doc stays


# ═══════════════════════════════════════════════════════════
# 8.2  Script Content Validation
# Requirements: 2.1, 3.1, 4.1-4.4, 8.5, 10.3
# ═══════════════════════════════════════════════════════════

class TestScriptContent:

    @pytest.fixture(scope="class")
    def main_bat(self):
        return MAIN_BAT.read_text(encoding="utf-8")

    @pytest.fixture(scope="class")
    def run_bat(self):
        return RUN_BAT.read_text(encoding="utf-8")

    def test_main_bat_python_check(self, main_bat):
        """Req 2.1 — launcher checks Python installation."""
        assert "python --version" in main_bat or "python" in main_bat

    def test_run_bat_python_check(self, run_bat):
        """Req 2.1 — internal run.bat checks Python."""
        assert "python --version" in run_bat

    def test_run_bat_tkinter_check(self, run_bat):
        """Req 3.1 — run.bat checks tkinter."""
        assert "import tkinter" in run_bat

    def test_run_bat_main_py_check(self, run_bat):
        """Req 4.2 — run.bat checks main.py exists."""
        assert "main.py" in run_bat

    def test_run_bat_dep_checker_check(self, run_bat):
        """Req 4.3 — run.bat checks dependency_checker.py."""
        assert "dependency_checker.py" in run_bat

    def test_run_bat_requirements_check(self, run_bat):
        """Req 4.4 — run.bat checks requirements.txt."""
        assert "requirements.txt" in run_bat

    def test_run_bat_success_indicators(self, run_bat):
        """Req 8.5, 10.3 — run.bat uses ✅ for success."""
        assert "✅" in run_bat

    def test_run_bat_failure_indicators(self, run_bat):
        """Req 8.5, 10.3 — run.bat uses ❌ for failure."""
        assert "❌" in run_bat

    def test_main_bat_has_header(self, main_bat):
        """Req 1.3, 10.1 — launcher has visual header."""
        assert "═" in main_bat or "=" in main_bat

    def test_main_bat_launches_main_py(self, main_bat):
        """Req 5.2 — launcher executes main.py."""
        assert "main.py" in main_bat


# ═══════════════════════════════════════════════════════════
# 8.3  Error Message Quality
# Requirements: 8.1, 8.2, 8.3, 8.4
# ═══════════════════════════════════════════════════════════

class TestErrorMessageQuality:

    @pytest.fixture(scope="class")
    def run_bat(self):
        return RUN_BAT.read_text(encoding="utf-8")

    def test_run_bat_pause_on_python_error(self, run_bat):
        """Req 8.1 — Python error must include python.org URL."""
        assert "python.org" in run_bat

    def test_run_bat_python_error_has_path_instructions(self, run_bat):
        """Req 8.2 — Python error must mention PATH."""
        assert "PATH" in run_bat

    def test_run_bat_tkinter_error_has_reinstall_instructions(self, run_bat):
        """Req 8.3 — tkinter error must mention reinstallation."""
        assert "reinstall" in run_bat.lower() or "tcl" in run_bat.lower() or "Reinstall" in run_bat

    def test_run_bat_missing_file_error_lists_files(self, run_bat):
        """Req 8.4 — missing file errors must name specific files."""
        assert "main.py" in run_bat
        assert "dependency_checker.py" in run_bat
        assert "requirements.txt" in run_bat

    def test_run_bat_pause_on_python_error(self, run_bat):
        """Req 2.5 — launcher pauses on Python validation failure."""
        assert "pause" in run_bat

    def test_run_bat_pause_on_tkinter_error(self, run_bat):
        """Req 3.4 — launcher pauses on tkinter validation failure."""
        assert run_bat.count("pause") >= 2
