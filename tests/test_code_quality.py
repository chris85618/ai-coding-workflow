"""Tests for codebase quality using Ruff and Mypy.

Traceable to: FR-QUALITY-001, FR-QUALITY-002
"""

import subprocess
import sys


def test_ruff_linting() -> None:
    """TC-QUALITY-001: Verify that Ruff check passes with zero warnings."""
    cmd = [sys.executable, "-m", "ruff", "check", "src", "tests"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 0, (
        f"Ruff check failed with exit code {result.returncode}.\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
    )


def test_mypy_type_safety() -> None:
    """TC-QUALITY-002: Verify that Mypy type check passes with zero errors."""
    cmd = [
        sys.executable,
        "-m",
        "mypy",
        "src",
        "tests",
        "--ignore-missing-imports",
        "--explicit-package-bases",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 0, (
        f"Mypy type check failed with exit code {result.returncode}.\n"
        f"Stdout:\n{result.stdout}\n"
        f"Stderr:\n{result.stderr}"
    )
