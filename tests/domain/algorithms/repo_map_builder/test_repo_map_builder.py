"""ALG-006 Domain Algorithm interface."""

from typing import Any

from agentic_workflow.domain.algorithms.repo_map_builder import RepoMapBuilder
from agentic_workflow.domain.value_objects import RepoMap


class TestRepoMapBuilder:
    """ALG-006 Domain Algorithm interface."""

    def setup_method(self) -> None:
        """Initialize algorithm reference."""
        self.algo = RepoMapBuilder

    def test_class_constants_exist(self) -> None:
        """TC-206: RepoMap constants check."""
        assert self.algo.CHARS_PER_TOKEN == 4
        assert self.algo.PAGERANK_DAMPING == 0.85
        assert self.algo.PAGERANK_ITERATIONS == 20

    def test_extract_symbols_ast_class(self) -> None:
        """TC-207: AST class extraction."""
        source = "class Foo:\n    pass\n"
        symbols = self.algo.extract_symbols_ast("test.py", source)
        assert any(s.name == "Foo" and s.kind == "class" for s in symbols)

    def test_extract_symbols_ast_function(self) -> None:
        """TC-208: AST function extraction."""
        source = "def bar(x, y):\n    pass\n"
        symbols = self.algo.extract_symbols_ast("test.py", source)
        assert any(s.name == "bar" and s.kind == "function" for s in symbols)

    def test_extract_symbols_ast_syntax_error_returns_empty(self) -> None:
        """TC-209: AST syntax error handling."""
        symbols = self.algo.extract_symbols_ast("bad.py", "def (broken:")
        assert symbols == []

    def test_build_import_graph_empty(self) -> None:
        """TC-210: Empty import graph."""
        graph = self.algo.build_import_graph([], "/tmp")
        assert graph == {}

    def test_pagerank_empty_graph(self) -> None:
        """TC-211: PageRank on empty graph."""
        result = self.algo.pagerank({})
        assert result == {}

    def test_pagerank_single_node(self) -> None:
        """TC-212: PageRank single node."""
        result = self.algo.pagerank({"a": []})
        assert "a" in result

    def test_build_returns_repo_map(self, tmp_path: Any) -> None:
        """TC-213: Build RepoMap from directory."""
        (tmp_path / "mod.py").write_text("def foo(): pass\n")
        result = self.algo.build(str(tmp_path), 500)
        assert isinstance(result, RepoMap)
        assert result.token_count <= 500

    def test_build_empty_dir_returns_empty_map(self, tmp_path: Any) -> None:
        """TC-214: Build RepoMap from empty directory."""
        result = self.algo.build(str(tmp_path), 500)
        assert result.token_count == 0
        assert result.symbols == ()
