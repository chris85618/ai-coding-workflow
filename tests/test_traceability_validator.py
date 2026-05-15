"""Tests for TraceabilityValidator — 100% statement + branch coverage.
Consolidated from: test_algorithms_coverage.py
Traceable to: FR-004, ALG-005
"""
import pytest
from agentic_workflow.domain.algorithms.traceability_validator import (
    TraceabilityValidator,
    TraceabilityNode,
)


class TestValidateIdFormat:
    def test_valid_fr_id(self):
        assert TraceabilityValidator.validate_id_format("FR-001") is True

    def test_valid_bg_id(self):
        assert TraceabilityValidator.validate_id_format("BG-001") is True

    def test_valid_adr_str(self):
        assert TraceabilityValidator.validate_id_format("ADR-STR-001") is True

    def test_valid_tc(self):
        assert TraceabilityValidator.validate_id_format("TC-099") is True

    def test_invalid_missing_number(self):
        assert TraceabilityValidator.validate_id_format("FR-") is False

    def test_invalid_bad_prefix(self):
        assert TraceabilityValidator.validate_id_format("XX-001") is False

    def test_invalid_no_dash(self):
        assert TraceabilityValidator.validate_id_format("FR001") is False

    def test_invalid_empty_string(self):
        assert TraceabilityValidator.validate_id_format("") is False


class TestGenerateNextId:
    """Covers all branches: prefix match/no-match, num>max/num<=max, ValueError."""

    def test_no_existing_ids_starts_at_001(self):
        result = TraceabilityValidator.generate_next_id("FR", [])
        assert result == "FR-001"

    def test_existing_ids_increments(self):
        result = TraceabilityValidator.generate_next_id("FR", ["FR-001", "FR-002"])
        assert result == "FR-003"

    def test_skips_different_prefix(self):
        """Branch 39→38: nid does NOT start with prefix- → skip."""
        result = TraceabilityValidator.generate_next_id("FR", ["BG-001", "BG-005"])
        assert result == "FR-001"

    def test_num_not_greater_than_max(self):
        """Branch 42→38: num <= max_num (existing max stays)."""
        result = TraceabilityValidator.generate_next_id("FR", ["FR-005", "FR-003"])
        # max_num = 5, next = 6
        assert result == "FR-006"

    def test_value_error_continue(self):
        """Covers ValueError branch: non-numeric suffix."""
        # "FR-abc" → int("abc") raises ValueError → continue
        result = TraceabilityValidator.generate_next_id("FR", ["FR-abc", "FR-002"])
        assert result == "FR-003"

    def test_mixed_valid_invalid(self):
        result = TraceabilityValidator.generate_next_id("TC", ["TC-010", "TC-bad", "FR-020"])
        assert result == "TC-011"

    def test_three_digit_padding(self):
        result = TraceabilityValidator.generate_next_id("BG", ["BG-009"])
        assert result == "BG-010"


class TestDetectOrphans:
    """Covers all branches: needs_upstream/downstream True/False; links bypass."""

    def _node(self, id_, type_, upstream=None, downstream=None, links=None):
        return TraceabilityNode(
            id=id_, type=type_,
            upstream=upstream or [],
            downstream=downstream or [],
            links=links or {}
        )

    def test_bg_node_no_upstream_not_orphan(self):
        """BG doesn't need upstream — not an orphan."""
        node = self._node("BG-001", "BG", upstream=[], downstream=["FEA-001"])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "BG-001" not in orphans

    def test_tc_node_no_downstream_not_orphan(self):
        """TC doesn't need downstream — not an orphan."""
        node = self._node("TC-001", "TC", upstream=["SC-001"], downstream=[])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "TC-001" not in orphans

    def test_fr_no_upstream_no_links_is_orphan(self):
        """FR with no upstream and no exemption links → orphan."""
        node = self._node("FR-001", "FR", upstream=[], downstream=["UC-001"])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "FR-001" in orphans

    def test_fr_no_downstream_no_links_is_orphan(self):
        """FR with no downstream and no exemption links → orphan."""
        node = self._node("FR-001", "FR", upstream=["BG-001"], downstream=[])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "FR-001" in orphans

    def test_fr_with_justifies_link_bypasses_upstream_check(self):
        """Branch 59→61: needs_upstream True, no upstream, BUT has justifies link → NOT orphan."""
        node = self._node("FR-001", "FR",
                          upstream=[],
                          downstream=["UC-001"],
                          links={"justifies": ["ADR-GOV-001"]})
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "FR-001" not in orphans

    def test_fr_with_mitigates_link_bypasses_downstream_check(self):
        """Branch 62→52: needs_downstream True, no downstream, BUT has mitigates link → NOT orphan."""
        node = self._node("FR-001", "FR",
                          upstream=["BG-001"],
                          downstream=[],
                          links={"mitigates": ["RISK-001"]})
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "FR-001" not in orphans

    def test_fully_connected_fr_not_orphan(self):
        node = self._node("FR-001", "FR",
                          upstream=["BG-001"], downstream=["UC-001"])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert orphans == []

    def test_empty_nodes_list(self):
        assert TraceabilityValidator.detect_orphans([]) == []

    def test_s_node_no_upstream_not_orphan(self):
        """S type doesn't need upstream."""
        node = self._node("S-001", "S", upstream=[], downstream=["FEA-001"])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert "S-001" not in orphans

    def test_deduplication_in_result(self):
        """Node both missing upstream and downstream → appears once."""
        node = self._node("FR-001", "FR", upstream=[], downstream=[])
        orphans = TraceabilityValidator.detect_orphans([node])
        assert orphans.count("FR-001") == 1


class TestRunValidation:
    def test_returns_passed_true(self):
        result = TraceabilityValidator.run_validation("FR-001 BG-001")
        assert result["passed"] is True

    def test_empty_content(self):
        result = TraceabilityValidator.run_validation("")
        assert result["passed"] is True

    def test_result_structure(self):
        result = TraceabilityValidator.run_validation("TC-001")
        assert "orphans" in result
        assert "invalid_ids" in result
        assert "next_action" in result
