"""Tests for config loader."""

import os
from typing import Any

import pytest

from agentic_workflow.frameworks.config import (
    WorkflowConfig,
    WorkflowConfigLoader,
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
    config = WorkflowConfigLoader.load(str(config_file))
    assert isinstance(config, WorkflowConfig)
    assert config.models["reasoning"].provider == "anthropic"


def test_interpolate_env_vars_recursive() -> None:
    """TC-074: Test interpolation helper with various types."""
    os.environ["VAR_X"] = "val_x"
    data = {"a": "${VAR_X}", "b": ["${VAR_X}", 123], "c": {"d": "${VAR_X}"}}
    result = WorkflowConfigLoader._interpolate_env_vars(data)
    assert result["a"] == "val_x"
    assert result["b"] == ["val_x", 123]
    assert result["c"]["d"] == "val_x"
    assert result["b"][1] == 123  # Trigger non-str/dict/list branch


def test_load_config_not_found() -> None:
    """TC-072: Raise error if config file not found."""
    with pytest.raises(FileNotFoundError):
        WorkflowConfigLoader.load("does_not_exist_xyz123.yaml")


class TestFrameworksSonarCloudConfig:
    """Branch coverage for frameworks.config.SonarCloudConfig."""

    def test_is_valid_true_when_all_fields_set(self) -> None:
        """Line 64: is_valid returns True when token, key, org present."""
        from agentic_workflow.frameworks.config import SonarCloudConfig

        cfg = SonarCloudConfig(token="tok", project_key="key", organization="org")
        assert cfg.is_valid is True

    def test_is_valid_false_when_fields_missing(self) -> None:
        """Line 64: is_valid returns False when fields are absent."""
        from agentic_workflow.frameworks.config import SonarCloudConfig

        cfg = SonarCloudConfig()
        assert cfg.is_valid is False

    def test_missing_vars_all_missing(self) -> None:
        """Lines 69-76: missing_vars lists all three when all absent."""
        from agentic_workflow.frameworks.config import SonarCloudConfig

        cfg = SonarCloudConfig()
        missing = cfg.missing_vars
        assert "SONAR_TOKEN" in missing
        assert "SONAR_PROJECT_KEY" in missing
        assert "SONAR_ORGANIZATION" in missing

    def test_missing_vars_empty_when_all_set(self) -> None:
        """Lines 69-76: missing_vars is empty when all fields provided."""
        from agentic_workflow.frameworks.config import SonarCloudConfig

        cfg = SonarCloudConfig(token="tok", project_key="key", organization="org")
        assert cfg.missing_vars == []


class TestCoerceValueExceptBranch:
    """Branch coverage for _coerce_value except block (lines 47-48)."""

    def test_attribute_error_returns_raw_string(self) -> None:
        """Lines 47-48: AttributeError on .replace → returns raw value."""
        from agentic_workflow.adapters.sonarcloud.sonar_adapter import _coerce_value

        # Pass an object with no .replace — triggers AttributeError,
        # falls through except and returns the original value unchanged.
        class _NoReplace:
            pass

        raw = _NoReplace()
        result = _coerce_value(raw)  # type: ignore[arg-type]
        assert result is raw  # type: ignore[comparison-overlap]
