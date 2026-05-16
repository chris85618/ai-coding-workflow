"""Unit tests for the AST symbol extraction helper."""

from agentic_workflow.domain.algorithms.repo_map_builder import RepoMapBuilder


class TestExtractSymbolsAst:
    """Unit tests for the AST symbol extraction helper."""

    def test_syntax_error_returns_empty(self) -> None:
        """L40-41: SyntaxError in ast.parse → return empty list."""
        result = RepoMapBuilder.extract_symbols_ast("bad.py", "def (: this is not valid python +++")
        assert result == []

    def test_class_def_extracted(self) -> None:
        """ClassDef branch: produces kind='class'."""
        result = RepoMapBuilder.extract_symbols_ast("f.py", "class Foo:\n    pass\n")
        assert any(s.kind == "class" and s.name == "Foo" for s in result)

    def test_function_def_extracted(self) -> None:
        """FunctionDef branch: produces kind='function'."""
        result = RepoMapBuilder.extract_symbols_ast("f.py", "def bar(x, y):\n    pass\n")
        assert any(s.kind == "function" and s.name == "bar" for s in result)

    def test_async_function_def_extracted(self) -> None:
        """L54: AsyncFunctionDef branch: also produces kind='function'."""
        result = RepoMapBuilder.extract_symbols_ast("f.py", "async def fetch(url):\n    pass\n")
        assert any(s.kind == "function" and s.name == "fetch" for s in result)

    def test_empty_source_returns_empty(self) -> None:
        """Empty file: no symbols extracted."""
        result = RepoMapBuilder.extract_symbols_ast("empty.py", "")
        assert result == []

    def test_signature_includes_args(self) -> None:
        """FunctionDef signature includes argument names."""
        result = RepoMapBuilder.extract_symbols_ast("f.py", "def greet(name, greeting='hi'):\n    pass\n")
        fn = next(s for s in result if s.name == "greet")
        assert "name" in fn.signature
        assert fn.line_number == 1
