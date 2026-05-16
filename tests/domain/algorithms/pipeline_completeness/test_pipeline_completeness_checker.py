"""Pipeline completeness OO class interface."""

from typing import Any


class TestPipelineCompletenessChecker:
    """Pipeline completeness OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        from agentic_workflow.domain.algorithms.pipeline_completeness import (
            PipelineCompletenessChecker,
        )

        self.cls = PipelineCompletenessChecker

    def test_empty_dir_returns_zero_score(self, tmp_path: Any) -> None:
        """TC-195: Empty directory score check."""
        checker = self.cls(tmp_path)
        result = checker.calculate()
        assert result["completeness_score"] == 0
        assert result["completeness_ratio"] == 0.0

    def test_greenfield_path_with_no_src(self, tmp_path: Any) -> None:
        """TC-196: Path A detection."""
        checker = self.cls(tmp_path)
        result = checker.calculate()
        assert result["decision"] == "Path A (Greenfield)"

    def test_brownfield_path_with_src(self, tmp_path: Any) -> None:
        """TC-197: Path B detection."""
        src = tmp_path / "src" / "main.py"
        src.parent.mkdir(parents=True)
        src.write_text("# code")
        checker = self.cls(tmp_path)
        result = checker.calculate()
        assert result["decision"] == "Path B (Brownfield)"

    def test_checks_breakdown_length(self, tmp_path: Any) -> None:
        """TC-198: Checks breakdown count."""
        checker = self.cls(tmp_path)
        result = checker.calculate()
        assert len(result["checks_breakdown"]) == 10

    def test_file_exists_and_contains_method(self, tmp_path: Any) -> None:
        """TC-199: File content check helper."""
        f = tmp_path / "test.md"
        f.write_text("BG-001 content")
        checker = self.cls(tmp_path)
        assert checker._file_exists_and_contains("test.md", "BG-001") is True
        assert checker._file_exists_and_contains("test.md", "FR-001") is False

    def test_glob_count_method(self, tmp_path: Any) -> None:
        """TC-200: Glob count helper."""
        checker = self.cls(tmp_path)
        assert checker._glob_count("*.md") is False
        (tmp_path / "file.md").write_text("x")
        assert checker._glob_count("*.md") is True
