"""Tests for config loader."""

import os
from typing import Any

import pytest

from agentic_workflow.frameworks.config import (
    WorkflowConfig,
    _interpolate_env_vars,
    load_config,
)


def test_load_config_success(tmp_path: Any) -> None:
    """TC-071: Load valid config file successfully."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
models:
  reasoning:
    provider: "anthropic"
    name: "claude-3-opus"
    temperature: 0.7
prompts:
  agent_alpha:
    system: "sys"
    task_template: "task"
sonarcloud:
  feedback:
    auto_convert_to_debt: true
    default_debt_priority: "P2"
  on_missing_config: "warn_and_disable"
    """
    )
    config = load_config(str(config_file))
    assert isinstance(config, WorkflowConfig)
    assert config.models["reasoning"].provider == "anthropic"


def test_interpolate_env_vars_recursive() -> None:
    """TC-074: Test interpolation helper with various types."""
    os.environ["VAR_X"] = "val_x"
    data = {"a": "${VAR_X}", "b": ["${VAR_X}", 123], "c": {"d": "${VAR_X}"}}
    result = _interpolate_env_vars(data)
    assert result["a"] == "val_x"
    assert result["b"] == ["val_x", 123]
    assert result["c"]["d"] == "val_x"
    assert result["b"][1] == 123  # Trigger non-str/dict/list branch


def test_load_config_not_found() -> None:
    """TC-072: Raise error if config file not found."""
    with pytest.raises(FileNotFoundError):
        load_config("does_not_exist_xyz123.yaml")
