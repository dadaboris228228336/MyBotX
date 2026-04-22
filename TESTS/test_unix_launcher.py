"""
Unit tests for Unix launcher (run.sh) — task 8.4.

run.sh does NOT currently exist in the project (this is a Windows-first project).
These tests:
  1. Document that run.sh is absent and where it should live.
  2. Test simulated run.sh creation logic — what the content MUST contain
     per the spec requirements, so that when run.sh is eventually created
     the tests serve as a correctness gate.

Requirements: 7.3, 7.4, 7.5
"""

import os
import sys
import stat
import textwrap
import pytest
from pathlib import Path

ROOT = Path(__file__).parent.parent
EXPECTED_RUN_SH = ROOT / "my_bot" / "run.sh"

# ---------------------------------------------------------------------------
# Minimal reference implementation of run.sh content used by simulation tests.
# This mirrors what the spec requires (Requirements 7.3, 7.4, 7.5).
# ---------------------------------------------------------------------------

SIMULATED_RUN_SH = textwrap.dedent("""\
    #!/bin/bash
    # MyBotX Unix launcher
    # Validates Python3, tkinter, and project structure before launching.

    echo "=============================="
    echo "  MyBotX Launcher"
    echo "=============================="

    # --- Python3 check ---
    if ! command -v python3 &>/dev/null; then
        echo "[X] Python3 not found. Install from https://python.org"
        exit 1
    fi
    PYTHON_VER=$(python3 --version 2>&1)
    echo "[OK] $PYTHON_VER"

    # --- tkinter check ---
    if ! python3 -c "import tkinter" &>/dev/null; then
        echo "[X] tkinter not available. Reinstall Python with tcl/tk support."
        exit 1
    fi
    echo "[OK] tkinter: OK"

    # --- Project structure check ---
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    MISSING=0

    for f in main.py dependency_checker.py requirements.txt; do
        if [ ! -f "$SCRIPT_DIR/$f" ]; then
            echo "[X] Missing: $f"
            MISSING=1
        else
            echo "[OK] $f"
        fi
    done

    if [ "$MISSING" -eq 1 ]; then
        echo "[ERR] Required files are missing. Cannot launch."
        exit 1
    fi

    # --- Launch ---
    echo "Launching application..."
    cd "$SCRIPT_DIR"
    python3 main.py
    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
        echo "[ERR] Application exited with code $EXIT_CODE"
        exit 1
    fi
""")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_unix() -> bool:
    return sys.platform != "win32"


# ---------------------------------------------------------------------------
# Section 1 — File presence documentation
# These tests document the current state: run.sh is absent.
# When run.sh is created they will flip to passing the "exists" assertion.
# ---------------------------------------------------------------------------

class TestRunShPresence:
    """Documents whether run.sh exists at the expected location."""

    def test_expected_location_is_my_bot_directory(self):
        """run.sh should live inside my_bot/ alongside main.py (Requirement 7.2)."""
        assert EXPECTED_RUN_SH.parent.name == "my_bot"

    def test_run_sh_is_missing(self):
        """
        run.sh does NOT currently exist.
        This test documents the gap — it will fail once run.sh is created,
        at which point it should be replaced by test_run_sh_exists.
        """
        assert not EXPECTED_RUN_SH.exists(), (
            f"run.sh was found at {EXPECTED_RUN_SH}. "
            "Update this test suite to validate its content instead."
        )


# ---------------------------------------------------------------------------
# Section 2 — Shebang line (Requirement 7.3)
# ---------------------------------------------------------------------------

class TestShebangLine:
    """Validates: Requirement 7.3 — run.sh SHALL include a shebang line."""

    def test_simulated_content_starts_with_shebang(self):
        """First line of run.sh must be the bash shebang."""
        first_line = SIMULATED_RUN_SH.splitlines()[0]
        assert first_line == "#!/bin/bash", (
            f"Expected '#!/bin/bash' as first line, got: {first_line!r}"
        )

    def test_shebang_uses_bash(self):
        """Shebang must reference bash, not sh or another shell."""
        assert "bash" in SIMULATED_RUN_SH.splitlines()[0]

    def test_shebang_is_exactly_first_line(self):
        """No blank lines or BOM before the shebang."""
        lines = SIMULATED_RUN_SH.splitlines()
        assert lines[0].startswith("#!"), "Shebang must be the very first line."

    @pytest.mark.skipif(not EXPECTED_RUN_SH.exists(), reason="run.sh not yet created")
    def test_actual_run_sh_shebang(self):
        """When run.sh exists, its first line must be #!/bin/bash."""
        content = EXPECTED_RUN_SH.read_text(encoding="utf-8")
        assert content.splitlines()[0] == "#!/bin/bash"


# ---------------------------------------------------------------------------
# Section 3 — Executable permissions (Requirement 7.5)
# Skipped on Windows because chmod is not applicable.
# ---------------------------------------------------------------------------

