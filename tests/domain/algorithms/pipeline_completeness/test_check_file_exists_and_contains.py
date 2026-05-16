"""Test _file_exists_and_contains utility."""

from pathlib import Path

from agentic_workflow.domain.algorithms.pipeline_completeness import PipelineCompletenessChecker


class TestCheckFileExistsAndContains:
    """Test _file_exists_and_contains utility."""

    def test_file_missing_returns_false(self, tmp_path: Path) -> None:
        """Verify missing file returns False."""
        assert PipelineCompletenessChecker(tmp_path)._file_exists_and_contains("missing.md") is False

    def test_directory_not_file_returns_false(self, tmp_path: Path) -> None:
        """Verify directory path returns False."""
        d = tmp_path / "adir"
        d.mkdir()
        assert PipelineCompletenessChecker(tmp_path)._file_exists_and_contains("adir") is False

    def test_file_exists_no_content_check(self, tmp_path: Path) -> None:
        """Verify existence check without content requirement."""
        (tmp_path / "f.md").write_text("x", encoding="utf-8")
        assert PipelineCompletenessChecker(tmp_path)._file_exists_and_contains("f.md") is True

    def test_file_contains_string(self, tmp_path: Path) -> None:
        """Verify content matching."""
        (tmp_path / "f.md").write_text("BG-001 here", encoding="utf-8")
        assert PipelineCompletenessChecker(tmp_path)._file_exists_and_contains("f.md", "BG-001") is True

    def test_file_missing_string(self, tmp_path: Path) -> None:
        """Verify non-matching content returns False."""
        (tmp_path / "f.md").write_text("nothing", encoding="utf-8")
        assert PipelineCompletenessChecker(tmp_path)._file_exists_and_contains("f.md", "BG-001") is False
