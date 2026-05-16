"""LLM Adapter — Provider-Agnostic LLM Gateway.

Implements: LLMGateway port
Traceable to: FR-026, FR-027, FR-029, UC-003, CLS-017, ALG-008, ADR-STR-004
Supports OpenAI and Anthropic providers. Uses LLMStrategySelector (CLS-017)
for model routing. Requires langchain-core >= 0.3.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchain_core.messages import HumanMessage, SystemMessage

from agentic_workflow.adapters.llm.provider_registry import LLMProviderRegistry
from agentic_workflow.application.ports.gateways import LLMGateway
from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
from agentic_workflow.domain.models.enums import TaskType
from agentic_workflow.domain.models.model_config import ModelConfig
from agentic_workflow.domain.services.llm_strategy_selector import LLMStrategySelector

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


class LangChainLLMAdapter(LLMGateway):
    """LangChain-backed LLM gateway.

    Uses CLS-017 LLMStrategySelector for task-type-based model routing.
    Delegates to LLMProviderRegistry to instantiate specific models.

    Args:
        strategy_config: Strategy configuration (ALG-008).
        system_prompt: Optional system-level instruction for all calls.
    """

    def __init__(
        self,
        strategy_config: StrategyConfig,
        system_prompt: str = "You are a helpful AI coding assistant.",
    ) -> None:
        """Initialize the adapter with strategy and prompt."""
        self._selector = LLMStrategySelector(strategy_config)
        self._system_prompt = system_prompt
        self._registry = LLMProviderRegistry()
        # Cache LangChain model instances keyed by (provider, model, temp)
        self._model_cache: dict[tuple[Any, ...], BaseChatModel] = {}

    def _get_model(self, model_cfg: ModelConfig) -> BaseChatModel:
        key = (model_cfg.provider, model_cfg.model, model_cfg.temperature)
        if key not in self._model_cache:
            provider = self._registry.get_provider(model_cfg.provider)
            self._model_cache[key] = provider.create_model(model_cfg)
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

        Raises:
            TokenLimitExceededError: If token limit is reached and auto-continue
                is disabled or maxed out.
        """
        from agentic_workflow.domain.models.exceptions import TokenLimitExceededError

        model_cfg = self._selector.select(task_type)
        lc_model = self._get_model(model_cfg)
        messages: list[Any] = [
            SystemMessage(content=self._system_prompt),
            HumanMessage(content=prompt),
        ]

        # Determine if auto-continuation is safe
        auto_continue_types = {TaskType.CRITIQUE, TaskType.COMPREHEND, TaskType.CHARTER}
        can_auto_continue = task_type in auto_continue_types
        max_continuations = 3 if can_auto_continue else 0
        continuations = 0
        full_content = ""

        while True:
            response = lc_model.invoke(messages)
            content = str(response.content)
            full_content += content

            finish_reason = response.response_metadata.get("finish_reason")
            if not finish_reason:
                finish_reason = response.response_metadata.get("stop_reason")

            if finish_reason in ("length", "max_tokens"):
                if not can_auto_continue:
                    raise TokenLimitExceededError(
                        f"Output exceeded max_tokens={max_tokens} for "
                        f"structural task {task_type.value}. "
                        "Auto-continuation disabled."
                    )
                continuations += 1
                if continuations > max_continuations:
                    raise TokenLimitExceededError(
                        f"Output exceeded max_tokens across {max_continuations} continuations."
                    )
                continuations += 1
                messages.append(response)
                messages.append(
                    HumanMessage(
                        content=(
                            "Response truncated due to length. Please continue "
                            "exactly where you left off. Do not repeat previous "
                            "content. Do not add introductory text."
                        )
                    )
                )
            else:
                break

        return full_content

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
            True if a corresponding API key is set in the config.
        """
        default_cfg = self._selector.select(TaskType.CRITIQUE)
        return bool(default_cfg.api_key)
