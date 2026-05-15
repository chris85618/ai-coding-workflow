"""Frameworks Layer — Configuration Loader.

Implements ADR-STR-006: External YAML Configuration.
Implements ADR-SEC-005: Configuration Security Gateway.
Loads models and prompts from config.yaml, and secrets from .env.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from re import Match
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field


class ModelConfig(BaseModel):
    """Configuration for a specific LLM model provider."""

    model_config = ConfigDict(populate_by_name=True)

    provider: str
    model: str = Field(alias="name", validation_alias="name")
    temperature: float = 0.0
    max_tokens: int = 4096
    api_key: str | None = None

    @property
    def name(self) -> str:
        """Backward compatibility for tests using .name."""
        return self.model


class PromptConfig(BaseModel):
    """Configuration for prompt templates and system messages."""

    system: str
    task_template: str


class FeedbackConfig(BaseModel):
    """Nested feedback configuration for SonarCloud."""

    auto_convert_to_debt: bool = True
    default_debt_priority: str = "P2"


class SonarCloudConfig(BaseModel):
    """Configuration for SonarCloud quality gate."""

    token: str | None = None
    project_key: str | None = None
    organization: str | None = None
    feedback: FeedbackConfig = Field(default_factory=FeedbackConfig)
    on_missing_config: str = "warn_and_disable"


class WorkflowConfig(BaseModel):
    """Root configuration object for the entire workflow."""

    models: dict[str, ModelConfig]
    prompts: dict[str, PromptConfig]
    sonarcloud: SonarCloudConfig


def _interpolate_env_vars(data: Any) -> Any:
    """Recursively search and replace ${VAR} with environment variables."""
    pattern = re.compile(r"\$\{(\w+)(?::([^}]*))?\}")

    if isinstance(data, str):

        def replacer(match: Match[str]) -> str:
            env_var, default = match.groups()
            return os.getenv(
                env_var, default if default is not None else match.group(0)
            )

        return pattern.sub(replacer, data)

    if isinstance(data, dict):
        return {k: _interpolate_env_vars(v) for k, v in data.items()}

    if isinstance(data, list):
        return [_interpolate_env_vars(i) for i in data]

    return data


def load_config(config_path: str = "config.yaml") -> WorkflowConfig:
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
    interpolated_data = _interpolate_env_vars(raw_data)

    # 4. Parse into Pydantic model
    return WorkflowConfig(**interpolated_data)
