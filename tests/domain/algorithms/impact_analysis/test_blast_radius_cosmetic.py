"""Tests for COSMETIC severity branch of calculate_blast_radius."""

from agentic_workflow.domain.algorithms.impact_analysis import ImpactAnalysis
from agentic_workflow.domain.algorithms.traceability_validator import TraceabilityNode


def _make_nodes(ids: list[str] | None = None) -> list[TraceabilityNode]:
    """Helper to create nodes."""
    nodes = []
    for nid in ids or []:
        nodes.append(TraceabilityNode(id=nid, type="FR", upstream=[], downstream=[]))
    return nodes


class TestBlastRadiusCosmetic:
    """Test COSMETIC severity branch of calculate_blast_radius."""

    def test_zero_blast_radius_is_cosmetic(self) -> None:
        """Verify zero radius results in COSMETIC severity."""
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [])
        assert result["blast_radius"] == 0
        assert result["severity"] == "COSMETIC"
        assert "Autonomously" in result["prompt_for_agent"]

    def test_result_structure_keys(self) -> None:
        """Verify output dictionary structure."""
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [])
        assert set(result.keys()) == {
            "blast_radius",
            "severity",
            "affected_downstream",
            "inconsistent_upstream",
            "affected_lateral_ids",
            "prompt_for_agent",
        }

    def test_all_lists_empty_when_no_injection(self) -> None:
        """Verify empty lists are returned by default."""
        result = ImpactAnalysis.calculate_blast_radius("FR-001", [])
        assert result["affected_downstream"] == []
        assert result["inconsistent_upstream"] == []
        assert result["affected_lateral_ids"] == []

    def test_empty_string_id_works(self) -> None:
        """Verify empty ID handles correctly."""
        result = ImpactAnalysis.calculate_blast_radius("", [])
        assert result["blast_radius"] == 0

    def test_nodes_accepted_without_error(self) -> None:
        """Verify node list acceptance."""
        nodes = _make_nodes(["FR-002", "FR-003"])
        result = ImpactAnalysis.calculate_blast_radius("FR-001", nodes)
        assert isinstance(result, dict)
