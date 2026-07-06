"""Tests for the RollbackPolicy domain service (FR-069, ADR-STR-029, ALG-018)."""

from agentic_workflow.domain.enums import FixedPointResult
from agentic_workflow.domain.services.rollback_policy import RollbackPolicy


class TestRollbackPolicy:
    """Covers the EC2 Neutrality degradation-path decision."""

    def test_diverging_triggers_rollback(self) -> None:
        """TC-V2-025: DIVERGING rolls back to the universal base."""
        decision = RollbackPolicy.decide(FixedPointResult.DIVERGING)
        assert decision.should_rollback is True
        assert decision.target_ref == "universal-base"
        assert "DIVERGING" in decision.reason

    def test_reached_does_not_rollback(self) -> None:
        """TC-V2-026: REACHED continues through the normal exit."""
        decision = RollbackPolicy.decide(FixedPointResult.REACHED)
        assert decision.should_rollback is False

    def test_not_reached_does_not_rollback(self) -> None:
        """TC-V2-027: NOT_REACHED keeps iterating without degradation."""
        assert RollbackPolicy.decide(FixedPointResult.NOT_REACHED).should_rollback is False

    def test_max_iterations_does_not_rollback(self) -> None:
        """TC-V2-028: MAX_ITERATIONS exits via alignment, not rollback."""
        assert RollbackPolicy.decide(FixedPointResult.MAX_ITERATIONS).should_rollback is False

    def test_custom_target_ref_is_respected(self) -> None:
        """TC-V2-029: An explicit target ref overrides the universal base."""
        decision = RollbackPolicy.decide(FixedPointResult.DIVERGING, target_ref="v1.2.3")
        assert decision.target_ref == "v1.2.3"
