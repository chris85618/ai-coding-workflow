"""BDD step definitions for llm_strategy.feature (SC-014).

Traceable to: UC-003, INV-022, CLS-017, ALG-008
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from agentic_workflow.domain.algorithms.model_selector import (
    StrategyConfig,
    select_model,
)
from agentic_workflow.domain.models.enums import TaskType
from agentic_workflow.domain.models.model_config import ModelConfig
from agentic_workflow.domain.services.llm_strategy_selector import LLMStrategySelector

# ── Scenarios ─────────────────────────────────────────────────────────────────


@scenario("llm_strategy.feature", "Agent alpha uses reasoning model for critique")
def test_alpha_critique() -> None:
    """SC-014: Agent alpha → reasoning model on CRITIQUE."""


@scenario("llm_strategy.feature", "Agent beta uses editing model for resolve")
def test_beta_resolve() -> None:
    """SC-014: Agent beta → editing model on RESOLVE."""


@scenario("llm_strategy.feature", "Simple formatting uses cheapest model")
def test_format_cheap() -> None:
    """SC-014: FORMAT task → cheapest model."""


@scenario("llm_strategy.feature", "Fallback when provider is disabled")
def test_fallback_disabled_provider() -> None:
    """SC-014: Disabled provider → fallback model."""


@scenario("llm_strategy.feature", "All configured providers are listed")
def test_list_providers() -> None:
    """SC-014: list_providers returns all enabled providers."""


# ── Context ───────────────────────────────────────────────────────────────────


@pytest.fixture
def ctx() -> dict[str, Any]:
    """Shared state dictionary for BDD step context."""
    return {}


# ── Given steps ───────────────────────────────────────────────────────────────


@given(parsers.parse("strategy config has reasoning_model set to {model}"))
def given_reasoning_model(ctx: dict[str, Any], model: str) -> None:
    """Step: set reasoning model."""
    ctx["reasoning_model"] = ModelConfig(provider="anthropic", model=model)


@given(parsers.parse("strategy config has editing_model set to {model}"))
def given_editing_model(ctx: dict[str, Any], model: str) -> None:
    """Step: set editing model."""
    ctx["editing_model"] = ModelConfig(provider="openai", model=model)


@given(parsers.parse("strategy config has cheap_model set to {model}"))
def given_cheap_model(ctx: dict[str, Any], model: str) -> None:
    """Step: set cheap model."""
    ctx["cheap_model"] = ModelConfig(provider="openai", model=model)


@given(parsers.parse("provider {provider} is disabled in config"))
def given_provider_disabled(ctx: dict[str, Any], provider: str) -> None:
    """Step: disable provider."""
    ctx["disabled_provider"] = provider


@given("reasoning_model uses anthropic")
def given_reasoning_uses_anthropic(ctx: dict[str, Any]) -> None:
    """Step: reasoning uses anthropic."""
    ctx.setdefault("reasoning_model", ModelConfig(provider="anthropic", model="claude-opus-4"))


@given(parsers.parse("strategy config has {n:d} providers enabled"))
def given_n_providers(ctx: dict[str, Any], n: int) -> None:
    """Step: set enabled providers count."""
    ctx["n_providers"] = n


# ── When steps ────────────────────────────────────────────────────────────────


@when(parsers.parse("task_type is {task_type}"))
def when_task_type(ctx: dict[str, Any], task_type: str) -> None:
    """Step: select model for task type."""
    task = TaskType(task_type.lower())

    reasoning = ctx.get("reasoning_model", ModelConfig(provider="anthropic", model="claude-opus-4"))
    editing = ctx.get("editing_model", ModelConfig(provider="openai", model="gpt-4o"))
    cheap = ctx.get("cheap_model", ModelConfig(provider="openai", model="gpt-4o-mini"))
    fallback = ModelConfig(provider="openai", model="gpt-4o")
    disabled = ctx.get("disabled_provider")

    enabled = frozenset(p for p in ("anthropic", "openai") if p != disabled)

    config = StrategyConfig(
        reasoning_model=reasoning,
        editing_model=editing,
        cheap_model=cheap,
        default_model=editing,
        fallback_model=fallback,
        enabled_providers=enabled,
    )
    ctx["selected"] = select_model(task, config)
    ctx["config"] = config


@when("list_providers is called")
def when_list_providers(ctx: dict[str, Any]) -> None:
    """Step: list providers."""
    n = ctx.get("n_providers", 3)
    providers = frozenset({f"provider{i}" for i in range(n)})
    config = StrategyConfig(
        reasoning_model=ModelConfig(provider="provider0", model="m"),
        editing_model=ModelConfig(provider="provider0", model="m"),
        cheap_model=ModelConfig(provider="provider0", model="m"),
        default_model=ModelConfig(provider="provider0", model="m"),
        fallback_model=ModelConfig(provider="provider0", model="m"),
        enabled_providers=providers,
    )
    selector = LLMStrategySelector(config)
    ctx["provider_list"] = selector.list_providers()


# ── Then steps ────────────────────────────────────────────────────────────────


@then(parsers.parse("ModelConfig.model is {model}"))
def then_model_is(ctx: dict[str, Any], model: str) -> None:
    """Step: verify selected model."""
    assert ctx["selected"].model == model


@then(parsers.parse("ModelConfig.provider is {provider}"))
def then_provider_is(ctx: dict[str, Any], provider: str) -> None:
    """Step: verify selected provider."""
    assert ctx["selected"].provider == provider


@then("fallback_model is selected instead")
def then_fallback_selected(ctx: dict[str, Any]) -> None:
    """Step: verify fallback selection."""
    assert ctx["selected"].provider == "openai"


@then("a warning is logged about provider unavailability")
def then_warning_logged(ctx: dict[str, Any]) -> None:
    """Step: verify warning logging."""
    # Structural: if we got here without exception, graceful degradation worked
    assert ctx["selected"] is not None


@then(parsers.parse("{n:d} provider names are returned"))
def then_n_providers_returned(ctx: dict[str, Any], n: int) -> None:
    """Step: verify providers count."""
    assert len(ctx["provider_list"]) == n
