"""Tests for the FewShotPromptOptimizer adapter (FR-075, ADR-STR-031)."""

from agentic_workflow.adapters.prompting.few_shot_prompt_optimizer import FewShotPromptOptimizer
from agentic_workflow.application.ports.gateways.prompt_optimizer import IPromptOptimizer


class TestFewShotPromptOptimizer:
    """Covers the pure-string bootstrap few-shot degradation path."""

    def test_no_examples_returns_base_prompt_unchanged(self) -> None:
        """TC-DSPY-001: With no demonstrations, the base prompt passes through untouched."""
        assert FewShotPromptOptimizer().optimize("Critique stage content", []) == "Critique stage content"

    def test_examples_are_appended_in_order(self) -> None:
        """TC-DSPY-002: Every demonstration is appended after the base prompt, in order."""
        examples = [("bad import", "move to adapter"), ("magic number", "extract constant")]
        optimized = FewShotPromptOptimizer().optimize("Critique stage content", examples)
        assert optimized.startswith("Critique stage content")
        first = optimized.index("Input: bad import")
        second = optimized.index("Input: magic number")
        assert first < second
        assert "Expected: move to adapter" in optimized
        assert "Expected: extract constant" in optimized

    def test_implements_prompt_optimizer_port(self) -> None:
        """TC-DSPY-003: The adapter is a concrete IPromptOptimizer implementation."""
        assert isinstance(FewShotPromptOptimizer(), IPromptOptimizer)
