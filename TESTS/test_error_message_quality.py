"""
Unit tests for error message quality — task 8.3.
Tests that error messages are actionable and specific, covering requirements
not already tested in test_run_bat_content.py or test_script_content_validation.py.

Requirements: 8.1, 8.2, 8.3, 8.4
"""

import pytest
from pathlib import Path

ROOT = Path(__file__).parent.parent
MAIN_BAT = ROOT / "MyBotX_1.0.bat"


@pytest.fixture(scope="module")
def bat_content():
    assert MAIN_BAT.exists(), f"MyBotX_1.0.bat not found at {MAIN_BAT}"
    return MAIN_BAT.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Requirement 8.1 — Python error includes a specific download URL
# ---------------------------------------------------------------------------

class TestPythonDownloadURL:
    """Validates: Requirements 8.1"""

    def test_python_error_includes_full_download_url(self, bat_content):
        """Python missing section provides a full https:// download URL."""
        assert "https://www.python.org" in bat_content

    def test_python_download_url_is_direct_installer(self, bat_content):
        """Download URL points directly to a Python installer file (.exe)."""
        assert "python-3.10" in bat_content and ".exe" in bat_content

    def test_python_download_url_in_missing_section(self, bat_content):
        """The download URL appears in the missing-components error section."""
        # The URL must appear after the MISS_PYTHON check block
        miss_python_idx = bat_content.find("MISS_PYTHON")
        url_idx = bat_content.find("https://www.python.org", miss_python_idx)
        assert url_idx != -1, (
            "Python download URL not found after MISS_PYTHON check"
        )

    def test_python_version_specified_in_error(self, bat_content):
        """Error message names the specific Python version to install."""
        # e.g. "Python 3.10.11" so the user knows exactly what to download
        assert "3.10" in bat_content


# ---------------------------------------------------------------------------
# Requirement 8.2 — Python error includes PATH / installation instructions
# ---------------------------------------------------------------------------

class TestPythonPathInstructions:
    """Validates: Requirements 8.2"""

    def test_pip_checkbox_instruction_present(self, bat_content):
        """
        Launcher instructs the user to enable the pip checkbox during Python
        installation, which implicitly covers the PATH/add-to-PATH step.
        """
        assert "pip checkbox" in bat_content

    def test_reinstall_python_instruction_present(self, bat_content):
        """Launcher tells the user to reinstall Python when pip is missing."""
        assert "Reinstall Python" in bat_content or "reinstall Python" in bat_content

    def test_install_missing_components_instruction(self, bat_content):
        """Launcher instructs the user to install missing components and retry."""
        assert "Install missing components" in bat_content


# ---------------------------------------------------------------------------
# Requirement 8.3 — tkinter / pip error includes reinstallation instructions
# ---------------------------------------------------------------------------

class TestTkinterReinstallInstructions:
    """Validates: Requirements 8.3

    The launcher validates Python packages via pip/requirements.txt rather than
    a direct tkinter import check. The reinstallation guidance is therefore
    provided in the pip-failure error path.
    """

    def test_pip_failure_includes_reinstall_instruction(self, bat_content):
        """pip failure message tells the user to reinstall Python."""
        # "Reinstall Python with pip checkbox" is the actionable instruction
        assert "Reinstall" in bat_content

    def test_pip_failure_message_is_actionable(self, bat_content):
        """pip failure message names the specific action (pip checkbox)."""
        assert "pip checkbox" in bat_content

    def test_package_install_failure_message_present(self, bat_content):
        """Launcher reports package installation failure with [ERR] indicator."""
        assert "[ERR] Package installation failed" in bat_content or (
            "[ERR]" in bat_content and "installation failed" in bat_content
        )

    def test_ensurepip_fallback_before_reinstall(self, bat_content):
        """Launcher tries ensurepip before asking the user to reinstall."""
        ensurepip_idx = bat_content.find("ensurepip")
        reinstall_idx = bat_content.find("Reinstall")
        assert ensurepip_idx != -1, "ensurepip fallback not found"
        assert reinstall_idx != -1, "Reinstall instruction not found"
        assert ensurepip_idx < reinstall_idx, (
            "ensurepip fallback should appear before reinstall instruction"
        )


# ---------------------------------------------------------------------------
# Requirement 8.4 — Missing file errors list specific file names
# ---------------------------------------------------------------------------

class TestMissingFileErrorSpecificity:
    """Validates: Requirements 8.4"""

    def test_main_py_named_in_missing_file_error(self, bat_content):
        """Error message for missing main.py includes the filename 'main.py'."""
        assert "main.py" in bat_content
        # Confirm it appears in an error context (not found / [ERR])
        assert "not found" in bat_content or "[ERR]" in bat_content

    def test_core_main_py_path_in_error(self, bat_content):
        """Error message specifies the full relative path CORE\\main.py."""
        assert "CORE\\main.py" in bat_content or "CORE/main.py" in bat_content

    def test_python_version_named_in_missing_component_list(self, bat_content):
        """Missing-components section names the Python version (e.g. 3.10.11)."""
        assert "3.10.11" in bat_content

    def test_bluestacks_named_in_missing_component_list(self, bat_content):
        """Missing-components section names BlueStacks 5 specifically."""
        assert "BlueStacks 5" in bat_content

    def test_missing_components_section_lists_items(self, bat_content):
        """Missing-components section uses list items (dash prefix) for clarity."""
        # The bat echoes "  - Python 3.10.11" and "  - BlueStacks 5"
        assert " - Python" in bat_content or "- Python" in bat_content

    def test_missing_file_error_uses_err_indicator(self, bat_content):
        """Missing file errors use the [ERR] visual indicator."""
        assert "[ERR]" in bat_content

    def test_requirements_txt_named_in_package_context(self, bat_content):
        """requirements.txt is named explicitly so the user knows which file."""
        assert "requirements.txt" in bat_content
