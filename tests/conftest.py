"""Pytest-BDD conftest — shared fixtures for all BDD feature files.

Provides fixtures for domain objects, test doubles, and common setup.
All step definitions share these fixtures.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
from agentic_workflow.domain.entities.stage import Stage
from agentic_workflow.domain.enums import (
    GateDecision,
    HookEvent,
)
from agentic_workflow.domain.services.hook_runner import HookDef, HookRunner
from agentic_workflow.domain.services.llm_strategy_selector import LLMStrategySelector
from agentic_workflow.domain.value_objects import ModelConfig, RepoMap, SymbolDef

# ── Project fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def context() -> dict[str, Any]:
    """BDD context fixture."""
    return {}


@pytest.fixture
def docs_path(tmp_path: Path) -> Path:
    """Provide a temporary docs/ directory for test isolation."""
    docs = tmp_path / "docs"
    docs.mkdir()
    return docs


@pytest.fixture
def empty_checkpoint() -> None:
    """Provide a None checkpoint simulating fresh start."""
    return


@pytest.fixture
def tmp_project(tmp_path: Path) -> str:
    """Create a minimal Python project directory for RepoMap tests."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.py").write_text("class Foo:\n    pass\n\ndef bar(): pass\n")
    (src / "b.py").write_text("from src.a import Foo\n\ndef baz(): pass\n")
    return str(tmp_path)


@pytest.fixture
def many_files_project(tmp_path: Path) -> str:
    """Create a larger project with 50 minimal Python files."""
    for i in range(50):
        f = tmp_path / f"module_{i:02d}.py"
        f.write_text(f"class Class{i}:\n    pass\n\ndef func_{i}(): pass\n")
    return str(tmp_path)


# ── Domain model fixtures ─────────────────────────────────────────────────────


@pytest.fixture
def running_pipeline() -> Pipeline:
    """Return a Pipeline in RUNNING state with PASS gate."""
    p = Pipeline(pipeline_id="test-pipe")
    p.start()
    p.record_gate(GateDecision.PASS)
    return p


@pytest.fixture
def fresh_stage() -> Stage:
    """Return a Stage in PENDING state."""
    return Stage(stage_id="stage3", name="Technical Planning")


# ── Strategy Pattern fixtures ─────────────────────────────────────────────────


@pytest.fixture
def anthropic_model() -> ModelConfig:
    """ModelConfig for Anthropic Claude Opus."""
    return ModelConfig(provider="anthropic", model="claude-opus-4")


@pytest.fixture
def openai_model() -> ModelConfig:
    """ModelConfig for OpenAI GPT-4o."""
    return ModelConfig(provider="openai", model="gpt-4o")


@pytest.fixture
def cheap_model() -> ModelConfig:
    """ModelConfig for OpenAI GPT-4o-mini."""
    return ModelConfig(provider="openai", model="gpt-4o-mini")


@pytest.fixture
def fallback_model() -> ModelConfig:
    """Fallback ModelConfig for when primary provider is unavailable."""
    return ModelConfig(provider="openai", model="gpt-4o")


@pytest.fixture
def strategy_config(
    anthropic_model: ModelConfig,
    openai_model: ModelConfig,
    cheap_model: ModelConfig,
    fallback_model: ModelConfig,
) -> StrategyConfig:
    """Full strategy config with anthropic + openai enabled."""
    return StrategyConfig(
        reasoning_model=anthropic_model,
        editing_model=openai_model,
        cheap_model=cheap_model,
        default_model=openai_model,
        fallback_model=fallback_model,
        enabled_providers=frozenset({"anthropic", "openai"}),
    )


@pytest.fixture
def selector(strategy_config: StrategyConfig) -> LLMStrategySelector:
    """Return a configured LLMStrategySelector."""
    return LLMStrategySelector(strategy_config)


@pytest.fixture
def openai_only_config(
    openai_model: ModelConfig,
    cheap_model: ModelConfig,
    fallback_model: ModelConfig,
) -> StrategyConfig:
    """Strategy config with only OpenAI enabled (anthropic disabled)."""
    return StrategyConfig(
        reasoning_model=ModelConfig(provider="anthropic", model="claude-opus-4"),
        editing_model=openai_model,
        cheap_model=cheap_model,
        default_model=openai_model,
        fallback_model=fallback_model,
        enabled_providers=frozenset({"openai"}),
    )


# ── Hook fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture
def hook_runner() -> HookRunner:
    """Return a fresh HookRunner with no hooks registered."""
    return HookRunner()


@pytest.fixture
def passing_hook() -> HookDef:
    """A hook that always exits 0 (success)."""
    return HookDef(
        event=HookEvent.PRE_STAGE_START,
        command='python -c "exit(0)"',
        blocking=True,
    )


@pytest.fixture
def blocking_hook() -> HookDef:
    """A blocking hook that exits 2 (block signal)."""
    return HookDef(
        event=HookEvent.PRE_STAGE_START,
        command='python -c "exit(2)"',
        blocking=True,
    )


# ── RepoMap fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def small_repo_map() -> RepoMap:
    """A RepoMap with 3 symbols across 2 files."""
    syms = (
        SymbolDef("a.py", "Foo", "class", "class Foo", 1),
        SymbolDef("a.py", "bar", "function", "def bar()", 5),
        SymbolDef("b.py", "baz", "function", "def baz()", 1),
    )
    return RepoMap(symbols=syms, token_count=10, file_ranks={"a.py": 0.6, "b.py": 0.4})


@pytest.fixture
def empty_repo_map() -> RepoMap:
    """An empty RepoMap."""
    return RepoMap(symbols=(), token_count=0, file_ranks={})
