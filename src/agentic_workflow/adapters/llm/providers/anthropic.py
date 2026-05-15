"""Anthropic LLM Provider Implementation.

Traceable to: ADR-STR-009, CLS-027
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_workflow.application.ports.llm_provider import LLMProvider

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

    from agentic_workflow.domain.models.model_config import ModelConfig


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic chat models."""

    def create_model(self, model_cfg: ModelConfig) -> BaseChatModel:
        """Instantiate a LangChain ChatAnthropic model."""
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as exc:
            raise ImportError(
                "langchain-anthropic is required for Anthropic provider. "
                "Install with: pip install langchain-anthropic"
            ) from exc

        from typing import cast

        return cast(
            "BaseChatModel",
            ChatAnthropic(
                model=model_cfg.model,
                temperature=model_cfg.temperature,
                max_tokens=model_cfg.max_tokens,
            ),
        )
