"""Abstract Interface and Delegations for Filesystem and AST Operations.

Traceable to: FR-001, FR-026
Defines the abstract interface for filesystem IO, decoupling adapters and domain from OS behaviors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from agentic_workflow.domain.value_objects.symbol_def import SymbolDef


class FilesystemIO(ABC):
    """Abstract interface for filesystem IO operations, separating OS logic from core logic."""

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if a path exists."""

    @abstractmethod
    def read_text(self, path: str, encoding: str = "utf-8", errors: str | None = None) -> str:
        """Read text from a file path."""

    @abstractmethod
    def write_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """Write text to a file path."""

    @abstractmethod
    def append_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """Append text to an existing file path."""

    @abstractmethod
    def mkdir(self, path: str, parents: bool = True, exist_ok: bool = True) -> None:
        """Create a directory path."""

    @abstractmethod
    def glob(self, dir_path: str, pattern: str) -> list[str]:
        """Perform glob pattern search under a directory path."""

    @abstractmethod
    def remove(self, path: str) -> bool:
        """Remove a file path."""

    @abstractmethod
    def is_dir(self, path: str) -> bool:
        """Check if path is a directory."""

    @abstractmethod
    def list_files(self, project_path: str) -> list[str]:
        """List all Python files excluding tests under the project path."""

    @abstractmethod
    def extract_symbols_ast(self, file_path: str, source: str) -> list[SymbolDef]:
        """Extract class/function symbols from source code via AST."""

    @abstractmethod
    def resolve_path(self, path: str) -> str:
        """Resolve absolute path from string."""

    @abstractmethod
    def relative_to(self, path: str, base_path: str) -> str:
        """Calculate relative path."""


_instance: FilesystemIO | None = None


def get_filesystem() -> FilesystemIO:
    """Get the currently registered FilesystemIO instance."""
    if _instance is None:
        raise RuntimeError("FilesystemIO implementation is not registered.")
    return _instance


def register_filesystem(fs: FilesystemIO) -> None:
    """Register a concrete FilesystemIO implementation."""
    global _instance
    _instance = fs


# Adapter-level functions for backwards compatibility and domain delegation
def default_exists(base_dir: Any, rel_path: str) -> bool:
    """Check if a relative file path exists under base_dir (must be a file, not directory)."""
    fs = get_filesystem()
    path = fs.resolve_path(f"{base_dir}/{rel_path}")
    return fs.exists(path) and not fs.is_dir(path)


def default_read_text(base_dir: Any, rel_path: str) -> str:
    """Read a relative file's contents as a UTF-8 string."""
    fs = get_filesystem()
    return fs.read_text(fs.resolve_path(f"{base_dir}/{rel_path}"))


def default_glob(base_dir: Any, pattern: str) -> list[str]:
    """Perform glob expansion for a pattern under base_dir."""
    return get_filesystem().glob(str(base_dir), pattern)


def default_list_files(project_path: str) -> list[str]:
    """Discovers all python files under the project path, excluding test files."""
    return get_filesystem().list_files(project_path)


def default_read_text_absolute(file_path: str) -> str:
    """Read an absolute file path's contents, ignoring encoding errors."""
    return get_filesystem().read_text(file_path, errors="ignore")


def default_is_dir(path: str) -> bool:
    """Check if a path is a directory."""
    return get_filesystem().is_dir(path)


def default_extract_symbols_ast(file_path: str, source: str) -> list[SymbolDef]:
    """Extract class and function symbols from source code via AST analysis."""
    return get_filesystem().extract_symbols_ast(file_path, source)
