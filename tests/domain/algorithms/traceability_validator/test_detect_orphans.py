"""Covers all branches: needs_upstream/downstream True/False; links bypass."""

from agentic_workflow.domain.algorithms.traceability_validator import (
    TraceabilityNode,
    TraceabilityValidator,
)


class TestDetectOrphans:
    """Covers all branches: needs_upstream/downstream True/False; links bypass."""

    def _node(
        self,
        id_: str,
        type_: str,
        upstream: list[str] | None = None,
        downstream: list[str] | None = None,
        links: dict[str, list[str]] | None = None,
    ) -> TraceabilityNode:
        """Helper to create node."""
        return TraceabilityNode(
            id=id_,
            type=type_,
            upstream=upstream or [],
            downstream=downstream or [],
            links=links or {},
        )

    def test_bg_node_no_upstream_not_orphan(self) -> None:
        """BG doesn't need upstream — not an orphan."""
        node = self._node("BG-001", "BG", upstream=[], downstream=["FEA-001"])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "BG-001" not in orphans

    def test_tc_node_no_downstream_not_orphan(self) -> None:
        """TC doesn't need downstream — not an orphan."""
        node = self._node("TC-001", "TC", upstream=["SC-001"], downstream=[])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "TC-001" not in orphans

    def test_fr_no_upstream_no_links_is_orphan(self) -> None:
        """FR with no upstream and no exemption links → orphan."""
        node = self._node("FR-001", "FR", upstream=[], downstream=["UC-001"])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "FR-001" in orphans

    def test_fr_no_downstream_no_links_is_orphan(self) -> None:
        """FR with no downstream and no exemption links → orphan."""
        node = self._node("FR-001", "FR", upstream=["BG-001"], downstream=[])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "FR-001" in orphans

    def test_fr_with_justifies_link_bypasses_upstream_check(self) -> None:
        """Branch 59→61: has justifies link → NOT orphan."""
        node = self._node(
            "FR-001",
            "FR",
            upstream=[],
            downstream=["UC-001"],
            links={"justifies": ["ADR-GOV-001"]},
        )
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "FR-001" not in orphans

    def test_fr_with_mitigates_link_bypasses_downstream_check(self) -> None:
        """Branch 62→52: has mitigates link → NOT orphan."""
        node = self._node(
            "FR-001",
            "FR",
            upstream=["BG-001"],
            downstream=[],
            links={"mitigates": ["RISK-001"]},
        )
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "FR-001" not in orphans

    def test_fully_connected_fr_not_orphan(self) -> None:
        """Verify fully connected node."""
        node = self._node("FR-001", "FR", upstream=["BG-001"], downstream=["UC-001"])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert orphans == []

    def test_empty_nodes_list(self) -> None:
        """Verify empty list."""
        assert TraceabilityValidator.detect_orphans([]) == []

    def test_s_node_no_upstream_not_orphan(self) -> None:
        """S type doesn't need upstream."""
        node = self._node("S-001", "S", upstream=[], downstream=["FEA-001"])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "S-001" not in orphans

    def test_deduplication_in_result(self) -> None:
        """Node both missing upstream and downstream → appears once."""
        node = self._node("FR-001", "FR", upstream=[], downstream=[])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert orphans.count("FR-001") == 1
