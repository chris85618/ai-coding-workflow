"""Persistence Adapter — Markdown Document Reader and Writer.

Implements: DocumentIOGateway port
Traceable to: FR-002 (file-driven docs), UC-002 (Phase 2), ADR-STR-001
Reads/writes Markdown files relative to a configured repository root.
"""

from __future__ import annotations

from pathlib import Path

from agentic_workflow.application.ports.doc_io import DocumentIOGateway


class MarkdownDocumentIO(DocumentIOGateway):
    """Filesystem Markdown document reader/writer.

    All paths are interpreted as relative to ``repo_root``.
    Creates missing parent directories automatically on write.

    Args:
        repo_root: Absolute or relative path to the target repository root.
    """

    def __init__(self, repo_root: str = ".") -> None:
        """Initializes the Markdown document IO.

        Args:
            repo_root: Path to the repository root directory.
        """
        self._root = Path(repo_root).resolve()

    def _resolve(self, doc_path: str) -> Path:
        """Resolve doc_path relative to repo_root.

        Raises:
            ValueError: If the resolved path escapes repo_root (SEC-002).
        """
        resolved = (self._root / doc_path).resolve()
        try:
            resolved.relative_to(self._root)
        except ValueError:
            raise ValueError(f"Path traversal detected: {doc_path!r} escapes repo root (SEC-002)") from None
        return resolved

    def read(self, doc_path: str) -> str:
        """Read a Markdown document.

        Args:
            doc_path: Relative path from repo root.

        Returns:
            Document content as string.

        Raises:
            FileNotFoundError: If the document does not exist.
        """
        path = self._resolve(doc_path)
        return path.read_text(encoding="utf-8")

    def write(self, doc_path: str, content: str) -> None:
        """Write (create or overwrite) a Markdown document.

        Args:
            doc_path: Relative path from repo root.
            content: Full document content to write.
        """
        path = self._resolve(doc_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def append(self, doc_path: str, content: str) -> None:
        """Append content to an existing document.

        Creates the file if it does not yet exist.

        Args:
            doc_path: Relative path from repo root.
            content: Content to append.
        """
        path = self._resolve(doc_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(content)

    def exists(self, doc_path: str) -> bool:
        """Check whether a document exists.

        Args:
            doc_path: Relative path from repo root.

        Returns:
            True if the file exists.
        """
        return self._resolve(doc_path).exists()
