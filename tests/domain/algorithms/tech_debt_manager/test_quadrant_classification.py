"""Tests for TechDebtManager quadrant classification."""

from agentic_workflow.domain.algorithms.tech_debt_manager import TechDebtManager


class TestQuadrantClassification:
    """Tests for ALG-011 TechDebtManager quadrant logic."""

    def test_quadrant_quick_win(self) -> None:
        """TC-241: Quick Win classification."""
        assert TechDebtManager.classify_quadrant(3.0, 1.0) == "Quick Win"

    def test_quadrant_major_project(self) -> None:
        """TC-242: Major Project classification."""
        assert TechDebtManager.classify_quadrant(3.0, 3.0) == "Major Project"

    def test_quadrant_fill_in(self) -> None:
        """TC-243: Fill In classification."""
        assert TechDebtManager.classify_quadrant(1.0, 1.0) == "Fill In"

    def test_quadrant_thankless(self) -> None:
        """TC-244: Thankless Task classification."""
        assert TechDebtManager.classify_quadrant(1.0, 3.0) == "Thankless Task"
