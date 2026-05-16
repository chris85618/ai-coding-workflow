"""ALG-008 OO class interface."""

import pytest

from agentic_workflow.domain.algorithms.model_selector import ModelSelector, StrategyConfig
from agentic_workflow.domain.models.enums import TaskType
from agentic_workflow.domain.models.model_config import ModelConfig


class TestModelSelectorOO:
    """ALG-008 OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        self.cls = ModelSelector
        self.reasoning = ModelConfig(provider="anthropic", model="claude-opus")
        self.editing = ModelConfig(provider="anthropic", model="claude-haiku")
        self.cheap = ModelConfig(provider="openai", model="gpt-3.5")
        self.default = ModelConfig(provider="anthropic", model="claude-sonnet")
        self.fallback = ModelConfig(provider="openai", model="gpt-4o")
        self.config = StrategyConfig(
            reasoning_model=self.reasoning,
            editing_model=self.editing,
            cheap_model=self.cheap,
            default_model=self.default,
            fallback_model=self.fallback,
            enabled_providers=frozenset(["anthropic", "openai"]),
        )

    def test_critique_maps_to_reasoning(self) -> None:
        """TC-201: CRITIQUE task mapping."""
        result = self.cls.select(TaskType.CRITIQUE, self.config)
        assert result == self.reasoning

    def test_resolve_maps_to_editing(self) -> None:
        """TC-202: RESOLVE task mapping."""
        result = self.cls.select(TaskType.RESOLVE, self.config)
        assert result == self.editing

    def test_format_maps_to_cheap(self) -> None:
        """TC-203: FORMAT task mapping."""
        result = self.cls.select(TaskType.FORMAT, self.config)
        assert result == self.cheap

    def test_falls_back_when_provider_disabled(self) -> None:
        """TC-204: Fallback for disabled provider."""
        config = StrategyConfig(
            reasoning_model=ModelConfig(provider="disabled_provider", model="x"),
            editing_model=self.editing,
            cheap_model=self.cheap,
            default_model=self.default,
            fallback_model=self.fallback,
            enabled_providers=frozenset(["openai"]),
        )
        result = self.cls.select(TaskType.CRITIQUE, config)
        assert result.provider == "openai"

    def test_no_providers_raises(self) -> None:
        """TC-205: No enabled providers raises error."""
        import icontract

        config = StrategyConfig(
            reasoning_model=self.reasoning,
            editing_model=self.editing,
            cheap_model=self.cheap,
            default_model=self.default,
            fallback_model=self.fallback,
            enabled_providers=frozenset(),
        )
        with pytest.raises(icontract.ViolationError):
            self.cls.select(TaskType.CRITIQUE, config)
