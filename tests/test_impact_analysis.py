"""Tests for ImpactAnalysis algorithm — 100% statement + branch coverage.

Consolidated from: test_impact_analysis.py, test_algorithms_coverage.py
Traceable to: FR-008, FR-009, FR-022, ALG-003.
"""

from agentic_workflow.domain.algorithms.impact_analysis import ImpactAnalysis
from agentic_workflow.domain.algorithms.traceability_validator import TraceabilityNode


# ── Helpers ────────────────────────────────────────────────────────────────────
def _make_nodes(ids: list[str] | None = None) -> list[TraceabilityNode]:
    """Helper to create nodes."""
    nodes = []
    for nid in ids or []:
        nodes.append(TraceabilityNode(id=nid, type="FR", upstream=[], downstream=[]))
    return nodes


# ── calculate_blast_radius — COSMETIC branch ───────────────────────────────────
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


# ── calculate_blast_radius — MINOR branch (1..3) ─────────────────────────────
class TestBlastRadiusMinor:
    """Test MINOR severity branch of calculate_blast_radius."""

    def test_blast_1_is_minor(self) -> None:
        """Verify blast radius 1 is MINOR."""
        result = ImpactAnalysis.calculate_blast_radius(
            "FR-001", [], _downstream=["FR-002"]
        )
        assert result["blast_radius"] == 1
        assert result["severity"] == "MINOR"
        assert "Autonomously" in result["prompt_for_agent"]

    def test_blast_3_is_minor(self) -> None:
        """Verify blast radius 3 is MINOR."""
        result = ImpactAnalysis.calculate_blast_radius(
            "FR-001", [], _downstream=["A", "B", "C"]
        )
        assert result["blast_radius"] == 3
        assert result["severity"] == "MINOR"

    def test_blast_2_from_upstream(self) -> None:
        """Verify upstream impact counts toward radius."""
        result = ImpactAnalysis.calculate_blast_radius(
            "FR-001", [], _upstream=["BG-001", "BG-002"]
        )
        assert result["severity"] == "MINOR"

    def test_blast_1_from_lateral(self) -> None:
        """Verify lateral impact counts toward radius."""
        result = ImpactAnalysis.calculate_blast_radius(
            "FR-001", [], _lateral=["ADR-GOV-001"]
        )
        assert result["severity"] == "MINOR"


# ── calculate_blast_radius — MODERATE branch (4..10) ─────────────────────────
class TestBlastRadiusModerate:
    """Test MODERATE severity branch of calculate_blast_radius."""

    def test_blast_4_is_moderate(self) -> None:
        """Verify blast radius 4 is MODERATE."""
        result = ImpactAnalysis.calculate_blast_radius(
            "FR-001", [], _downstream=["A", "B", "C", "D"]
        )
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
            "FR-001", [], _downstream=["A", "B"], _upstream=["C"], _lateral=["D", "E"]
        )
        assert result["blast_radius"] == 5
        assert result["severity"] == "MODERATE"


# ── calculate_blast_radius — MAJOR branch (>10) ───────────────────────────────
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
