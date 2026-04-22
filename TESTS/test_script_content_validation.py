"""
Unit tests for script content validation — task 8.2.
Tests additional validation logic in MyBotX_1.0.bat not already covered
by test_run_bat_content.py.

Requirements: 2.1, 3.1, 4.1, 4.2, 4.3, 4.4, 8.5, 10.3
"""

import pytest
from pathlib import Path

ROOT = Path(__file__).parent.parent
MAIN_BAT = ROOT / "MyBotX_1.0.bat"


@pytest.fixture(scope="module")
def bat_content():
    assert MAIN_BAT.exists(), f"MyBotX_1.0.bat not found at {MAIN_BAT}"
    return MAIN_BAT.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def bat_lines(bat_content):
    return bat_content.splitlines()


# ---------------------------------------------------------------------------
# Requirement 2.1 — Python validation command presence
# ---------------------------------------------------------------------------

class TestPythonValidation:
    """Validates: Requirements 2.1"""

    def test_python_version_flag_present(self, bat_content):
        """The launcher calls python --version to detect Python."""
        assert "--version" in bat_content

    def test_check_python_subroutine_defined(self, bat_content):
        """A :check_python subroutine is defined for version validation."""
        assert ":check_python" in bat_content

    def test_python_version_comparison_major(self, bat_content):
        """Launcher checks major version >= 3."""
        assert "GEQ 3" in bat_content

    def test_python_version_comparison_minor(self, bat_content):
        """Launcher checks minor version >= 10."""
        assert "GEQ 10" in bat_content

    def test_python_exe_variable_set_on_success(self, bat_content):
        """PYTHON_EXE variable is set when a valid Python is found."""
        assert "PYTHON_EXE" in bat_content

    def test_python_not_found_message(self, bat_content):
        """Launcher emits a clear message when Python is not found."""
        assert "Python - NOT FOUND" in bat_content

    def test_python_missing_flag_set(self, bat_content):
        """MISS_PYTHON flag is set when Python is absent."""
        assert "MISS_PYTHON" in bat_content


# ---------------------------------------------------------------------------
# Requirement 3.1 — tkinter / package validation command presence
# The real launcher validates packages via pip install from requirements.txt
# rather than a direct tkinter import check.
# ---------------------------------------------------------------------------

class TestPackageValidation:
    """Validates: Requirements 3.1"""

    def test_pip_install_present(self, bat_content):
        """Launcher installs Python packages via pip."""
        assert "pip install" in bat_content

    def test_requirements_txt_referenced(self, bat_content):
        """Launcher references requirements.txt for package installation."""
        assert "requirements.txt" in bat_content

    def test_pip_version_check_present(self, bat_content):
        """Launcher verifies pip is available before installing packages."""
        assert "pip --version" in bat_content

    def test_ensurepip_fallback_present(self, bat_content):
        """Launcher falls back to ensurepip when pip is missing."""
        assert "ensurepip" in bat_content

    def test_package_install_error_message(self, bat_content):
        """Launcher reports an error when package installation fails."""
        assert "Package installation failed" in bat_content or "[ERR]" in bat_content

    def test_packages_ok_success_message(self, bat_content):
        """Launcher confirms all packages are installed on success."""
        assert "All packages installed" in bat_content


# ---------------------------------------------------------------------------
# Requirements 4.1–4.4 — File existence checks
# ---------------------------------------------------------------------------

class TestFileExistenceChecks:
    """Validates: Requirements 4.1, 4.2, 4.3, 4.4"""

    def test_core_directory_check_present(self, bat_content):
        """Launcher checks that the CORE directory / main.py exists."""
        assert "CORE" in bat_content

    def test_main_py_existence_check(self, bat_content):
        """Launcher verifies main.py exists before launching."""
        assert "main.py" in bat_content
        assert "not exist" in bat_content

    def test_main_py_not_found_error(self, bat_content):
        """Launcher emits an error when main.py is missing."""
        assert "main.py not found" in bat_content or "CORE\\main.py" in bat_content

    def test_adb_check_present(self, bat_content):
        """Launcher checks for ADB executable."""
        assert "adb.exe" in bat_content or "ADB_EXE" in bat_content

    def test_adb_not_found_message(self, bat_content):
        """Launcher reports ADB not found."""
        assert "ADB - NOT FOUND" in bat_content

    def test_bluestacks_check_present(self, bat_content):
        """Launcher checks for BlueStacks installation."""
        assert "BlueStacks" in bat_content or "HD-Player.exe" in bat_content

    def test_bluestacks_not_found_message(self, bat_content):
        """Launcher reports BlueStacks not found."""
        assert "BlueStacks 5 - NOT FOUND" in bat_content

    def test_missing_flag_used_for_gating(self, bat_content):
        """MISSING flag gates the download/error section."""
        assert "MISSING" in bat_content


