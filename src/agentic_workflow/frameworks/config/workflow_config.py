"""Frameworks Config — WorkflowConfig root Pydantic model and load_config.

Implements ADR-STR-006: External YAML Configuration.
Implements ADR-SEC-005: Configuration Security Gateway.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

from agentic_workflow.frameworks.config.model_config import ModelConfig
from agentic_workflow.frameworks.config.prompt_config import PromptConfig
from agentic_workflow.frameworks.config.sonarcloud import SonarCloudConfig


class WorkflowConfig(BaseModel):
    """Root configuration object for the entire workflow."""

    models: dict[str, ModelConfig]
    prompts: dict[str, PromptConfig]
    sonarcloud: SonarCloudConfig


def _sub_env(val: str) -> str:
    pat = re.compile(r"\$\{(\w+)(?::\-?([^}]*))?\}")

    def rep(m: Any) -> str:
        return os.getenv(m.group(1), m.group(2) if m.group(2) is not None else m.group(0))

    return pat.sub(rep, val)


def _sub_dict(data: dict[Any, Any]) -> dict[Any, Any]:
    return {k: WorkflowConfigLoader._interpolate_env_vars(v) for k, v in data.items()}


def _sub_list(data: list[Any]) -> list[Any]:
    return [WorkflowConfigLoader._interpolate_env_vars(i) for i in data]


def _read_yaml(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _assert_exists(path: Path, config_path: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")


class WorkflowConfigLoader:
    """Loader and orchestrator for system-wide configuration configuration.

    Encapsulates logic for loading YAML configuration and interpolating
    environment variables.
    """

    @staticmethod
    def _interpolate_env_vars(data: Any) -> Any:
        """Recursively search and replace ${VAR} with environment variables."""
        handlers: dict[type, Any] = {str: _sub_env, dict: _sub_dict, list: _sub_list}
        handler = handlers.get(type(data), lambda x: x)
        return handler(data)

    @classmethod
    def load(cls, config_path: str = "config.yaml") -> WorkflowConfig:
        """Load and merge configuration with environment variable interpolation.

        Supports ${VAR_NAME} syntax in YAML to reference .env variables.
        """
        load_dotenv()
        path = Path(config_path)
        _assert_exists(path, config_path)
        raw = _read_yaml(path)
        return WorkflowConfig(**cls._interpolate_env_vars(raw))
