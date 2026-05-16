"""OpenAI LLM Provider Implementation.

Traceable to: ADR-STR-009, CLS-026
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_workflow.application.ports.llm_provider import LLMProvider

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

    from agentic_workflow.domain.models.model_config import ModelConfig


class OpenAIProvider(LLMProvider):
    """Provider for OpenAI chat models."""

    def create_model(self, model_cfg: ModelConfig) -> BaseChatModel:
        """Instantiate a LangChain ChatOpenAI model."""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise ImportError(
                "langchain-openai is required for OpenAI provider. Install with: pip install langchain-openai"
            ) from exc

        from typing import cast

        return cast(
            "BaseChatModel",
            ChatOpenAI(
                model=model_cfg.model,
                temperature=model_cfg.temperature,
                max_tokens=model_cfg.max_tokens,
                openai_api_key=model_cfg.api_key,
            ),
        )
