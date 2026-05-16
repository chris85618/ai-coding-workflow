"""Unit tests for RepoMap value object methods."""

from agentic_workflow.domain.value_objects import RepoMap, SymbolDef


class TestRepoMapModel:
    """Unit tests for RepoMap value object methods."""

    def _make_sym(
        self,
        name: str = "Foo",
        file_path: str = "a.py",
        kind: str = "class",
        sig: str = "class Foo",
        line: int = 1,
    ) -> SymbolDef:
        """Create a SymbolDef for testing."""
        return SymbolDef(file_path=file_path, name=name, kind=kind, signature=sig, line_number=line)

    def test_prune_to_budget_zero_returns_empty(self) -> None:
        """L56-57: budget <= 0 → return empty RepoMap."""
        rm = RepoMap(symbols=(self._make_sym(),), token_count=5, file_ranks={})
        result = rm.prune_to_budget(0)
        assert result.token_count == 0
        assert result.symbols == ()

    def test_prune_to_budget_negative_returns_empty(self) -> None:
        """Budget < 0 → also returns empty."""
        rm = RepoMap(symbols=(self._make_sym(),), token_count=5, file_ranks={})
        result = rm.prune_to_budget(-1)
        assert result.symbols == ()

    def test_prune_to_budget_keeps_within_limit(self) -> None:
        """Prune to budget trims symbols correctly."""
        syms = tuple(
            SymbolDef(
                file_path="f.py",
                name=f"F{i}",
                kind="class",
                signature="class " + "X" * 40,
                line_number=i,
            )
            for i in range(20)
        )
        rm = RepoMap(symbols=syms, token_count=200, file_ranks={})
        result = rm.prune_to_budget(10)
        assert result.token_count <= 10

    def test_get_context_string_empty(self) -> None:
        """L80-81: empty symbols → return empty string."""
        rm = RepoMap(symbols=(), token_count=0, file_ranks={})
        assert rm.get_context_string() == ""

    def test_get_context_string_single_file(self) -> None:
        """L82-89: symbols from same file grouped under one header."""
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
        syms = (
            self._make_sym("A", "a.py"),
            self._make_sym("B", "b.py"),
        )
        rm = RepoMap(symbols=syms, token_count=2, file_ranks={})
        ctx = rm.get_context_string()
        assert "## a.py" in ctx
        assert "## b.py" in ctx