# ---------------------------------------------------------------------------
# Requirement 8.5 — Error message content
# ---------------------------------------------------------------------------

class TestErrorMessageContent:
    """Validates: Requirements 8.5"""

    def test_python_download_url_present(self, bat_content):
        """Error section provides a Python download URL."""
        assert "python.org" in bat_content or "python-3.10" in bat_content

    def test_bluestacks_download_url_present(self, bat_content):
        """Error section provides a BlueStacks download URL."""
        assert "bluestacks.com" in bat_content or "BlueStacksInstaller" in bat_content

    def test_missing_components_section_header(self, bat_content):
        """Error section has a clear header for missing components."""
        assert "Missing components" in bat_content

    def test_install_instruction_present(self, bat_content):
        """Error section instructs user to install missing components."""
        assert "Install missing components" in bat_content

    def test_pip_not_found_error_message(self, bat_content):
        """Launcher provides guidance when pip is not found."""
        assert "pip" in bat_content and ("Reinstall" in bat_content or "reinstall" in bat_content
                                          or "pip checkbox" in bat_content)

    def test_pause_after_error(self, bat_content):
        """Launcher pauses after displaying errors so user can read them."""
        assert "pause" in bat_content

    def test_exit_code_1_on_error(self, bat_content):
        """Launcher exits with code 1 on any validation failure."""
        assert "exit /b 1" in bat_content


# ---------------------------------------------------------------------------
# Requirement 10.3 — Success message content
# ---------------------------------------------------------------------------

class TestSuccessMessageContent:
    """Validates: Requirements 10.3"""

    def test_all_components_found_message(self, bat_content):
        """Launcher confirms all components are found before proceeding."""
        assert "All components found" in bat_content

    def test_all_checks_passed_message(self, bat_content):
        """Launcher confirms all checks passed before launching."""
        assert "All checks passed" in bat_content

    def test_starting_application_message(self, bat_content):
        """Launcher announces it is starting the application."""
        assert "Starting MyBotX" in bat_content

    def test_adb_found_locally_message(self, bat_content):
        """Launcher confirms ADB found locally."""
        assert "ADB - found" in bat_content

    def test_bluestacks_found_message(self, bat_content):
        """Launcher confirms BlueStacks found."""
        assert "BlueStacks 5 - found" in bat_content


# ---------------------------------------------------------------------------
# Requirements 8.5, 10.3 — Visual indicators [OK] / [X] / [ERR]
# ---------------------------------------------------------------------------

class TestVisualIndicators:
    """Validates: Requirements 8.5, 10.3"""

    def test_ok_indicator_present(self, bat_content):
        """[OK] indicator is used for success states."""
        assert "[OK]" in bat_content

    def test_x_indicator_present(self, bat_content):
        """[X] indicator is used for not-found states."""
        assert "[X]" in bat_content

    def test_err_indicator_present(self, bat_content):
        """[ERR] indicator is used for error/failure states."""
        assert "[ERR]" in bat_content

    def test_ok_used_for_python_success(self, bat_content):
        """[OK] appears alongside Python version on success."""
        # The check_python subroutine echoes [OK] Python <version>
        assert "[OK] Python" in bat_content

    def test_ok_used_for_adb_success(self, bat_content):
        """[OK] appears when ADB is found."""
        assert "[OK] ADB" in bat_content

    def test_ok_used_for_bluestacks_success(self, bat_content):
        """[OK] appears when BlueStacks is found."""
        assert "[OK] BlueStacks" in bat_content

    def test_ok_used_for_packages_success(self, bat_content):
        """[OK] appears when all packages are installed."""
        assert "[OK] All packages installed" in bat_content

    def test_x_used_for_python_failure(self, bat_content):
        """[X] appears when Python is not found."""
        assert "[X] Python" in bat_content

    def test_x_used_for_adb_failure(self, bat_content):
        """[X] appears when ADB is not found."""
        assert "[X] ADB" in bat_content

    def test_x_used_for_bluestacks_failure(self, bat_content):
        """[X] appears when BlueStacks is not found."""
        assert "[X] BlueStacks" in bat_content

    def test_err_used_for_pip_failure(self, bat_content):
        """[ERR] appears when pip installation fails."""
        assert "[ERR]" in bat_content

    def test_no_emoji_indicators(self, bat_content):
        """Launcher uses text indicators, not emoji (bat file limitation)."""
        assert "✅" not in bat_content
        assert "❌" not in bat_content
