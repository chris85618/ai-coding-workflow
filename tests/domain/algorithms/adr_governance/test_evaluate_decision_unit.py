"""Tests for ADRGovernance.evaluate_decision_unit."""

from agentic_workflow.domain.algorithms.adr_governance import ADRGovernance


class TestEvaluateDecisionUnit:
    """Covers evaluate_decision_unit — 2 branches (True/False return)."""

    def test_all_conditions_met_returns_true(self) -> None:
        """TC-294: evaluate_decision_unit success path."""
        assert ADRGovernance.evaluate_decision_unit("We decided X", 0.9, True, True) is True

    def test_low_cohesiveness_returns_false(self) -> None:
        """TC-295: evaluate_decision_unit low cohesiveness."""
        assert ADRGovernance.evaluate_decision_unit("stmt", 0.5, True, True) is False

    def test_not_consequences_coupled_returns_false(self) -> None:
        """TC-296: evaluate_decision_unit decoupling."""
        assert ADRGovernance.evaluate_decision_unit("stmt", 0.9, False, True) is False

    def test_not_atomic_returns_false(self) -> None:
        """TC-297: evaluate_decision_unit non-atomic."""
        assert ADRGovernance.evaluate_decision_unit("stmt", 0.9, True, False) is False

    def test_all_false_returns_false(self) -> None:
        """TC-298: evaluate_decision_unit all false."""
        assert ADRGovernance.evaluate_decision_unit("stmt", 0.0, False, False) is False

    def test_boundary_cohesiveness_exactly_08(self) -> None:
        """TC-299: evaluate_decision_unit boundary 0.8."""
        # 0.8 >= 0.8 → True (if others also True)
        assert ADRGovernance.evaluate_decision_unit("stmt", 0.8, True, True) is True

    def test_boundary_cohesiveness_just_below_08(self) -> None:
        """TC-300: evaluate_decision_unit boundary 0.799."""
        assert ADRGovernance.evaluate_decision_unit("stmt", 0.799, True, True) is False
