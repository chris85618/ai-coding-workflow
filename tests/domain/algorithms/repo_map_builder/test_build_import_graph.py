"""Unit tests for import graph builder."""

from pathlib import Path

from agentic_workflow.domain.algorithms.repo_map_builder import RepoMapBuilder


class TestBuildImportGraph:
    """Unit tests for import graph builder."""

    def test_oserror_on_file_read_is_skipped(self, tmp_path: Path) -> None:
        """L94-95: OSError when reading a file → skip that file, continue."""
        f = tmp_path / "module.py"
        f.write_text("import os\n")
        fake_file = str(tmp_path / "unreadable.py")
        # Pass both files; unreadable.py doesn't exist → OSError
        result = RepoMapBuilder.build_import_graph([str(f), fake_file], str(tmp_path))
        # Should contain entry for f, may or may not for fake_file
        assert str(f) in result

    def test_simple_import_detected(self, tmp_path: Path) -> None:
        """Simple 'import X' form is detected."""
        a = tmp_path / "alpha.py"
        b = tmp_path / "beta.py"
        a.write_text("import beta\n")
        b.write_text("def b(): pass\n")
        result = RepoMapBuilder.build_import_graph([str(a), str(b)], str(tmp_path))
        assert str(b) in result[str(a)]

    def test_from_import_detected(self, tmp_path: Path) -> None:
        """'from X import Y' form is detected."""
        a = tmp_path / "gamma.py"
        b = tmp_path / "delta.py"
        a.write_text("from delta import something\n")
        b.write_text("def something(): pass\n")
        result = RepoMapBuilder.build_import_graph([str(a), str(b)], str(tmp_path))
        assert str(b) in result[str(a)]

    def test_no_imports_yields_empty_adjacency(self, tmp_path: Path) -> None:
        """File with no imports → empty adjacency list."""
        f = tmp_path / "standalone.py"
        f.write_text("x = 1\n")
        result = RepoMapBuilder.build_import_graph([str(f)], str(tmp_path))
        assert result[str(f)] == []
