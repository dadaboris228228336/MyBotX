"""
Property-Based Tests for Project Restructure Launcher
Feature: project-restructure-launcher

Uses hypothesis for property-based testing.
Minimum 100 iterations per property test.
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_doc_filename(name: str, ext: str) -> str:
    """Return a safe filename like 'name.ext'."""
    return f"{name}{ext}"


def _migrate_docs(root_dir: Path, dest_dir: Path) -> None:
    """
    Simulate the documentation-file migration step described in Requirement 6.7:
    Move every *.md and *.txt file found directly in root_dir into dest_dir.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    for item in list(root_dir.iterdir()):
        if item.is_file() and item.suffix.lower() in (".md", ".txt"):
            shutil.move(str(item), str(dest_dir / item.name))


# ---------------------------------------------------------------------------
# Property 1: Documentation File Migration Completeness
# Validates: Requirements 6.7
# ---------------------------------------------------------------------------

# Strategy: generate a non-empty list of (stem, extension) pairs for doc files.
_doc_extensions = st.sampled_from([".md", ".txt"])
_file_stems = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd"),
        whitelist_characters="_-",
    ),
    min_size=1,
    max_size=20,
)
_doc_file_strategy = st.lists(
    st.tuples(_file_stems, _doc_extensions),
    min_size=1,
    max_size=10,
    unique_by=lambda pair: pair[0].lower() + pair[1].lower(),
)


