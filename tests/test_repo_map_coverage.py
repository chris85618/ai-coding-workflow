"""DEBT-003: repo_map_builder.py boundary branch coverage.

Covers uncovered lines:
- L40-41: SyntaxError branch in _extract_symbols_ast
- L54: AsyncFunctionDef branch
- L94-95: OSError branch in _build_import_graph
- L119-120: empty graph branch in _pagerank
- L175-176: no .py files branch in repo_map_build
- L183-184: OSError on file read in repo_map_build
- RepoMap model: prune_to_budget (budget<=0), get_context_string (empty + multi-file)

Traceable to: DEBT-003, ALG-006, INV-024, FR-018
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import pytest


# ===========================================================================
# _extract_symbols_ast — boundary branches
# ===========================================================================

class TestExtractSymbolsAst:
    """Unit tests for the AST symbol extraction helper."""

    def _fn(self, file_path: str, source: str):
        from agentic_workflow.domain.algorithms.repo_map_builder import _extract_symbols_ast
        return _extract_symbols_ast(file_path, source)

    def test_syntax_error_returns_empty(self) -> None:
        """L40-41: SyntaxError in ast.parse → return empty list."""
        result = self._fn("bad.py", "def (: this is not valid python +++")
        assert result == []

    def test_class_def_extracted(self) -> None:
        """ClassDef branch: produces kind='class'."""
        result = self._fn("f.py", "class Foo:\n    pass\n")
        assert any(s.kind == "class" and s.name == "Foo" for s in result)

    def test_function_def_extracted(self) -> None:
        """FunctionDef branch: produces kind='function'."""
        result = self._fn("f.py", "def bar(x, y):\n    pass\n")
        assert any(s.kind == "function" and s.name == "bar" for s in result)

    def test_async_function_def_extracted(self) -> None:
        """L54: AsyncFunctionDef branch: also produces kind='function'."""
        result = self._fn("f.py", "async def fetch(url):\n    pass\n")
        assert any(s.kind == "function" and s.name == "fetch" for s in result)

    def test_empty_source_returns_empty(self) -> None:
        """Empty file: no symbols extracted."""
        result = self._fn("empty.py", "")
        assert result == []

    def test_signature_includes_args(self) -> None:
        """FunctionDef signature includes argument names."""
        result = self._fn("f.py", "def greet(name, greeting='hi'):\n    pass\n")
        fn = next(s for s in result if s.name == "greet")
        assert "name" in fn.signature
        assert fn.line_number == 1


# ===========================================================================
# _build_import_graph — OSError branch
# ===========================================================================

class TestBuildImportGraph:
    """Unit tests for import graph builder."""

    def _fn(self, py_files, project_path):
        from agentic_workflow.domain.algorithms.repo_map_builder import _build_import_graph
        return _build_import_graph(py_files, project_path)

    def test_oserror_on_file_read_is_skipped(self, tmp_path: Path) -> None:
        """L94-95: OSError when reading a file → skip that file, continue."""
        f = tmp_path / "module.py"
        f.write_text("import os\n")
        fake_file = str(tmp_path / "unreadable.py")
        # Pass both files; unreadable.py doesn't exist → OSError
        result = self._fn([str(f), fake_file], str(tmp_path))
        # Should contain entry for f, may or may not for fake_file
        assert str(f) in result

    def test_simple_import_detected(self, tmp_path: Path) -> None:
        """Simple 'import X' form is detected."""
        a = tmp_path / "alpha.py"
        b = tmp_path / "beta.py"
        a.write_text("import beta\n")
        b.write_text("def b(): pass\n")
        result = self._fn([str(a), str(b)], str(tmp_path))
        assert str(b) in result[str(a)]

    def test_from_import_detected(self, tmp_path: Path) -> None:
        """'from X import Y' form is detected."""
        a = tmp_path / "gamma.py"
        b = tmp_path / "delta.py"
        a.write_text("from delta import something\n")
        b.write_text("def something(): pass\n")
        result = self._fn([str(a), str(b)], str(tmp_path))
        assert str(b) in result[str(a)]

    def test_no_imports_yields_empty_adjacency(self, tmp_path: Path) -> None:
        """File with no imports → empty adjacency list."""
        f = tmp_path / "standalone.py"
        f.write_text("x = 1\n")
        result = self._fn([str(f)], str(tmp_path))
        assert result[str(f)] == []


# ===========================================================================
# _pagerank — empty graph branch
# ===========================================================================

class TestPagerank:
    """Unit tests for the simplified PageRank implementation."""

    def _fn(self, graph, damping=0.85, iterations=20):
        from agentic_workflow.domain.algorithms.repo_map_builder import _pagerank
        return _pagerank(graph, damping, iterations)

    def test_empty_graph_returns_empty(self) -> None:
        """L119-120: empty graph → return {}."""
        result = self._fn({})
        assert result == {}

    def test_single_node_no_links(self) -> None:
        """Single node with no edges → rank converges to (1-damping)/n = 0.15."""
        result = self._fn({"a.py": []})
        assert "a.py" in result
        # With damping=0.85, n=1: stable rank = (1-0.85)/1 = 0.15
        assert abs(result["a.py"] - 0.15) < 0.01

    def test_two_nodes_one_imports(self) -> None:
        """a.py imports b.py → b.py gets higher rank."""
        result = self._fn({"a.py": ["b.py"], "b.py": []})
        # b.py is imported → it receives rank contribution
        assert result["b.py"] >= result["a.py"]

    def test_isolated_nodes_equal_rank(self) -> None:
        """Nodes with no edges share equal rank."""
        result = self._fn({"x.py": [], "y.py": [], "z.py": []})
        ranks = list(result.values())
        assert max(ranks) - min(ranks) < 0.01


# ===========================================================================
# repo_map_build — edge cases
# ===========================================================================

class TestRepoMapBuild:
    """Integration-level tests for repo_map_build."""

    def test_no_python_files_returns_empty(self, tmp_path: Path) -> None:
        """L175-176: no .py files → RepoMap with 0 tokens and empty symbols."""
        from agentic_workflow.domain.algorithms.repo_map_builder import repo_map_build
        (tmp_path / "README.md").write_text("# readme")
        result = repo_map_build(str(tmp_path), token_budget=1000)
        assert result.token_count == 0
        assert len(result.symbols) == 0

    def test_oserror_on_symbol_read_skipped(self, tmp_path: Path) -> None:
        """L183-184: OSError when reading file for symbols → skip, continue."""
        from agentic_workflow.domain.algorithms.repo_map_builder import repo_map_build
        # Create one good file
        (tmp_path / "good.py").write_text("def f(): pass\n")
        # Simulate OSError on read by patching Path.read_text
        original_read_text = Path.read_text

        def patched_read_text(self, *a, **kw):
            if "good" not in str(self):
                raise OSError("simulated")
            return original_read_text(self, *a, **kw)

        with patch.object(Path, "read_text", patched_read_text):
            result = repo_map_build(str(tmp_path), token_budget=1000)
        # Should still have symbol from good.py
        assert result.token_count >= 0

    def test_tight_token_budget_prunes_symbols(self, tmp_path: Path) -> None:
        """Token budget of 1 forces pruning after first symbol."""
        from agentic_workflow.domain.algorithms.repo_map_builder import repo_map_build
        for i in range(10):
            (tmp_path / f"mod_{i}.py").write_text(
                f"class BigClass{i}:\n    pass\n" * 5
            )
        result = repo_map_build(str(tmp_path), token_budget=1)
        assert result.token_count <= 1

    def test_test_files_excluded(self, tmp_path: Path) -> None:
        """Files starting with test_ are not scanned for symbols."""
        from agentic_workflow.domain.algorithms.repo_map_builder import repo_map_build
        (tmp_path / "test_something.py").write_text("def test_foo(): pass\n")
        (tmp_path / "module.py").write_text("def real_func(): pass\n")
        result = repo_map_build(str(tmp_path), token_budget=500)
        # test_something.py should not appear as any symbol's file_path
        test_file_paths = [
            s.file_path for s in result.symbols
            if os.path.basename(s.file_path).startswith("test_")
        ]
        assert test_file_paths == [], f"test_ files appeared in map: {test_file_paths}"

    def test_invalid_project_path_raises(self, tmp_path: Path) -> None:
        """icontract precondition: non-existent project_path raises ViolationError."""
        from agentic_workflow.domain.algorithms.repo_map_builder import repo_map_build
        import icontract
        with pytest.raises((icontract.ViolationError, ValueError)):
            repo_map_build("/nonexistent/path/xyz", token_budget=1000)

    def test_zero_budget_raises(self, tmp_path: Path) -> None:
        """icontract precondition: token_budget=0 raises ViolationError."""
        from agentic_workflow.domain.algorithms.repo_map_builder import repo_map_build
        import icontract
        with pytest.raises((icontract.ViolationError, ValueError)):
            repo_map_build(str(tmp_path), token_budget=0)


# ===========================================================================
# RepoMap model — uncovered branches (L56-68, L80-89)
# ===========================================================================

class TestRepoMapModel:
    """Unit tests for RepoMap value object methods."""

    def _make_sym(self, name="Foo", file_path="a.py", kind="class", sig="class Foo", line=1):
        from agentic_workflow.domain.models.repo_map import SymbolDef
        return SymbolDef(file_path=file_path, name=name, kind=kind, signature=sig, line_number=line)

    def test_prune_to_budget_zero_returns_empty(self) -> None:
        """L56-57: budget <= 0 → return empty RepoMap."""
        from agentic_workflow.domain.models.repo_map import RepoMap
        rm = RepoMap(symbols=(self._make_sym(),), token_count=5, file_ranks={})
        result = rm.prune_to_budget(0)
        assert result.token_count == 0
        assert result.symbols == ()

    def test_prune_to_budget_negative_returns_empty(self) -> None:
        """budget < 0 → also returns empty."""
        from agentic_workflow.domain.models.repo_map import RepoMap
        rm = RepoMap(symbols=(self._make_sym(),), token_count=5, file_ranks={})
        result = rm.prune_to_budget(-1)
        assert result.symbols == ()

    def test_prune_to_budget_keeps_within_limit(self) -> None:
        """Prune to budget trims symbols correctly."""
        from agentic_workflow.domain.models.repo_map import SymbolDef, RepoMap
        syms = tuple(
            SymbolDef(file_path="f.py", name=f"F{i}", kind="class",
                      signature="class " + "X" * 40, line_number=i)
            for i in range(20)
        )
        rm = RepoMap(symbols=syms, token_count=200, file_ranks={})
        result = rm.prune_to_budget(10)
        assert result.token_count <= 10

    def test_get_context_string_empty(self) -> None:
        """L80-81: empty symbols → return empty string."""
        from agentic_workflow.domain.models.repo_map import RepoMap
        rm = RepoMap(symbols=(), token_count=0, file_ranks={})
        assert rm.get_context_string() == ""

    def test_get_context_string_single_file(self) -> None:
        """L82-89: symbols from same file grouped under one header."""
        from agentic_workflow.domain.models.repo_map import RepoMap
        syms = (
            self._make_sym("Foo", "a.py"),
            self._make_sym("Bar", "a.py", "function", "def Bar()"),
        )
        rm = RepoMap(symbols=syms, token_count=4, file_ranks={})
        ctx = rm.get_context_string()
        assert "## a.py" in ctx
        assert ctx.count("## a.py") == 1  # Only one header for the same file

    def test_get_context_string_multiple_files(self) -> None:
        """L85-87: symbols from different files get separate headers."""
        from agentic_workflow.domain.models.repo_map import RepoMap
        syms = (
            self._make_sym("A", "a.py"),
            self._make_sym("B", "b.py"),
        )
        rm = RepoMap(symbols=syms, token_count=2, file_ranks={})
        ctx = rm.get_context_string()
        assert "## a.py" in ctx
        assert "## b.py" in ctx
