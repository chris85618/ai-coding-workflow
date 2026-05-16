"""Test _glob_count utility."""

from pathlib import Path

from agentic_workflow.domain.algorithms.pipeline_completeness import PipelineCompletenessChecker


class TestCheckGlobCount:
    """Test _glob_count utility."""

    def test_no_matches_returns_false(self, tmp_path: Path) -> None:
        """Verify glob with no matches returns False."""
        assert PipelineCompletenessChecker(tmp_path)._glob_count("*.xyz") is False

    def test_with_match_returns_true(self, tmp_path: Path) -> None:
        """Verify glob with matches returns True."""
        (tmp_path / "file.md").write_text("x", encoding="utf-8")
        assert PipelineCompletenessChecker(tmp_path)._glob_count("*.md") is True
