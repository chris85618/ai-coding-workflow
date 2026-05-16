"""Tests for TechDebtManager priority assignment."""

from agentic_workflow.domain.algorithms.tech_debt_manager import TechDebtManager


class TestPriorityAssignment:
    """Tests for ALG-011 TechDebtManager priority logic."""

    def test_priority_quick_win(self) -> None:
        """TC-245: Priority for Quick Win."""
        assert TechDebtManager.assign_priority("Quick Win") == "P1"

    def test_priority_major_project(self) -> None:
        """TC-246: Priority for Major Project."""
        assert TechDebtManager.assign_priority("Major Project") == "P2"

    def test_priority_fill_in(self) -> None:
        """TC-247: Priority for Fill In."""
        assert TechDebtManager.assign_priority("Fill In") == "P3"

    def test_priority_thankless(self) -> None:
        """TC-248: Priority for Thankless."""
        assert TechDebtManager.assign_priority("Thankless Task") == "P3"

    def test_priority_unknown(self) -> None:
        """TC-249: Priority for Unknown quadrant."""
        assert TechDebtManager.assign_priority("Unknown") == "P3"
