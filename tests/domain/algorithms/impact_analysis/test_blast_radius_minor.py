"""Tests for MINOR severity branch of calculate_blast_radius."""

from agentic_workflow.domain.algorithms.impact_analysis import ImpactAnalysis


class TestBlastRadiusMinor:
    """Test MINOR severity branch of calculate_blast_radius."""

    def test_blast_1_is_minor(self) -> None:
        """Verify blast radius 1 is MINOR."""
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [], _downstream=["FR-002"])
        assert result["blast_radius"] == 1
        assert result["severity"] == "MINOR"
        assert "Autonomously" in result["prompt_for_agent"]

    def test_blast_3_is_minor(self) -> None:
        """Verify blast radius 3 is MINOR."""
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [], _downstream=["A", "B", "C"])
        assert result["blast_radius"] == 3
        assert result["severity"] == "MINOR"

    def test_blast_2_from_upstream(self) -> None:
        """Verify upstream impact counts toward radius."""
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [], _upstream=["BG-001", "BG-002"])
        assert result["severity"] == "MINOR"

    def test_blast_1_from_lateral(self) -> None:
        """Verify lateral impact counts toward radius."""
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [], _lateral=["ADR-GOV-001"])
        assert result["severity"] == "MINOR"