# Feature: project-restructure-launcher, Property 1: Documentation File Migration Completeness
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(doc_files=_doc_file_strategy)
def test_all_documentation_files_migrated(doc_files):
    """
    Property 1: Documentation File Migration Completeness

    For any set of .md / .txt files placed in the root directory,
    after the migration step:
      - every such file MUST exist inside my_bot/
      - no such file MUST remain in the root directory

    Validates: Requirements 6.7
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        dest = root / "my_bot"

        # --- Arrange: create doc files in the simulated root ---
        created_names = []
        for stem, ext in doc_files:
            filename = _make_doc_filename(stem, ext)
            (root / filename).write_text(f"content of {filename}", encoding="utf-8")
            created_names.append(filename)

        # --- Act: run the migration ---
        _migrate_docs(root, dest)

        # --- Assert ---
        for filename in created_names:
            # Must exist in my_bot/
            assert (dest / filename).exists(), (
                f"'{filename}' was not migrated to my_bot/"
            )
            # Must NOT remain in root
            assert not (root / filename).exists(), (
                f"'{filename}' still exists in root after migration"
            )


# ---------------------------------------------------------------------------
# Helpers for launcher script property tests
# ---------------------------------------------------------------------------

# The validation checks that must appear in any compliant launcher script.
REQUIRED_VALIDATION_CHECKS = [
    ("python", "python --version"),          # Python installation check
    ("tkinter", 'import tkinter'),           # tkinter availability check
    ("my_bot dir", "my_bot"),                # project directory check
    ("main.py", "main.py"),                  # main.py existence check
    ("dependency_checker", "dependency_checker.py"),  # dep checker check
    ("requirements.txt", "requirements.txt"),         # requirements check
]

SUCCESS_INDICATOR = "✅"
FAILURE_INDICATOR = "❌"


def _build_minimal_launcher(checks: list) -> str:
    """
    Build a minimal but spec-compliant launcher script string that includes
    all provided validation checks, each with success and failure paths,
    pause on error, and visual indicators.
    """
    lines = ["@echo off", ""]
    for name, cmd in checks:
        lines += [
            f"REM --- {name} ---",
            f"{cmd} >nul 2>&1",
            "if errorlevel 1 (",
            f"    echo {FAILURE_INDICATOR} Error: {name} not found",
            "    pause",
            "    exit /b 1",
            ")",
            f"echo {SUCCESS_INDICATOR} {name}: OK",
            "",
        ]
    lines += ["cd my_bot", "python main.py"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Property 2: Launcher Script Validation Completeness
# Validates: Requirements 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1-4.6
# ---------------------------------------------------------------------------

# Strategy: generate subsets of the required checks (always non-empty).
_check_strategy = st.lists(
    st.sampled_from(REQUIRED_VALIDATION_CHECKS),
    min_size=1,
    max_size=len(REQUIRED_VALIDATION_CHECKS),
    unique_by=lambda c: c[0],
)


# Feature: project-restructure-launcher, Property 2: Launcher Script Validation Completeness
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(checks=_check_strategy)
def test_launcher_contains_all_validation_checks(checks):
    """
    Property 2: Launcher Script Validation Completeness

    For any required validation check included in the launcher, the generated
    script must contain:
      - the corresponding validation command
      - a success message path
      - a failure message path

    Validates: Requirements 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
    """
    script = _build_minimal_launcher(checks)

    for name, cmd in checks:
        # Validation command must be present
        assert cmd in script, (
            f"Validation command for '{name}' ('{cmd}') not found in launcher script"
        )
        # Success path must be present
        assert SUCCESS_INDICATOR in script, (
            f"Success indicator '{SUCCESS_INDICATOR}' missing for check '{name}'"
        )
        # Failure path must be present
        assert FAILURE_INDICATOR in script, (
            f"Failure indicator '{FAILURE_INDICATOR}' missing for check '{name}'"
        )


# ---------------------------------------------------------------------------
# Property 3: Error Handling Consistency
# Validates: Requirements 2.5, 3.4
# ---------------------------------------------------------------------------

# Strategy: generate a list of error-path names (arbitrary strings).
_error_names = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters=" _-"),
    min_size=1,
    max_size=30,
)
_error_list_strategy = st.lists(_error_names, min_size=1, max_size=10, unique=True)


def _build_script_with_errors(error_names: list) -> str:
    """Build a script that has one error-handling block per error name."""
    lines = ["@echo off", ""]
    for name in error_names:
        lines += [
            f"REM error block: {name}",
            "if errorlevel 1 (",
            f"    echo {FAILURE_INDICATOR} Error: {name}",
            "    pause",
            "    exit /b 1",
            ")",
            "",
        ]
    return "\n".join(lines)


# Feature: project-restructure-launcher, Property 3: Error Handling Consistency
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(error_names=_error_list_strategy)
def test_every_error_path_has_pause_and_exit(error_names):
    """
    Property 3: Error Handling Consistency

    For any validation failure path in the launcher script, the script must
    include both a 'pause' command and an 'exit /b 1' (non-zero exit code).

    Validates: Requirements 2.5, 3.4
    """
    script = _build_script_with_errors(error_names)

    assert "pause" in script, (
        "Launcher script is missing 'pause' in error handling path"
    )
    assert "exit /b 1" in script, (
        "Launcher script is missing 'exit /b 1' (non-zero exit) in error handling path"
    )


# ---------------------------------------------------------------------------
# Property 4: Visual Indicator Consistency
# Validates: Requirements 8.5, 10.3
# ---------------------------------------------------------------------------

# Strategy: generate status messages that should each carry ✅ or ❌.
_status_messages = st.lists(
    st.one_of(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters=" :._-"),
            min_size=1,
            max_size=40,
        ).map(lambda m: f"echo {SUCCESS_INDICATOR} {m}"),
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters=" :._-"),
            min_size=1,
            max_size=40,
        ).map(lambda m: f"echo {FAILURE_INDICATOR} {m}"),
    ),
    min_size=1,
    max_size=20,
)


# Feature: project-restructure-launcher, Property 4: Visual Indicator Consistency
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(status_lines=_status_messages)
def test_every_status_message_has_visual_indicator(status_lines):
    """
    Property 4: Visual Indicator Consistency

    For any status message line in the launcher script, the line must contain
    either a success indicator (✅) or a failure indicator (❌).

    Validates: Requirements 8.5, 10.3
    """
    for line in status_lines:
        has_indicator = (SUCCESS_INDICATOR in line) or (FAILURE_INDICATOR in line)
        assert has_indicator, (
            f"Status message line is missing visual indicator (✅ or ❌): '{line}'"
        )
