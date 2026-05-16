"""Tests for TraceabilityValidator ID generation."""

from agentic_workflow.domain.algorithms.traceability_validator import TraceabilityValidator


class TestIdGeneration:
    """Tests for ALG-012 TraceabilityValidator ID generation logic."""

    def test_generate_next_id_empty(self) -> None:
        """TC-256: Next ID for empty list."""
        nid = TraceabilityValidator.generate_next_id("FR", [])
        assert nid == "FR-001"

    def test_generate_next_id_with_existing(self) -> None:
        """TC-257: Next ID with existing items."""
        nid = TraceabilityValidator.generate_next_id("FR", ["FR-003", "FR-010"])
        assert nid == "FR-011"

    def test_generate_next_id_ignores_invalid(self) -> None:
        """TC-258: Next ID ignores malformed existing."""
        nid = TraceabilityValidator.generate_next_id("FR", ["FR-abc", "FR-001"])
        assert nid == "FR-002"
