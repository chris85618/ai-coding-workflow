"""Cover missing branches in CLS-015 repo_map.py."""

from agentic_workflow.domain.value_objects import RepoMap, SymbolDef


class TestRepoMapBranches:
    """Cover missing branches in CLS-015 repo_map.py."""

    def test_prune_to_zero_budget(self) -> None:
        """Pruning to budget=0 returns empty map."""
        syms = (SymbolDef("a.py", "Foo", "class", "class Foo", 1),)
        m = RepoMap(symbols=syms, token_count=5, file_ranks={})
        pruned = m.prune_to_budget(0)
        assert pruned.token_count == 0
        assert len(pruned.symbols) == 0

    def test_get_context_string_empty(self) -> None:
        """Empty map returns empty string."""
        m = RepoMap(symbols=(), token_count=0, file_ranks={})
        assert m.get_context_string() == ""

    def test_get_context_string_multiple_files(self) -> None:
        """Context string groups symbols by file."""
        syms = (
            SymbolDef("a.py", "Foo", "class", "class Foo", 1),
            SymbolDef("a.py", "bar", "function", "def bar()", 5),
            SymbolDef("b.py", "baz", "function", "def baz()", 1),
        )
        m = RepoMap(symbols=syms, token_count=10, file_ranks={})
        ctx = m.get_context_string()
        assert "## a.py" in ctx
        assert "## b.py" in ctx
        assert "class Foo" in ctx

    def test_prune_fits_all(self) -> None:
        """Large budget keeps all symbols."""
        syms = (
            SymbolDef("a.py", "Foo", "class", "class Foo", 1),
            SymbolDef("b.py", "bar", "function", "def bar()", 1),
        )
        m = RepoMap(symbols=syms, token_count=10, file_ranks={})
        pruned = m.prune_to_budget(1000)
        assert len(pruned.symbols) == 2
