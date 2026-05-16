"""Cover missing branches in ALG-006."""

from pathlib import Path

from agentic_workflow.domain.algorithms.repo_map_builder import RepoMapBuilder


class TestRepoMapBuilderBranches:
    """Cover missing branches in ALG-006."""

    def test_empty_directory_returns_empty(self, tmp_path: Path) -> None:
        """No Python files ->empty RepoMap."""
        result = RepoMapBuilder.build(str(tmp_path), 1000)
        assert result.token_count == 0
        assert len(result.symbols) == 0

    def test_single_file(self, tmp_path: Path) -> None:
        """Single file produces symbols."""
        (tmp_path / "a.py").write_text("class A:\n    pass\n\ndef foo(): pass\n")
        result = RepoMapBuilder.build(str(tmp_path), 1000)
        assert len(result.symbols) >= 2

    def test_pagerank_empty(self) -> None:
        """PageRank on empty graph returns empty dict."""
        ranks = RepoMapBuilder.pagerank({})
        assert ranks == {}

    def test_extract_symbols_syntax_error(self) -> None:
        """Syntax error in file returns empty symbol list."""
        symbols = RepoMapBuilder.extract_symbols_ast("bad.py", "def :(")
        assert symbols == []

    def test_import_graph_unreadable_file(self, tmp_path: Path) -> None:
        """Import graph handles missing files gracefully."""
        fake = str(tmp_path / "nonexistent.py")
        graph = RepoMapBuilder.build_import_graph([fake], str(tmp_path))
        assert fake in graph

    def test_budget_prunes_symbols(self, tmp_path: Path) -> None:
        """Token budget limits symbol count (INV-024)."""
        for i in range(20):
            (tmp_path / f"mod_{i:02d}.py").write_text(
                f"class BigClass{i}:\n    def method(self): pass\n\n" * 10,
            )
        result = RepoMapBuilder.build(str(tmp_path), 50)
        assert result.token_count <= 50
