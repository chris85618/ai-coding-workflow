"""CLS-015: SymbolDef — A single symbol definition extracted from source code.

Traceable to: ALG-006 (RepoMapBuilder creates this)
"""

from __future__ import annotations

from dataclasses import dataclass


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
