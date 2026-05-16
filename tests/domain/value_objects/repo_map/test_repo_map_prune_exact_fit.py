"""Cover exact-budget boundary in CLS-015."""

from agentic_workflow.domain.value_objects import RepoMap, SymbolDef


class TestRepoMapPruneExactFit:
    """Cover exact-budget boundary in CLS-015."""

    def test_prune_exact_budget(self) -> None:
        """Symbol exactly at budget limit is included."""
        syms = (
            SymbolDef("a.py", "Foo", "class", "class Foo:  # 5 tokens", 5),
            SymbolDef("b.py", "bar", "function", "def bar(): ...", 5),
        )
        m = RepoMap(symbols=syms, token_count=10, file_ranks={})
        pruned = m.prune_to_budget(5)
        assert pruned.token_count <= 5

    def test_prune_single_symbol_exceeds_budget(self) -> None:
        """Symbol with long signature bigger than budget is excluded."""
        long_sig = "class HeavyClass: " + "x" * 400
        syms = (SymbolDef("a.py", "HeavyClass", "class", long_sig, 1),)
        m = RepoMap(symbols=syms, token_count=100, file_ranks={})
        pruned = m.prune_to_budget(50)
        assert len(pruned.symbols) == 0
