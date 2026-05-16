"""Tests for MODERATE severity branch of calculate_blast_radius."""

from agentic_workflow.domain.algorithms.impact_analysis import ImpactAnalysis


class TestBlastRadiusModerate:
    """Test MODERATE severity branch of calculate_blast_radius."""

    def test_blast_4_is_moderate(self) -> None:
        """Verify blast radius 4 is MODERATE."""
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [], _downstream=["A", "B", "C", "D"])
        assert result["blast_radius"] == 4
        assert result["severity"] == "MODERATE"

    def test_blast_10_is_moderate(self) -> None:
        """Verify blast radius 10 is MODERATE."""
        ids = [f"FR-{i:03d}" for i in range(10)]
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [], _downstream=ids)
        assert result["blast_radius"] == 10
        assert result["severity"] == "MODERATE"
        assert "Autonomously" in result["prompt_for_agent"]

    def test_mixed_lists_sum_to_moderate(self) -> None:
        """Verify mixed list summation."""
        result = ImpactAnalysis.calculate_blast_radius(
            "FR-001",
            [],
            _downstream=["A", "B"],
            _upstream=["C"],
            _lateral=["D", "E"],
        )
        assert result["blast_radius"] == 5
        assert result["severity"] == "MODERATE"
