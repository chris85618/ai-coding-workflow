"""Tests for the AssumptionRegistry domain service (FR-070, ADR-STR-029, ALG-019)."""

import deal
import pytest

from agentic_workflow.domain.services.assumption_registry import AssumptionRegistry
from agentic_workflow.domain.value_objects.assumption import Assumption


class TestAssumptionRegistry:
    """Covers registration, injection filtering and retro conversion."""

    def test_register_and_count(self) -> None:
        """TC-V2-020: Registration is idempotent per assumption id."""
        registry = AssumptionRegistry()
        assumption = Assumption(assumption_id="ASM-001", statement="No type: ignore")
        registry.register(assumption)
        registry.register(assumption)
        assert registry.count() == 1

    def test_active_statements_filters_inactive(self) -> None:
        """TC-V2-021: Only active assumptions are injected at START."""
        registry = AssumptionRegistry()
        registry.register(Assumption(assumption_id="ASM-001", statement="keep"))
        registry.register(Assumption(assumption_id="ASM-002", statement="drop", active=False))
        assert registry.active_statements() == ["keep"]

    def test_newest_statement_wins_for_same_id(self) -> None:
        """TC-V2-022: Re-registering an id replaces the statement."""
        registry = AssumptionRegistry()
        registry.register(Assumption(assumption_id="ASM-001", statement="old"))
        registry.register(Assumption(assumption_id="ASM-001", statement="new"))
        assert registry.active_statements() == ["new"]

    def test_from_lessons_numbers_and_skips_empty(self) -> None:
        """TC-V2-023: Retro lessons become numbered assumptions; blanks dropped."""
        assumptions = AssumptionRegistry.from_lessons(["lesson a", "", "lesson b"], start_index=5)
        assert [a.assumption_id for a in assumptions] == ["ASM-005", "ASM-006"]
        assert all(a.source_id == "phase10-retro" for a in assumptions)

    def test_from_lessons_rejects_zero_start_index(self) -> None:
        """TC-V2-024: Assumption numbering is 1-based."""
        with pytest.raises(deal.PreContractError):
            AssumptionRegistry.from_lessons(["x"], start_index=0)
