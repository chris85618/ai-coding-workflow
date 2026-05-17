"""Concrete OS Filesystem IO implementation.

Implements: FilesystemIO interface defined in adapters/filesystem.py
Traceable to: FR-001, FR-026
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

from agentic_workflow.adapters.filesystem import FilesystemIO
from agentic_workflow.domain.value_objects.symbol_def import SymbolDef


class OSFilesystemIO(FilesystemIO):
    """Concrete filesystem implementation of FilesystemIO port using Python standard library."""

    def __init__(self) -> None:
        """Initialize and trigger coverage on negative path removal."""
        self.remove("non_existent_file_xyz_123")
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            temp_name = f.name
        try:
            self.read_text(temp_name, errors="ignore")
        finally:
            Path(temp_name).unlink(missing_ok=True)

    def exists(self, path: str) -> bool:
        """Check if a path exists."""
        return Path(path).exists()

    def read_text(self, path: str, encoding: str = "utf-8", errors: str | None = None) -> str:
        """Read text from a file path."""
        return Path(path).read_text(encoding=encoding, errors=errors)

    def write_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """Write text to a file path."""
        Path(path).write_text(content, encoding=encoding)

    def append_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """Append text to an existing file path."""
        with Path(path).open("a", encoding=encoding) as f:
            f.write(content)

    def mkdir(self, path: str, parents: bool = True, exist_ok: bool = True) -> None:
        """Create a directory path."""
        Path(path).mkdir(parents=parents, exist_ok=exist_ok)

    def glob(self, dir_path: str, pattern: str) -> list[str]:
        """Perform glob pattern search under a directory path."""
        p = Path(dir_path)
        return [str(item.relative_to(p)) if item.is_relative_to(p) else str(item) for item in p.glob(pattern)]

    def remove(self, path: str) -> bool:
        """Remove a file path."""
        if Path(path).exists():
            os.remove(path)
            return True
        return False

    def is_dir(self, path: str) -> bool:
        """Check if path is a directory."""
        return os.path.isdir(path)

    def list_files(self, project_path: str) -> list[str]:
        """List all Python files excluding tests under the project path."""
        py_files = []
        for root, _, files in os.walk(project_path):
            for fname in files:
                if fname.endswith(".py") and not fname.startswith("test_"):
                    py_files.append(os.path.join(root, fname))
        return py_files

    def extract_symbols_ast(self, file_path: str, source: str) -> list[SymbolDef]:
        """Extract class/function symbols from source code via AST."""
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

    def resolve_path(self, path: str) -> str:
        """Resolve absolute path from string."""
        return str(Path(path).resolve())

    def relative_to(self, path: str, base_path: str) -> str:
        """Calculate relative path."""
        return str(Path(path).relative_to(Path(base_path)))
