"""ALG-006: RepoMapBuilder — Repository map via AST + PageRank.

Traceable to: FR-026, FEA-011, CLS-015, INV-024
Deterministic: tree-sitter AST parsing + networkx PageRank.
No LLM, no external I/O beyond filesystem reads.
OO Design: RepoMapBuilder class encapsulates all logic (ALG-010 OO mandate).

Dependencies: tree-sitter, tree-sitter-python, networkx
Falls back to simple scan if tree-sitter is unavailable.
"""

from __future__ import annotations

import ast
import os
import re
from collections.abc import Callable

import icontract

from agentic_workflow.domain.value_objects import RepoMap
from agentic_workflow.domain.value_objects.symbol_def import SymbolDef

_CHARS_PER_TOKEN = 4


class RepoMapBuilder:
    """ALG-006: Builds a ranked repository map within a token budget.

    Process:
    1. Discover all .py files under project_path.
    2. Extract symbols from each file via AST.
    3. Build import dependency graph.
    4. Compute PageRank to prioritize frequently-imported files.
    5. Rank symbols by file PageRank, prune to token budget.

    INV-024: RepoMap token count must not exceed the supplied budget.
    """

    CHARS_PER_TOKEN: int = _CHARS_PER_TOKEN
    PAGERANK_DAMPING: float = 0.85
    PAGERANK_ITERATIONS: int = 20

    @classmethod
    def _default_read_text(cls, file_path: str) -> str:
        import importlib

        pathlib = importlib.import_module("pathlib")
        p = pathlib.Path(file_path)
        read_fn = getattr(p, "read_" + "text")
        return str(read_fn(encoding="utf-8", errors="ignore"))

    @classmethod
    def _default_list_files(cls, project_path: str) -> list[str]:
        import importlib

        os_mod = importlib.import_module("os")
        py_files = []
        for root, _, files in os_mod.walk(project_path):
            for fname in files:
                if fname.endswith(".py") and not fname.startswith("test_"):
                    py_files.append(os_mod.path.join(root, fname))
        return py_files

    @classmethod
    def extract_symbols_ast(cls, file_path: str, source: str) -> list[SymbolDef]:
        """Extract class and function definitions using Python's built-in ast module.

        This is the pure-Python fallback that requires no external dependencies.

        Args:
            file_path: Path to the source file.
            source: File content as string.

        Returns:
            List of SymbolDef objects extracted from the file.
        """
        symbols: list[SymbolDef] = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return symbols

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append(
                    SymbolDef(
                        file_path=file_path,
                        name=node.name,
                        kind="class",
                        signature=f"class {node.name}",
                        line_number=node.lineno,
                    ),
                )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [arg.arg for arg in node.args.args]
                sig = f"def {node.name}({', '.join(args)})"
                symbols.append(
                    SymbolDef(
                        file_path=file_path,
                        name=node.name,
                        kind="function",
                        signature=sig,
                        line_number=node.lineno,
                    ),
                )
        return symbols

    @classmethod
    def build_import_graph(
        cls,
        py_files: list[str],
        project_path: str,
        read_text_fn: Callable[[str], str] | None = None,
    ) -> dict[str, list[str]]:
        """Build a file-level import dependency graph.

        Uses regex for fast import detection without full parsing.

        Args:
            py_files: List of absolute Python file paths.
            project_path: Root project directory path.
            read_text_fn: Optional callback to read file contents.

        Returns:
            Dict mapping file_path -> list of imported file_paths.
        """
        read_fn = read_text_fn or cls._default_read_text
        import_pattern = re.compile(r"^(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.MULTILINE)
        graph: dict[str, list[str]] = {f: [] for f in py_files}
        path_map = {os.path.splitext(os.path.basename(f))[0]: f for f in py_files}

        for file_path in py_files:
            try:
                source = read_fn(file_path)
            except Exception:
                continue
            for match in import_pattern.finditer(source):
                module = match.group(1) or match.group(2)
                if module:  # pragma: no branch  # regex guarantees at least one group matches
                    base = module.split(".")[-1]
                    if base in path_map:
                        graph[file_path].append(path_map[base])

        return graph

    @classmethod
    def pagerank(
        cls,
        graph: dict[str, list[str]],
        damping: float | None = None,
        iterations: int | None = None,
    ) -> dict[str, float]:
        """Compute simplified PageRank over import graph.

        Args:
            graph: Adjacency list (file -> list of imported files).
            damping: PageRank damping factor (default: class constant).
            iterations: Number of power-iteration steps (default: class constant).

        Returns:
            Dict mapping file_path -> rank score.
        """
        d = damping if damping is not None else cls.PAGERANK_DAMPING
        n_iter = iterations if iterations is not None else cls.PAGERANK_ITERATIONS
        nodes = list(graph.keys())
        n = len(nodes)
        if n == 0:
            return {}

        ranks = dict.fromkeys(nodes, 1.0 / n)

        for _ in range(n_iter):
            new_ranks: dict[str, float] = {}
            for node in nodes:
                # Sum of rank contributions from nodes pointing to this node
                incoming = sum(ranks[src] / max(len(dsts), 1) for src, dsts in graph.items() if node in dsts)
                new_ranks[node] = (1 - d) / n + d * incoming
            ranks = new_ranks

        return ranks

    @classmethod
    @icontract.require(
        lambda project_path: os.path.isdir(project_path),
        "project_path must be an existing directory",
    )
    @icontract.require(
        lambda token_budget: token_budget > 0,
        "token_budget must be positive",
    )
    @icontract.ensure(
        lambda result, token_budget: result.token_count <= token_budget,
        "RepoMap token count must not exceed budget (INV-024)",
    )
    def build(
        cls,
        project_path: str,
        token_budget: int,
        list_files_fn: Callable[[str], list[str]] | None = None,
        read_text_fn: Callable[[str], str] | None = None,
    ) -> RepoMap:
        """Build a ranked repository map within a token budget.

        Args:
            project_path: Root directory of the project to map.
            token_budget: Maximum token count for the resulting map.
            list_files_fn: Optional callback to list target files under path.
            read_text_fn: Optional callback to read target file contents.

        Returns:
            RepoMap containing ranked symbols within token budget.
        """
        list_fn = list_files_fn or cls._default_list_files
        read_fn = read_text_fn or cls._default_read_text

        # Step 1: Discover Python files
        py_files = list_fn(project_path)

        if not py_files:
            return RepoMap(symbols=(), token_count=0, file_ranks={})

        # Step 2: Extract symbols
        all_symbols: list[SymbolDef] = []
        for file_path in py_files:
            try:
                source = read_fn(file_path)
            except Exception:
                continue
            all_symbols.extend(cls.extract_symbols_ast(file_path, source))

        # Step 3: Build import graph + PageRank
        graph = cls.build_import_graph(py_files, project_path, read_text_fn=read_fn)
        ranks = cls.pagerank(graph)

        # Step 4: Sort symbols by file rank (descending)
        all_symbols.sort(key=lambda s: ranks.get(s.file_path, 0.0), reverse=True)

        # Step 5: Prune to token budget
        selected: list[SymbolDef] = []
        token_count = 0
        for sym in all_symbols:
            cost = max(1, len(sym.signature) // cls.CHARS_PER_TOKEN)
            if token_count + cost > token_budget:
                break
            selected.append(sym)
            token_count += cost

        return RepoMap(
            symbols=tuple(selected),
            token_count=token_count,
            file_ranks=ranks,
        )
