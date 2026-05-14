"""CLS-015: RepoMap — Value Object for repository symbol map.

Traceable to: ALG-006 (RepoMapBuilder creates this)
INV-024 ensures token_count <= budget.

Condensed representation of repository structure via tree-sitter AST.
Ranked by PageRank on import/dependency graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SymbolDef:
    """A single symbol definition extracted from source code.

    Attributes:
        file_path: Source file containing this symbol.
        name: Symbol name (class, function, method).
        kind: Symbol kind ("class", "function", "method").
        signature: Full signature string for context.
        line_number: Line number in source file.
    """

    file_path: str
    name: str
    kind: str
    signature: str
    line_number: int


@dataclass(frozen=True)
class RepoMap:
    """Condensed repository structure map.

    Attributes:
        symbols: Ranked list of symbol definitions.
        token_count: Estimated total token count of this map.
        file_ranks: PageRank scores per file path.
    """

    symbols: tuple[SymbolDef, ...] = field(default_factory=tuple)
    token_count: int = 0
    file_ranks: dict[str, float] = field(default_factory=dict)

    def prune_to_budget(self, budget: int) -> RepoMap:
        """Return a new RepoMap pruned to fit within token budget.

        Args:
            budget: Maximum token count allowed.

        Returns:
            New RepoMap with symbols trimmed to fit budget.
        """
        # Implementation deferred to Stage 8 (TDD)
        raise NotImplementedError

    def get_context_string(self) -> str:
        """Render this map as a string for LLM context injection.

        Returns:
            Formatted string of symbol signatures.
        """
        # Implementation deferred to Stage 8 (TDD)
        raise NotImplementedError
