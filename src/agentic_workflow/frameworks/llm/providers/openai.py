"""OpenAI LLM Provider Implementation.

Traceable to: ADR-STR-009, CLS-026
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from agentic_workflow.application.ports.llm_provider import LLMProvider

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

    from agentic_workflow.domain.value_objects import ModelConfig


class OpenAIProviderMapper(LLMProvider):
    """Provider for OpenAI chat models."""

    @staticmethod
    def _get_openai_class() -> Any:
        """Dynamically import ChatOpenAI or raise descriptive ImportError."""
        try:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI
        except ImportError as err:
            raise ImportError("langchain-openai is required. Install: pip install langchain-openai") from err

    def create_model(self, model_cfg: ModelConfig) -> BaseChatModel:
        """Instantiate a LangChain ChatOpenAI model."""
        cls = self._get_openai_class()
        cfg = model_cfg
        kw = {"model": cfg.model, "temperature": cfg.temperature, "max_tokens": cfg.max_tokens}
        kw.update({"openai_api_key": cfg.api_key, "base_url": cfg.base_url})
        return cast("BaseChatModel", cls(**kw))


# Backward compatibility facades
OpenAIProvider = OpenAIProviderMapper
