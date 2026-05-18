"""LangChain-backed LLM gateway adapter implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchain_core.messages import HumanMessage, SystemMessage

from agentic_workflow.application.ports.gateways import LLMGateway
from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
from agentic_workflow.domain.enums import TaskType
from agentic_workflow.domain.services.llm_strategy_selector import LLMStrategySelector
from agentic_workflow.domain.value_objects import ModelConfig
from agentic_workflow.frameworks.llm.provider_registry import LLMProviderRegistry

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


class LangChainLLMAdapterMapper(LLMGateway):
    """LangChain-backed LLM gateway.

    Uses CLS-017 LLMStrategySelector for task-type-based model routing.
    Delegates to LLMProviderRegistry to instantiate specific models.

    Args:
        strategy_config: Strategy configuration (ALG-008).
        system_prompt: Optional system-level instruction for all calls.
    """

    TRUNC = (
        "Response truncated due to length. Please continue "
        "exactly where you left off. Do not repeat previous "
        "content. Do not add introductory text."
    )

    @staticmethod
    def _check_auto(is_auto: bool, task_type: TaskType) -> None:
        from agentic_workflow.domain.exceptions import TokenLimitExceededError

        if not is_auto:
            raise TokenLimitExceededError(
                f"Output exceeded max_tokens for structural task {task_type.value}. Auto-continuation disabled."
            )

    @staticmethod
    def _check_count(count: int, max_cont: int) -> None:
        from agentic_workflow.domain.exceptions import TokenLimitExceededError

        if count > max_cont:
            raise TokenLimitExceededError(f"Output exceeded max_tokens across {max_cont} continuations.")

    @classmethod
    def _append_msgs(cls, messages: list[Any], resp: Any) -> None:
        messages.append(resp)
        messages.append(HumanMessage(content=cls.TRUNC))

    @classmethod
    def _handle_len(
        cls,
        messages: list[Any],
        resp: Any,
        task_type: TaskType,
        is_auto: bool,
        max_cont: int,
        state: dict[str, Any],
    ) -> bool:
        cls._check_auto(is_auto, task_type)
        state["count"] += 1
        cls._check_count(state["count"], max_cont)
        cls._append_msgs(messages, resp)
        return True

    @classmethod
    def _step(
        cls,
        model: BaseChatModel,
        messages: list[Any],
        task_type: TaskType,
        is_auto: bool,
        max_cont: int,
        state: dict[str, Any],
    ) -> bool:
        resp = model.invoke(messages)
        state["content"] += str(resp.content)
        meta = resp.response_metadata
        reason = meta.get("finish_reason") or meta.get("stop_reason")
        is_len = reason in ("length", "max_tokens")
        return cls._handle_len(messages, resp, task_type, is_auto, max_cont, state) if is_len else False

    @classmethod
    def _run_loop(cls, model: BaseChatModel, messages: list[Any], task_type: TaskType) -> str:
        is_auto = task_type in {TaskType.CRITIQUE, TaskType.COMPREHEND, TaskType.CHARTER}
        state = {"content": "", "count": 0}
        has_more = True
        while has_more:
            has_more = cls._step(model, messages, task_type, is_auto, 3 if is_auto else 0, state)
        return str(state["content"])

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
        key = (model_cfg.provider, model_cfg.model, model_cfg.temperature, model_cfg.base_url)
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
        lc_model = self._get_model(self._selector.select(task_type))
        messages = [SystemMessage(content=self._system_prompt), HumanMessage(content=prompt)]
        return self._run_loop(lc_model, messages, task_type)

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


LangChainLLMAdapter = LangChainLLMAdapterMapper
