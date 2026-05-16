"""Coverage tests for ImpactAnalysis module."""

from agentic_workflow.domain.algorithms.impact_analysis import ImpactAnalysis


class TestImpactAnalysisCoverage:
    """Tests for ALG-002 ImpactAnalysis."""

    def test_cosmetic_on_empty_nodes(self) -> None:
        """TC-218: Cosmetic blast radius check."""
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [])
        assert result["severity"] == "COSMETIC"
        assert result["blast_radius"] == 0

    def test_returns_prompt_for_cosmetic(self) -> None:
        """TC-219: Prompt generation for cosmetic."""
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [])
        assert "Autonomously" in result["prompt_for_agent"]

    def test_result_structure(self) -> None:
        """TC-220: Impact analysis result keys."""
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [])
        assert "blast_radius" in result
        assert "affected_downstream" in result
        assert "inconsistent_upstream" in result
        assert "affected_lateral_ids" in result
