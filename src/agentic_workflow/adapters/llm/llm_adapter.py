"""LLM Adapter — Provider-Agnostic LLM Gateway.

Implements: LLMGateway port
Traceable to: FR-026, FR-027, FR-029, UC-003, CLS-017, ALG-008, ADR-STR-004
Supports OpenAI and Anthropic providers. Uses LLMStrategySelector (CLS-017)
for model routing. Requires langchain-core >= 0.3.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from langchain_core.messages import HumanMessage, SystemMessage

from agentic_workflow.application.ports.gateways import LLMGateway
from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
from agentic_workflow.domain.models.enums import TaskType
from agentic_workflow.domain.models.model_config import ModelConfig
from agentic_workflow.domain.services.llm_strategy_selector import LLMStrategySelector

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


def _build_langchain_model(model_cfg: ModelConfig) -> "BaseChatModel":
    """Instantiate a LangChain chat model from a ModelConfig.

    Lazily imports provider-specific packages so the adapter can be
    imported without both openai and anthropic being installed.

    Args:
        model_cfg: Immutable model configuration.

    Returns:
        LangChain BaseChatModel instance.

    Raises:
        ImportError: If the required provider package is not installed.
        ValueError: If the provider is unsupported.
    """
    provider = model_cfg.provider.lower()
    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "langchain-openai is required for OpenAI provider. "
                "Install with: pip install langchain-openai"
            ) from exc
        return ChatOpenAI(
            model=model_cfg.model,
            temperature=model_cfg.temperature,
            max_tokens=model_cfg.max_tokens,
        )
    if provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "langchain-anthropic is required for Anthropic provider. "
                "Install with: pip install langchain-anthropic"
            ) from exc
        return ChatAnthropic(  # type: ignore[call-arg]
            model=model_cfg.model,
            temperature=model_cfg.temperature,
            max_tokens=model_cfg.max_tokens,
        )
    raise ValueError(f"Unsupported LLM provider: {provider!r}")


class LangChainLLMAdapter(LLMGateway):
    """LangChain-backed LLM gateway.

    Uses CLS-017 LLMStrategySelector for task-type-based model routing.
    Delegates to langchain_openai or langchain_anthropic at call time.

    Args:
        strategy_config: Strategy configuration (ALG-008).
        system_prompt: Optional system-level instruction for all calls.
    """

    def __init__(
        self,
        strategy_config: StrategyConfig,
        system_prompt: str = "You are a helpful AI coding assistant.",
    ) -> None:
        self._selector = LLMStrategySelector(strategy_config)
        self._system_prompt = system_prompt
        # Cache LangChain model instances keyed by (provider, model, temp)
        self._model_cache: dict[tuple[Any, ...], "BaseChatModel"] = {}

    def _get_model(self, model_cfg: ModelConfig) -> "BaseChatModel":
        key = (model_cfg.provider, model_cfg.model, model_cfg.temperature)
        if key not in self._model_cache:
            self._model_cache[key] = _build_langchain_model(model_cfg)
        return self._model_cache[key]

    def complete(
        self,
        prompt: str,
        task_type: TaskType = TaskType.RESOLVE,
        max_tokens: int = 4096,
    ) -> str:
        """Send a prompt to the selected LLM and return the completion.

        Args:
            prompt: User-facing prompt string.
            task_type: Task type for ALG-008 model selection.
            max_tokens: Maximum tokens in the response.

        Returns:
            LLM completion string.
        """
        model_cfg = self._selector.select(task_type)
        lc_model = self._get_model(model_cfg)
        messages = [
            SystemMessage(content=self._system_prompt),
            HumanMessage(content=prompt),
        ]
        response = lc_model.invoke(messages)
        return str(response.content)

    def get_model_config(self, task_type: TaskType) -> ModelConfig:
        """Return the ModelConfig for the given task type.

        Args:
            task_type: Task type to resolve.

        Returns:
            ModelConfig for the selected model.
        """
        return self._selector.select(task_type)

    def is_available(self) -> bool:
        """Check if an API key is present for the default provider.

        Tests the reasoning-model provider (used by Agent alpha).

        Returns:
            True if a corresponding API key env-var is set.
        """
        default_cfg = self._selector.select(TaskType.CRITIQUE)
        provider = default_cfg.provider.lower()
        env_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }
        env_var = env_map.get(provider, f"{provider.upper()}_API_KEY")
        return bool(os.environ.get(env_var))
