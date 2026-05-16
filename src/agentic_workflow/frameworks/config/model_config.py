"""Frameworks Config — ModelConfig Pydantic model.

Implements ADR-STR-006: External YAML Configuration.
Implements ADR-SEC-005: Configuration Security Gateway.
"""

from __future__ import annotations

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
