"""Frameworks Layer — Configuration Loader.

Implements ADR-STR-006: External YAML Configuration.
Loads models and prompts from config.yaml.
"""
from __future__ import annotations

import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Any

class ModelConfig(BaseModel):
    provider: str
    name: str
    temperature: float

class PromptConfig(BaseModel):
    system: str
    task_template: str

class WorkflowConfig(BaseModel):
    models: Dict[str, ModelConfig]
    prompts: Dict[str, PromptConfig]

def load_config(config_path: str = "config.yaml") -> WorkflowConfig:
    """Load the externalized YAML configuration."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
        
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    return WorkflowConfig(**data)
