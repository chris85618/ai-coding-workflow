"""Cover missing branches in CLS-017."""

from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
from agentic_workflow.domain.enums import TaskType
from agentic_workflow.domain.services.llm_strategy_selector import LLMStrategySelector
from agentic_workflow.domain.value_objects import ModelConfig


class TestLLMStrategySelectorBranches:
    """Cover missing branches in CLS-017."""

    def _make_selector(self) -> LLMStrategySelector:
        m = ModelConfig(provider="anthropic", model="claude-opus-4")
        cfg = StrategyConfig(
            reasoning_model=m,
            editing_model=ModelConfig(provider="openai", model="gpt-4o"),
            cheap_model=ModelConfig(provider="openai", model="gpt-4o-mini"),
            default_model=ModelConfig(provider="openai", model="gpt-4o"),
            fallback_model=ModelConfig(provider="openai", model="gpt-4o"),
            enabled_providers=frozenset({"anthropic", "openai"}),
        )
        return LLMStrategySelector(cfg)

    def test_list_providers(self) -> None:
        """list_providers returns sorted list."""
        sel = self._make_selector()
        providers = sel.list_providers()
        assert sorted(providers) == providers
        assert "anthropic" in providers

    def test_enabled_provider_count(self) -> None:
        """enabled_provider_count returns integer count."""
        sel = self._make_selector()
        assert sel.enabled_provider_count == 2

    def test_select_comprehend(self) -> None:
        """COMPREHEND maps to reasoning model."""
        sel = self._make_selector()
        m = sel.select(TaskType.COMPREHEND)
        assert m.provider == "anthropic"

    def test_select_charter(self) -> None:
        """CHARTER maps to reasoning model."""
        sel = self._make_selector()
        m = sel.select(TaskType.CHARTER)
        assert m.provider == "anthropic"
