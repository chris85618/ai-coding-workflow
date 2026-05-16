"""BDD step definitions for configuration interpolation."""

import os
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from agentic_workflow.frameworks.config import WorkflowConfigLoader

scenarios("features/config_interpolation.feature")


@pytest.fixture
def config_file(tmp_path: Any) -> str:
    """Fixture to provide a temporary config file path."""
    return str(tmp_path / "config_test.yaml")


@given(
    parsers.parse('a configuration file with "{placeholder}" as an api_key'),
    target_fixture="context",
)
def config_with_placeholder(placeholder: str, config_file: str) -> dict[str, Any]:
    """Given a config file with a placeholder for api_key."""
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(
            f"""
models:
  reasoning:
    provider: "anthropic"
    name: "claude"
    temperature: 0.7
    api_key: "{placeholder}"
prompts:
  agent_alpha:
    system: "sys"
    task_template: "task"
sonarcloud:
  on_missing_config: "warn"
""",
        )
    return {"path": config_file}


@given(
    parsers.parse('a configuration file with "{placeholder}" as a name'),
    target_fixture="context",
)
def config_with_name_placeholder(placeholder: str, config_file: str) -> dict[str, Any]:
    """Given a config file with a placeholder for name."""
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(
            f"""
models:
  reasoning:
    provider: "anthropic"
    name: "{placeholder}"
    temperature: 0.7
prompts:
  agent_alpha:
    system: "sys"
    task_template: "task"
sonarcloud:
  on_missing_config: "warn"
""",
        )
    return {"path": config_file}


@given(parsers.parse('the environment variable "{name}" is set to "{value}"'))
def set_env_var(name: str, value: str) -> None:
    """Set an environment variable."""
    os.environ[name] = value


@given(parsers.parse('the environment variable "{name}" is NOT set'))
def unset_env_var(name: str) -> None:
    """Unset an environment variable."""
    if name in os.environ:
        del os.environ[name]


@when("I load the configuration", target_fixture="workflow_config")
def load_workflow_config(context: dict[str, Any]) -> Any:
    """When I load the configuration."""
    return WorkflowConfigLoader.load(context["path"])


@then(parsers.parse('the loaded api_key should be "{expected}"'))
def verify_api_key(workflow_config: Any, expected: str) -> None:
    """Then verify the interpolated api_key."""
    assert workflow_config.models["reasoning"].api_key == expected


@then(parsers.parse('the loaded name should be "{expected}"'))
def verify_name(workflow_config: Any, expected: str) -> None:
    """Then verify the interpolated name."""
    assert workflow_config.models["reasoning"].name == expected
