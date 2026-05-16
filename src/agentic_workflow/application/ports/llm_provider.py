"""LLM Provider Port — Interface for model instantiation.

Traceable to: ADR-STR-009, CLS-025
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

    from agentic_workflow.domain.value_objects import ModelConfig


class LLMProvider(ABC):
    """Abstract interface for LLM model instantiation."""

    @abstractmethod
    def create_model(self, model_cfg: ModelConfig) -> BaseChatModel:
        """Create a LangChain chat model instance."""
