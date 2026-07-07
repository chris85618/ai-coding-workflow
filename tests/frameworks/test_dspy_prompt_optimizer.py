"""Tests for the DSPyPromptOptimizer frameworks gateway (FR-075, ADR-STR-031)."""

import sys
import types
from typing import Any

import pytest

from agentic_workflow.adapters.prompting.few_shot_prompt_optimizer import FewShotPromptOptimizer
from agentic_workflow.application.ports.gateways.prompt_optimizer import IPromptOptimizer
from agentic_workflow.frameworks.dspy_prompt_optimizer import (
    DSPyDemoMapper,
    DSPyModuleLoader,
    DSPyPromptOptimizer,
)


class FakeExample:
    """Stands in for dspy.Example with question/answer fields."""

    def __init__(self, question: str, answer: str) -> None:
        """Store the demonstration fields."""
        self.question = question
        self.answer = answer


def _fake_dspy_module() -> types.ModuleType:
    """Build a minimal fake dspy module exposing Example."""
    module = types.ModuleType("dspy")
    module_any: Any = module
    module_any.Example = FakeExample
    return module


class TestDSPyModuleLoader:
    """Covers optional-accelerator loading with graceful degradation."""

    def test_load_returns_none_when_dspy_is_absent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-DSPY-004: Missing dspy degrades to None instead of raising (ADR-GOV-017)."""
        monkeypatch.setitem(sys.modules, "dspy", None)
        assert DSPyModuleLoader.load() is None

    def test_load_returns_module_when_dspy_is_installed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-DSPY-005: An installed dspy module is returned as-is."""
        fake = _fake_dspy_module()
        monkeypatch.setitem(sys.modules, "dspy", fake)
        assert DSPyModuleLoader.load() is fake


class TestDSPyDemoMapper:
    """Covers demonstration normalization through dspy.Example."""

    def test_round_trip_preserves_pairs(self) -> None:
        """TC-DSPY-006: to_demos then to_pairs is the identity over example pairs."""
        pairs = [("q1", "a1"), ("q2", "a2")]
        demos = DSPyDemoMapper.to_demos(_fake_dspy_module(), pairs)
        assert all(isinstance(demo, FakeExample) for demo in demos)
        assert DSPyDemoMapper.to_pairs(demos) == pairs


class TestDSPyPromptOptimizer:
    """Covers the DSPy-backed optimizer and its degradation path."""

    def test_degrades_to_pure_few_shot_without_dspy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-DSPY-007: Without dspy the output equals the pure few-shot adapter's."""
        monkeypatch.setitem(sys.modules, "dspy", None)
        examples = [("finding", "resolution")]
        expected = FewShotPromptOptimizer().optimize("Critique", examples)
        assert DSPyPromptOptimizer().optimize("Critique", examples) == expected

    def test_uses_dspy_demonstrations_when_installed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-DSPY-008: With dspy installed, demos are normalized through dspy.Example."""
        monkeypatch.setitem(sys.modules, "dspy", _fake_dspy_module())
        examples = [("finding", "resolution")]
        expected = FewShotPromptOptimizer().optimize("Critique", examples)
        assert DSPyPromptOptimizer().optimize("Critique", examples) == expected

    def test_implements_prompt_optimizer_port(self) -> None:
        """TC-DSPY-009: The frameworks gateway is a concrete IPromptOptimizer implementation."""
        assert isinstance(DSPyPromptOptimizer(), IPromptOptimizer)

    def test_container_exposes_prompt_optimizer_injection_point(self) -> None:
        """TC-DSPY-010: DependencyContainer.prompt_optimizer provides the gateway."""
        from unittest.mock import MagicMock

        from agentic_workflow.application.ports.doc_io.document_io_gateway import DocumentIOGateway
        from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner
        from agentic_workflow.application.ports.repositories.checkpoint_repository import CheckpointRepository
        from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
        from agentic_workflow.frameworks.dependency_container import DependencyContainer

        container = DependencyContainer(
            pipeline_repo=MagicMock(spec=IPipelineRepository),
            checkpoint_repo=MagicMock(spec=CheckpointRepository),
            doc_io=MagicMock(spec=DocumentIOGateway),
            reasoner=MagicMock(spec=IAgentReasoner),
        )
        assert isinstance(container.prompt_optimizer, DSPyPromptOptimizer)
