"""Tests for TechDebtManager RICE score calculation."""

from agentic_workflow.domain.algorithms.tech_debt_manager import TechDebtManager


class TestRiceScoreCalculation:
    """Tests for ALG-011 TechDebtManager RICE score logic."""

    def test_rice_normal(self) -> None:
        """TC-239: RICE score calculation."""
        score = TechDebtManager.calculate_rice_score(100, 2.0, 0.8, 5.0)
        assert abs(score - 32.0) < 0.001

    def test_rice_zero_effort(self) -> None:
        """TC-240: RICE with zero effort."""
        assert TechDebtManager.calculate_rice_score(100, 2.0, 0.8, 0) == 0.0
