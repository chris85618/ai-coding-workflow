#!/usr/bin/env python3
"""Install Git hooks for the project.

Automates the synchronization of generated files.
"""

import os
from pathlib import Path


def install_hooks():
    git_dir = Path(".git")
    if not git_dir.exists():
        print("Error: .git directory not found. Are you in the root of a git repository?")
        return

    hooks_dir = git_dir / "hooks"
    pre_commit_path = hooks_dir / "pre-commit"

    # Hook content
    hook_content = """#!/bin/sh
# Git Pre-commit Hook: Format code and Sync SonarCloud properties
echo "Running ruff format..."
python -m ruff format src tests

echo "Checking configuration sync..."
python scripts/sync_sonar_props.py
"""

    with open(pre_commit_path, "w", encoding="utf-8") as f:
        f.write(hook_content)

    # Make executable (compatible with Unix-like systems, for Windows we rely on git bash)
    try:
        os.chmod(pre_commit_path, 0o755)
    except Exception:
        pass

    print(f"Successfully installed pre-commit hook to {pre_commit_path}")


if __name__ == "__main__":
    install_hooks()
