"""Tests for orphan status verification logic."""

from typing import Any

from agentic_workflow.domain.algorithms.exhaustive_search import ExhaustiveSearch


class TestVerifyOrphanStatus:
    """Tests for orphan status verification logic."""

    def test_verify_orphan_status_no_references(self) -> None:
        """TC-008: Orphan if no references."""
        # scan_directory returns [] so len==0 → not referenced → False
        assert ExhaustiveSearch.verify_orphan_status("FR-001", "/path") is False

    def test_verify_orphan_status_logic(self, monkeypatch: Any) -> None:
        """TC-009: Reference check logic."""
        monkeypatch.setattr(ExhaustiveSearch, "scan_directory", lambda *_: ["a", "b"])
        assert ExhaustiveSearch.verify_orphan_status("FR-001", "/path") is True
