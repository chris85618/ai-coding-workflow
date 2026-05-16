"""Frameworks Config — PromptConfig Pydantic model.

Implements ADR-STR-006: External YAML Configuration.
Implements ADR-SEC-005: Configuration Security Gateway.
"""

from __future__ import annotations

from pydantic import BaseModel


class PromptConfig(BaseModel):
    """Configuration for prompt templates and system messages."""

    system: str
    task_template: str
