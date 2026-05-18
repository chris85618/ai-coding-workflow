"""OpenAI LLM Provider Implementation.

Traceable to: ADR-STR-009, CLS-026
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from agentic_workflow.application.ports.llm_provider import LLMProvider

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

    from agentic_workflow.domain.value_objects import ModelConfig


def _get_openai_class() -> Any:
    try:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI
    except ImportError as err:
        raise ImportError("langchain-openai is required. Install: pip install langchain-openai") from err


class OpenAIProvider(LLMProvider):
    """Provider for OpenAI chat models."""

    def create_model(self, model_cfg: ModelConfig) -> BaseChatModel:
        """Instantiate a LangChain ChatOpenAI model."""
        cls = _get_openai_class()
        return cast("BaseChatModel", cls(
            model=model_cfg.model, temperature=model_cfg.temperature, max_tokens=model_cfg.max_tokens,
            openai_api_key=model_cfg.api_key, base_url=model_cfg.base_url
        ))
