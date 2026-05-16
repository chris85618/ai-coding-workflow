"""Tests for directory scanning logic."""

from agentic_workflow.domain.algorithms.exhaustive_search import ExhaustiveSearch


class TestScanDirectory:
    """Tests for directory scanning logic."""

    def test_scan_directory_returns_list(self) -> None:
        """TC-007: Scan returns list."""
        result = ExhaustiveSearch.scan_directory("/some/path", "FR-")
        assert isinstance(result, list)
