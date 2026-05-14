"""CLS-015: RepoMap — Value Object for repository symbol map.

Traceable to: ALG-006 (RepoMapBuilder creates this)
INV-024 ensures token_count <= budget.
"""

from __future__ import annotations

from dataclasses import dataclass, field

_CHARS_PER_TOKEN = 4


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
        if budget <= 0:
            return RepoMap(symbols=(), token_count=0, file_ranks={})

        selected: list[SymbolDef] = []
        token_count = 0
        for sym in self.symbols:
            cost = max(1, len(sym.signature) // _CHARS_PER_TOKEN)
            if token_count + cost > budget:
                break
            selected.append(sym)
            token_count += cost

        return RepoMap(
            symbols=tuple(selected),
            token_count=token_count,
            file_ranks=self.file_ranks,
        )

    def get_context_string(self) -> str:
        """Render this map as a string for LLM context injection.

        Returns:
            Formatted string of symbol signatures.
        """
        if not self.symbols:
            return ""
        lines = [f"# Repository Map ({self.token_count} tokens)"]
        current_file = ""
        for sym in self.symbols:
            if sym.file_path != current_file:
                lines.append(f"\n## {sym.file_path}")
                current_file = sym.file_path
            lines.append(f"  {sym.kind}: {sym.signature}")
        return "\n".join(lines)
