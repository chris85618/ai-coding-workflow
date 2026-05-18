"""Anthropic LLM Provider Implementation.

Traceable to: ADR-STR-009, CLS-027
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from agentic_workflow.application.ports.llm_provider import LLMProvider

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

    from agentic_workflow.domain.value_objects import ModelConfig


def _get_anthropic_class() -> Any:
    try:
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic
    except ImportError as err:
        raise ImportError("langchain-anthropic is required. Install: pip install langchain-anthropic") from err


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic chat models."""

    def create_model(self, model_cfg: ModelConfig) -> BaseChatModel:
        """Instantiate a LangChain ChatAnthropic model."""
        cls = _get_anthropic_class()
        return cast(
            "BaseChatModel",
            cls(
                model=model_cfg.model,
                temperature=model_cfg.temperature,
                max_tokens=model_cfg.max_tokens,
                api_key=model_cfg.api_key,
            ),
        )
