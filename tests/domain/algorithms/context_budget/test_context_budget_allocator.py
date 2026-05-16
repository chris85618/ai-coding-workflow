"""ALG-007 OO class interface."""

import pytest

from agentic_workflow.domain.value_objects import RepoMap


class TestContextBudgetAllocator:
    """ALG-007 OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        from agentic_workflow.domain.algorithms.context_budget import (
            ContextBudgetAllocator,
        )

        self.cls = ContextBudgetAllocator

    def test_class_constants_exist(self) -> None:
        """TC-190: Budget constants check."""
        assert self.cls.CHARS_PER_TOKEN == 4
        assert self.cls.TASK_BUDGET_FRACTION == 0.5
        assert self.cls.FILES_BUDGET_FRACTION == 0.7

    def test_estimate_tokens_minimum_one(self) -> None:
        """TC-191: Minimum token estimation."""
        assert self.cls.estimate_tokens("") == 1

    def test_estimate_tokens_calculation(self) -> None:
        """TC-192: Token calculation logic."""
        text = "a" * 400
        assert self.cls.estimate_tokens(text) == 100

    def test_allocate_respects_budget(self) -> None:
        """TC-193: Budget allocation logic."""
        repo_map = RepoMap(symbols=(), token_count=0, file_ranks={})
        result = self.cls.allocate(1000, repo_map, [], "hello world task context")
        assert result.total_tokens <= 1000

    def test_allocate_invalid_budget_raises(self) -> None:
        """TC-194: Zero budget detection."""
        import icontract

        with pytest.raises(icontract.ViolationError):
            self.cls.allocate(0, RepoMap(symbols=(), token_count=0, file_ranks={}), [], "task")
