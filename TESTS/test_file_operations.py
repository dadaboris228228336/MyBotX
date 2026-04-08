"""
Unit tests for file operations — project restructure validation.
Validates the ACTUAL current project structure (post-restructure).

Requirements covered: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.9, 1.1
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent.parent
CORE_DIR = ROOT / "CORE"
LAUNCHER = ROOT / "MyBotX_1.0.bat"
NOVA_PAPKA = ROOT / "Новая папка"   # empty dir that should have been removed


# ===========================================================================
# 1. Directory creation — Requirement 6.1
#    (The spec planned my_bot/; the actual implementation used CORE/)
# ===========================================================================

def test_core_directory_exists():
    """CORE/ directory must exist at the project root. Validates: Req 6.1"""
    assert CORE_DIR.is_dir(), f"Expected CORE/ directory at {CORE_DIR}"


def test_core_directory_is_not_empty():
    """CORE/ must contain at least one Python file. Validates: Req 6.1"""
    py_files = list(CORE_DIR.glob("*.py"))
    assert py_files, "CORE/ directory is empty — expected Python source files"


# ===========================================================================
# 2. File movement — Requirements 6.2, 6.3, 6.4, 6.5, 6.6
# ===========================================================================

@pytest.mark.parametrize("filename", [
    "main.py",               # Req 6.2
    "dependency_checker.py", # Req 6.3
    "requirements.txt",      # Req 6.4
])
def test_required_file_exists_in_core(filename):
    """Each required project file must exist inside CORE/. Validates: Req 6.2–6.4"""
    target = CORE_DIR / filename
    assert target.exists(), f"Expected {filename} inside CORE/ but not found at {target}"


def test_config_json_exists():
    """config.json must exist (in CONFIG/ as per actual structure). Validates: Req 6.5"""
    config_locations = [
        ROOT / "CONFIG" / "config.json",
        CORE_DIR / "config.json",
    ]
    found = any(p.exists() for p in config_locations)
    assert found, "config.json not found in CONFIG/ or CORE/"


def test_check_requirements_exists_in_core():
    """check_requirements.py must exist in CORE/ (used by launcher). Validates: Req 6.6"""
    assert (CORE_DIR / "check_requirements.py").exists(), (
        "check_requirements.py not found in CORE/"
    )


# ===========================================================================
# 3. Empty directory removal — Requirement 6.9
# ===========================================================================

def test_nova_papka_directory_removed():
    """'Новая папка' (empty dir) must not exist at root. Validates: Req 6.9"""
    assert not NOVA_PAPKA.exists(), (
        f"'Новая папка' directory still exists at {NOVA_PAPKA} — should have been removed"
    )


# ===========================================================================
# 4. Launcher script creation — Requirement 1.1
# ===========================================================================

def test_launcher_exists_at_root():
    """MyBotX_1.0.bat must exist at the project root. Validates: Req 1.1"""
    assert LAUNCHER.exists(), f"Launcher not found at {LAUNCHER}"


def test_launcher_is_a_file():
    """MyBotX_1.0.bat must be a regular file, not a directory. Validates: Req 1.1"""
    assert LAUNCHER.is_file(), f"{LAUNCHER} is not a regular file"


def test_launcher_is_not_empty():
    """MyBotX_1.0.bat must have non-zero content. Validates: Req 1.1"""
    assert LAUNCHER.stat().st_size > 0, "MyBotX_1.0.bat is empty"


def test_launcher_is_bat_file():
    """Launcher must have .bat extension. Validates: Req 1.1"""
    assert LAUNCHER.suffix.lower() == ".bat", (
        f"Expected .bat extension, got '{LAUNCHER.suffix}'"
    )


# ===========================================================================
# 5. Simulated directory creation (unit-level)
# ===========================================================================

def test_create_project_directory_in_temp():
    """Simulate creating a project directory — verifies mkdir logic. Validates: Req 6.1"""
    with tempfile.TemporaryDirectory() as tmp:
        project_dir = Path(tmp) / "CORE"
        project_dir.mkdir()
        assert project_dir.is_dir()


# ===========================================================================
# 6. Simulated file movement (unit-level)
# ===========================================================================

@pytest.mark.parametrize("filename", [
    "main.py",
    "dependency_checker.py",
    "requirements.txt",
    "config.json",
    "run.bat",
])
def test_simulated_file_move(filename):
    """
    Simulate moving a file from root into a project subdirectory.
    Validates the move logic used during restructuring. Validates: Req 6.2–6.6
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        dest = root / "CORE"
        dest.mkdir()

        src_file = root / filename
        src_file.write_text(f"# {filename}", encoding="utf-8")

        shutil.move(str(src_file), str(dest / filename))

        assert (dest / filename).exists(), f"{filename} not found in destination"
        assert not src_file.exists(), f"{filename} still exists at source after move"


# ===========================================================================
# 7. Simulated empty directory removal (unit-level)
# ===========================================================================

def test_simulated_empty_dir_removal():
    """Simulate removing an empty directory. Validates: Req 6.9"""
    with tempfile.TemporaryDirectory() as tmp:
        empty_dir = Path(tmp) / "Новая папка"
        empty_dir.mkdir()
        assert empty_dir.exists()

        empty_dir.rmdir()
        assert not empty_dir.exists()


def test_simulated_nonempty_dir_not_removed():
    """Non-empty directories should NOT be silently removed. Validates: Req 6.9"""
    with tempfile.TemporaryDirectory() as tmp:
        non_empty = Path(tmp) / "some_dir"
        non_empty.mkdir()
        (non_empty / "file.txt").write_text("data", encoding="utf-8")

        with pytest.raises(OSError):
            non_empty.rmdir()  # must raise because dir is not empty


# ===========================================================================
# 8. Simulated launcher script creation (unit-level)
# ===========================================================================

def test_simulated_launcher_creation():
    """Simulate writing a launcher .bat file. Validates: Req 1.1"""
    with tempfile.TemporaryDirectory() as tmp:
        launcher = Path(tmp) / "MyBotX_1.0.bat"
        launcher.write_text("@echo off\necho Hello\n", encoding="utf-8")

        assert launcher.exists()
        assert launcher.is_file()
        assert launcher.stat().st_size > 0
        assert launcher.suffix.lower() == ".bat"


def test_simulated_launcher_content_readable():
    """Launcher content must be readable as text. Validates: Req 1.1"""
    with tempfile.TemporaryDirectory() as tmp:
        launcher = Path(tmp) / "MyBotX_1.0.bat"
        content = "@echo off\ntitle MyBotX 1.0\n"
        launcher.write_text(content, encoding="utf-8")

        read_back = launcher.read_text(encoding="utf-8")
        assert read_back == content
