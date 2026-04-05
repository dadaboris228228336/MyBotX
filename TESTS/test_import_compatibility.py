"""
Integration tests for import compatibility after project restructuring.
Validates: Requirements 9.1, 9.2, 9.3, 9.4
"""

import sys
import importlib
import tempfile
import json
from pathlib import Path

import pytest

# Path to CORE (current location of the project files)
CORE_DIR = Path(__file__).parent.parent / "CORE"


# ---------------------------------------------------------------------------
# 6.1 Test that main.py can import dependency_checker
# Validates: Requirements 9.1, 9.2
# ---------------------------------------------------------------------------

def test_dependency_checker_importable_from_core():
    """
    Verify that dependency_checker can be imported when sys.path includes CORE/.
    This simulates the import resolution that main.py performs via sys.path.insert().
    """
    if str(CORE_DIR) not in sys.path:
        sys.path.insert(0, str(CORE_DIR))

    try:
        import dependency_checker
        assert hasattr(dependency_checker, "DependencyChecker"), (
            "DependencyChecker class not found in dependency_checker module"
        )
    except ImportError as e:
        pytest.fail(f"Failed to import dependency_checker: {e}")


def test_main_py_has_sys_path_fallback():
    """
    Verify that main.py contains a sys.path.insert fallback for import resolution.
    This ensures imports work regardless of working directory.
    Validates: Requirements 9.1, 9.2
    """
    main_py = CORE_DIR / "main.py"
    assert main_py.exists(), "main.py not found in CORE/"
    content = main_py.read_text(encoding="utf-8")
    assert "sys.path.insert" in content, (
        "main.py is missing sys.path.insert() fallback for import resolution"
    )
    assert "Path(__file__).parent" in content, (
        "main.py should use Path(__file__).parent for path resolution"
    )


# ---------------------------------------------------------------------------
# 6.2 Test that application can locate requirements.txt
# Validates: Requirements 9.3
# ---------------------------------------------------------------------------

def test_requirements_txt_path_uses_file_parent():
    """
    Verify that main.py resolves requirements.txt relative to __file__,
    not relative to the working directory.
    Validates: Requirements 9.3
    """
    main_py = CORE_DIR / "main.py"
    content = main_py.read_text(encoding="utf-8")
    # main.py should use Path(__file__).parent / "requirements.txt"
    assert 'Path(__file__).parent' in content and 'requirements.txt' in content, (
        "main.py should resolve requirements.txt using Path(__file__).parent"
    )


def test_requirements_txt_exists_in_core():
    """requirements.txt must exist alongside main.py in CORE/."""
    req = CORE_DIR / "requirements.txt"
    assert req.exists(), f"requirements.txt not found at {req}"


# ---------------------------------------------------------------------------
# 6.3 Test that application can locate config.json
# Validates: Requirements 9.4
# ---------------------------------------------------------------------------

def test_config_json_exists():
    """config.json must exist in the CONFIG/ directory."""
    config = Path(__file__).parent.parent / "CONFIG" / "config.json"
    assert config.exists(), f"config.json not found at {config}"


def test_config_json_is_valid_json():
    """config.json must be valid JSON."""
    config_path = Path(__file__).parent.parent / "CONFIG" / "config.json"
    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict), "config.json root must be a JSON object"
    except json.JSONDecodeError as e:
        pytest.fail(f"config.json is not valid JSON: {e}")


# ---------------------------------------------------------------------------
# 6.4 Integration test: all file paths resolve correctly
# Validates: Requirements 9.1, 9.2, 9.3, 9.4
# ---------------------------------------------------------------------------

def test_all_required_files_present_in_core():
    """
    All files required for the application to run must exist in CORE/.
    Validates: Requirements 9.1, 9.2, 9.3
    """
    required = ["main.py", "dependency_checker.py", "requirements.txt"]
    missing = [f for f in required if not (CORE_DIR / f).exists()]
    assert not missing, f"Missing required files in CORE/: {missing}"


def test_dependency_checker_uses_relative_path():
    """
    dependency_checker.py should accept a requirements_file parameter
    so it can resolve the file relative to its own location.
    Validates: Requirements 9.3
    """
    dep_checker = CORE_DIR / "dependency_checker.py"
    content = dep_checker.read_text(encoding="utf-8")
    assert "requirements_file" in content, (
        "DependencyChecker should accept a requirements_file parameter"
    )