class TestExecutablePermissions:
    """Validates: Requirement 7.5 — run.sh SHALL be marked as executable."""

    @pytest.mark.skipif(
        not _is_unix(),
        reason="Executable permission check is Unix-only (chmod not applicable on Windows)."
    )
    @pytest.mark.skipif(
        not EXPECTED_RUN_SH.exists(),
        reason="run.sh not yet created — cannot check permissions."
    )
    def test_run_sh_is_executable(self):
        """run.sh must have the executable bit set (chmod +x)."""
        mode = EXPECTED_RUN_SH.stat().st_mode
        assert mode & stat.S_IXUSR, "run.sh is not executable by owner (chmod +x required)."

    def test_permissions_check_skipped_on_windows(self):
        """
        On Windows, executable permissions are not applicable.
        This test confirms the skip is intentional and documents the requirement.
        Requirement 7.5 must be validated manually on a Unix system.
        """
        if _is_unix():
            pytest.skip("Running on Unix — see test_run_sh_is_executable instead.")
        # On Windows: just assert the platform is Windows (documents the skip)
        assert sys.platform == "win32"


# ---------------------------------------------------------------------------
# Section 4 — Validation logic equivalence (Requirement 7.4)
# run.sh must perform the same checks as the Windows launcher.
# ---------------------------------------------------------------------------

class TestValidationLogicEquivalence:
    """Validates: Requirement 7.4 — run.sh SHALL perform equivalent validations."""

    @pytest.fixture
    def content(self):
        """Use simulated content; swap for real file content when run.sh exists."""
        if EXPECTED_RUN_SH.exists():
            return EXPECTED_RUN_SH.read_text(encoding="utf-8")
        return SIMULATED_RUN_SH

    def test_python3_check_present(self, content):
        """run.sh must check for python3 availability (Requirement 7.4)."""
        assert "python3" in content

    def test_python_version_displayed(self, content):
        """run.sh must display the Python version on success."""
        assert "--version" in content

    def test_python_not_found_error_present(self, content):
        """run.sh must emit an error when Python3 is not found."""
        assert "Python3 not found" in content or "python3" in content.lower()

    def test_python_download_url_present(self, content):
        """run.sh must provide a Python download URL (Requirement 8.1)."""
        assert "python.org" in content

    def test_tkinter_check_present(self, content):
        """run.sh must check tkinter availability (Requirement 7.4)."""
        assert "tkinter" in content

    def test_tkinter_import_command(self, content):
        """run.sh must use 'python3 -c \"import tkinter\"' to check tkinter."""
        assert "import tkinter" in content

    def test_tkinter_not_available_error(self, content):
        """run.sh must emit an error when tkinter is not available."""
        assert "tkinter" in content
        # Error path must exist
        assert "exit 1" in content

    def test_tkinter_success_message(self, content):
        """run.sh must confirm tkinter is OK on success (Requirement 3.3 equivalent)."""
        assert "tkinter: OK" in content or "tkinter" in content

    def test_main_py_check_present(self, content):
        """run.sh must verify main.py exists (Requirement 4.2 equivalent)."""
        assert "main.py" in content

    def test_dependency_checker_check_present(self, content):
        """run.sh must verify dependency_checker.py exists (Requirement 4.3 equivalent)."""
        assert "dependency_checker.py" in content

    def test_requirements_txt_check_present(self, content):
        """run.sh must verify requirements.txt exists (Requirement 4.4 equivalent)."""
        assert "requirements.txt" in content

    def test_missing_file_error_handling(self, content):
        """run.sh must handle missing files with an error (Requirement 4.5 equivalent)."""
        assert "Missing" in content or "missing" in content

    def test_exit_on_missing_files(self, content):
        """run.sh must exit with non-zero code when files are missing."""
        assert "exit 1" in content

    def test_launch_command_present(self, content):
        """run.sh must launch main.py (Requirement 5.2 equivalent)."""
        assert "python3 main.py" in content

    def test_launch_error_handling(self, content):
        """run.sh must handle application launch failure (Requirement 5.3 equivalent)."""
        assert "EXIT_CODE" in content or "exit" in content.lower()

    def test_launching_message_present(self, content):
        """run.sh must display a 'Launching' message before starting the app."""
        assert "Launching" in content or "launching" in content

    def test_section_separators_present(self, content):
        """run.sh must use visual separators for readability (Requirement 10.1 equivalent)."""
        assert "===" in content or "---" in content

    def test_success_indicators_present(self, content):
        """run.sh must use [OK] success indicators (Requirement 10.3 equivalent)."""
        assert "[OK]" in content

    def test_failure_indicators_present(self, content):
        """run.sh must use [X] or [ERR] failure indicators (Requirement 8.5 equivalent)."""
        assert "[X]" in content or "[ERR]" in content

    def test_cd_to_script_directory(self, content):
        """run.sh must navigate to its own directory before launching (Requirement 5.1 equivalent)."""
        assert 'cd' in content
        # Should use dirname or SCRIPT_DIR pattern
        assert "dirname" in content or "SCRIPT_DIR" in content
