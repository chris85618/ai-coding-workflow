"""Tests for the GovernanceCostModel domain service (FR-071, ADR-STR-029, ALG-017)."""

from agentic_workflow.domain.services.governance_cost_model import GovernanceCostModel


class TestGovernanceCostModel:
    """Covers kappa accumulation and delayed-HITL triggering."""

    def test_accumulated_cost_formula(self) -> None:
        """TC-V2-016: kappa = iterations * 1.0 + debts * 0.5."""
        assert GovernanceCostModel.accumulated_cost(4, 6) == 7.0

    def test_no_hitl_below_threshold(self) -> None:
        """TC-V2-017: Routine work below threshold never summons a human."""
        assert GovernanceCostModel.should_trigger_hitl(2, 2, diverging=False) is False

    def test_hitl_when_cost_exceeds_threshold(self) -> None:
        """TC-V2-018: kappa above HITL_THRESHOLD triggers delayed intervention."""
        assert GovernanceCostModel.should_trigger_hitl(11, 0, diverging=False) is True

    def test_hitl_always_on_divergence(self) -> None:
        """TC-V2-019: DIVERGING is an unresolvable conflict — always HITL."""
        assert GovernanceCostModel.should_trigger_hitl(0, 0, diverging=True) is True
