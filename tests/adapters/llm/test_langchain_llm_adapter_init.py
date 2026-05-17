"""TC-124, TC-125: OpenAI and Anthropic adapter initialization."""

import sys
from unittest.mock import MagicMock, patch

from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
from agentic_workflow.domain.enums import TaskType
from agentic_workflow.domain.value_objects import ModelConfig
from agentic_workflow.frameworks.llm.llm_adapter import LangChainLLMAdapter


def _get_cfg(provider: str) -> StrategyConfig:
    mc = ModelConfig(provider=provider, model="test")
    return StrategyConfig(
        reasoning_model=mc,
        editing_model=mc,
        cheap_model=mc,
        default_model=mc,
        fallback_model=mc,
        enabled_providers=frozenset([provider]),
    )


class TestLangChainLLMAdapterInit:
    """TC-124, TC-125: Adapter initialization tests."""

    def test_llm_adapter_openai_init_success(self) -> None:
        """TC-124: OpenAI adapter initialization."""
        cfg = _get_cfg("openai")

        mock_openai = MagicMock()
        with patch.dict(sys.modules, {"langchain_openai": mock_openai}):
            adapter = LangChainLLMAdapter(cfg)
            adapter.complete("hi", TaskType.RESOLVE)
            mock_openai.ChatOpenAI.return_value.invoke.assert_called_once()

    def test_llm_adapter_anthropic_init_success(self) -> None:
        """TC-125: Anthropic adapter initialization."""
        cfg = _get_cfg("anthropic")
        mock_anthropic = MagicMock()
        with patch.dict(sys.modules, {"langchain_anthropic": mock_anthropic}):
            adapter = LangChainLLMAdapter(cfg)
            adapter.complete("hi", TaskType.RESOLVE)
            mock_anthropic.ChatAnthropic.return_value.invoke.assert_called_once()
