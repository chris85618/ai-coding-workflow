"""Anthropic LLM Provider Implementation.

Traceable to: ADR-STR-009, CLS-027
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from agentic_workflow.application.ports.llm_provider import LLMProvider

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

    from agentic_workflow.domain.value_objects import ModelConfig


class AnthropicProviderMapper(LLMProvider):
    """Provider for Anthropic chat models."""

    @staticmethod
    def _get_anthropic_class() -> Any:
        """Dynamically import ChatAnthropic or raise descriptive ImportError."""
        try:
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic
        except ImportError as err:
            raise ImportError("langchain-anthropic is required. Install: pip install langchain-anthropic") from err

    def create_model(self, model_cfg: ModelConfig) -> BaseChatModel:
        """Instantiate a LangChain ChatAnthropic model."""
        cls = self._get_anthropic_class()
        cfg = model_cfg
        kw = {"model": cfg.model, "temperature": cfg.temperature, "max_tokens": cfg.max_tokens, "api_key": cfg.api_key}
        return cast("BaseChatModel", cls(**kw))


# Backward compatibility facades
AnthropicProvider = AnthropicProviderMapper
