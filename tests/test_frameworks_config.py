"""Tests for config loader."""
import pytest
from pathlib import Path
from agentic_workflow.frameworks.config import load_config, WorkflowConfig

def test_load_config_success(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text('''
models:
  reasoning:
    provider: "anthropic"
    name: "claude-3-opus"
    temperature: 0.7
prompts:
  agent_alpha:
    system: "sys"
    task_template: "task"
    ''')
    config = load_config(str(config_file))
    assert isinstance(config, WorkflowConfig)
    assert config.models["reasoning"].provider == "anthropic"

def test_load_config_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("does_not_exist_xyz123.yaml")
