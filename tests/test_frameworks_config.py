"""Tests for config loader."""

from typing import Any

import pytest

from agentic_workflow.frameworks.config import WorkflowConfig, load_config


def test_load_config_success(tmp_path: Any) -> None:
    """TC-071: Load valid config file successfully."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
models:
  reasoning:
    provider: "anthropic"
    name: "claude-3-opus"
    temperature: 0.7
prompts:
  agent_alpha:
    system: "sys"
    task_template: "task"
    """)
    config = load_config(str(config_file))
    assert isinstance(config, WorkflowConfig)
    assert config.models["reasoning"].provider == "anthropic"


def test_load_config_not_found() -> None:
    """TC-072: Raise error if config file not found."""
    with pytest.raises(FileNotFoundError):
        load_config("does_not_exist_xyz123.yaml")
