"""Frameworks Layer — Configuration Loader.

Implements ADR-STR-006: External YAML Configuration.
Loads models and prompts from config.yaml.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


class ModelConfig(BaseModel):
    """Configuration for a specific LLM model provider."""

    provider: str
    name: str
    temperature: float


class PromptConfig(BaseModel):
    """Configuration for prompt templates and system messages."""

    system: str
    task_template: str


class WorkflowConfig(BaseModel):
    """Root configuration object for the entire workflow."""

    models: dict[str, ModelConfig]
    prompts: dict[str, PromptConfig]


def load_config(config_path: str = "config.yaml") -> WorkflowConfig:
    """Load the externalized YAML configuration."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return WorkflowConfig(**data)
