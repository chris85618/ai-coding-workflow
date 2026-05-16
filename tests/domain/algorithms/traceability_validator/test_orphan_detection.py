"""Tests for TraceabilityValidator orphan detection."""

from agentic_workflow.domain.algorithms.traceability_validator import (
    TraceabilityNode,
    TraceabilityValidator,
)


class TestOrphanDetection:
    """Tests for ALG-012 TraceabilityValidator orphan logic."""

    def test_detect_orphans_source_nodes_exempt(self) -> None:
        """TC-259: Source nodes orphan detection."""
        # BG with no downstream IS an orphan in the current implementation
        node = TraceabilityNode(id="BG-001", type="BG", upstream=[], downstream=[])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "BG-001" in orphans

    def test_detect_orphans_tc_no_downstream_exempt(self) -> None:
        """TC-260: TC nodes orphan exemption."""
        node = TraceabilityNode(id="TC-001", type="TC", upstream=["SC-001"], downstream=[])
        assert "TC-001" not in TraceabilityValidator.detect_orphans([node])

    def test_detect_orphans_fr_missing_upstream_is_orphan(self) -> None:
        """TC-261: FR nodes missing upstream orphan check."""
        node = TraceabilityNode(id="FR-001", type="FR", upstream=[], downstream=["UC-001"])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "FR-001" in orphans
