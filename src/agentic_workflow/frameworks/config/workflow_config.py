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


class EnvVarSubstituter:
    """Helper class to interpolate environment variables in configuration."""

    @staticmethod
    def sub_env(val: str) -> str:
        """Substitute env vars in string using regex."""
        pat = re.compile(r"\$\{(\w+)(?::\-?([^}]*))?\}")
        return pat.sub(lambda m: os.getenv(m.group(1), m.group(2) if m.group(2) is not None else m.group(0)), val)

    @staticmethod
    def sub_dict(data: dict[Any, Any]) -> dict[Any, Any]:
        """Substitute env vars in dictionary."""
        return {k: WorkflowConfigLoader._interpolate_env_vars(v) for k, v in data.items()}

    @staticmethod
    def sub_list(data: list[Any]) -> list[Any]:
        """Substitute env vars in list."""
        return [WorkflowConfigLoader._interpolate_env_vars(i) for i in data]


class WorkflowConfigLoader:
    """Loader and orchestrator for system-wide configuration configuration.

    Encapsulates logic for loading YAML configuration and interpolating
    environment variables.
    """

    @staticmethod
    def _read_yaml(path: Path) -> Any:
        """Read YAML file safely."""
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def _assert_exists(path: Path, config_path: str) -> None:
        """Assert that config file exists."""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

    @staticmethod
    def _interpolate_env_vars(data: Any) -> Any:
        """Recursively search and replace ${VAR} with environment variables."""
        handlers: dict[Any, Any] = {
            str: EnvVarSubstituter.sub_env,
            dict: EnvVarSubstituter.sub_dict,
            list: EnvVarSubstituter.sub_list,
        }
        return handlers.get(type(data), lambda x: x)(data)

    @classmethod
    def load(cls, config_path: str = "config.yaml") -> WorkflowConfig:
        """Load and merge configuration with environment variable interpolation.

        Supports ${VAR_NAME} syntax in YAML to reference .env variables.
        """
        load_dotenv()
        path = Path(config_path)
        cls._assert_exists(path, config_path)
        raw = cls._read_yaml(path)
        return WorkflowConfig(**cls._interpolate_env_vars(raw))
