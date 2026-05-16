"""Frameworks Config — WorkflowConfig root Pydantic model and load_config.

Implements ADR-STR-006: External YAML Configuration.
Implements ADR-SEC-005: Configuration Security Gateway.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from re import Match
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

from agentic_workflow.frameworks.config.model_config import ModelConfig
from agentic_workflow.frameworks.config.prompt_config import PromptConfig
from agentic_workflow.frameworks.config.sonarcloud_config import SonarCloudConfig


class WorkflowConfig(BaseModel):
    """Root configuration object for the entire workflow."""

    models: dict[str, ModelConfig]
    prompts: dict[str, PromptConfig]
    sonarcloud: SonarCloudConfig


class WorkflowConfigLoader:
    """OO Configuration Loader.

    Encapsulates logic for loading YAML configuration and interpolating
    environment variables.
    """

    @staticmethod
    def _interpolate_env_vars(data: Any) -> Any:
        """Recursively search and replace ${VAR} with environment variables."""
        pattern = re.compile(r"\$\{(\w+)(?::([^}]*))?\}")

        if isinstance(data, str):

            def replacer(match: Match[str]) -> str:
                env_var, default = match.groups()
                return os.getenv(env_var, default if default is not None else match.group(0))

            return pattern.sub(replacer, data)

        if isinstance(data, dict):
            return {k: WorkflowConfigLoader._interpolate_env_vars(v) for k, v in data.items()}

        if isinstance(data, list):
            return [WorkflowConfigLoader._interpolate_env_vars(i) for i in data]

        return data

    @classmethod
    def load(cls, config_path: str = "config.yaml") -> WorkflowConfig:
        """Load and merge configuration with environment variable interpolation.

        Supports ${VAR_NAME} syntax in YAML to reference .env variables.
        """
        # 1. Load environment variables from .env
        load_dotenv()

        # 2. Load YAML configuration
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(path, encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)

        # 3. Interpolate environment variables
        interpolated_data = cls._interpolate_env_vars(raw_data)

        # 4. Parse into Pydantic model
        return WorkflowConfig(**interpolated_data)
