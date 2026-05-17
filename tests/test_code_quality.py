"""Tests for codebase quality using Ruff and Mypy.

Traceable to: FR-QUALITY-001, FR-QUALITY-002
"""

import pathlib
import subprocess
import sys

# Load tomllib (Python 3.11+) or tomli for compatibility
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


def _load_target_paths() -> list[str]:
    """Load target paths from pyproject.toml configuration."""
    pyproject_path = pathlib.Path(__file__).parent.parent / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            config = tomllib.load(f)
            # Try to load target paths from [tool.ruff] src definition
            ruff_src = config.get("tool", {}).get("ruff", {}).get("src")
            if isinstance(ruff_src, list):
                return [str(p) for p in ruff_src]
    # Fallback default if config parsing fails
    return ["src", "tests"]


def test_ruff_linting() -> None:
    """TC-QUALITY-001: Verify Ruff check reports zero warnings and passes successfully."""
    paths = _load_target_paths()
    cmd = [sys.executable, "-m", "ruff", "check"] + paths
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    # Assert on both exit code and success indicator in stdout
    assert result.returncode == 0, (
        f"Ruff check failed with exit code {result.returncode}.\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
    )
    assert "All checks passed!" in result.stdout or not result.stdout, (
        f"Ruff linting found violations:\n{result.stdout}"
    )


def test_mypy_type_safety() -> None:
    """TC-QUALITY-002: Verify Mypy type-checking reports zero issues and passes successfully."""
    paths = _load_target_paths()
    cmd = [sys.executable, "-m", "mypy"] + paths
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    # Assert on both exit code and success indicator in stdout
    assert result.returncode == 0, (
        f"Mypy check failed with exit code {result.returncode}.\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
    )

    assert "Success: no issues found" in result.stdout, f"Mypy found type safety violations:\n{result.stdout}"
