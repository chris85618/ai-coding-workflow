#!/usr/bin/env python3
"""Sync sonar-project.properties from pyproject.toml [tool.sonar].

Ensures pyproject.toml remains the Single Source of Truth (SSOT).
Flattens nested dictionaries to Sonar's dot notation.
"""

import tomllib
from pathlib import Path
from typing import Any


def flatten_dict(d: dict[str, Any], prefix: str = "") -> dict[str, str]:
    """Recursively flatten a nested dictionary into dot notation."""
    items = {}
    for k, v in d.items():
        new_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key))
        else:
            items[new_key] = str(v)
    return items


def sync_sonar() -> None:
    """Sync Sonar properties from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    props_path = Path("sonar-project.properties")

    if not pyproject_path.exists():
        print("Error: pyproject.toml not found.")
        return

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    sonar_config = data.get("tool", {}).get("sonar", {})
    if not sonar_config:
        print("No [tool.sonar] section found in pyproject.toml. Skipping sync.")
        return

    # Flatten the configuration
    flattened_config = flatten_dict(sonar_config)

    lines = [
        "# This file is AUTO-GENERATED from pyproject.toml [tool.sonar].",
        "# DO NOT EDIT MANUALLY. Automated via git hooks.",
        "",
    ]

    for key, value in flattened_config.items():
        prop_key = f"sonar.{key}" if not key.startswith("sonar.") else key
        lines.append(f"{prop_key}={value}")

    with open(props_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Successfully synced {props_path} from pyproject.toml.")


if __name__ == "__main__":
    sync_sonar()
