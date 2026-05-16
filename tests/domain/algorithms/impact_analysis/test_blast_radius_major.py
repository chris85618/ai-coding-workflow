"""Tests for MAJOR severity branch of calculate_blast_radius."""

from agentic_workflow.domain.algorithms.impact_analysis import ImpactAnalysis


class TestBlastRadiusMajor:
    """Test MAJOR severity branch of calculate_blast_radius."""

    def test_blast_11_is_major(self) -> None:
        """Verify blast radius 11 is MAJOR."""
        ids = [f"FR-{i:03d}" for i in range(11)]
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [], _downstream=ids)
        assert result["blast_radius"] == 11
        assert result["severity"] == "MAJOR"
        assert "M1-M4" in result["prompt_for_agent"]

    def test_blast_100_is_major(self) -> None:
        """Verify large blast radius handling."""
        ids = [f"X-{i}" for i in range(100)]
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [], _downstream=ids)
        assert result["severity"] == "MAJOR"

    def test_major_prompt_for_agent(self) -> None:
        """Verify prompt content for MAJOR severity."""
        ids = [str(i) for i in range(12)]
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [], _downstream=ids)
        assert "Execute M1-M4" in result["prompt_for_agent"]

    def test_affected_lists_preserved_in_result(self) -> None:
        """Verify input lists are preserved in result."""
        down = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [], _downstream=down)
        assert result["affected_downstream"] == down
        assert result["blast_radius"] == 11
