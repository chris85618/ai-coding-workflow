"""Test suite for exhaustive search algorithms (ALG-007)."""

from typing import Any

from agentic_workflow.domain.algorithms.exhaustive_search import ExhaustiveSearch


class TestExhaustiveSearch:
    """Test suite for exhaustive search algorithms."""

    def test_scan_directory_returns_list(self) -> None:
        """TC-007: Scan returns list."""
        result = ExhaustiveSearch.scan_directory("/some/path", "FR-")
        assert isinstance(result, list)

    def test_verify_orphan_status_no_references(self) -> None:
        """TC-008: Orphan if no references."""
        assert ExhaustiveSearch.verify_orphan_status("FR-001", "/path") is False

    def test_verify_orphan_status_logic(self, monkeypatch: Any) -> None:
        """TC-009: Reference check logic."""
        monkeypatch.setattr(ExhaustiveSearch, "scan_directory", lambda *_: ["a", "b"])
        assert ExhaustiveSearch.verify_orphan_status("FR-001", "/path") is True
