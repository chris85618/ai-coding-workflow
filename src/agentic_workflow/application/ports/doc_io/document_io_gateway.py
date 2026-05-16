"""Port Interfaces — DocumentIOGateway Contract.

Traceable to: FR-002 (docs persistence), FR-024 (change management),
ADR-STR-001
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class DocumentIOGateway(ABC):
    """Abstract gateway for reading and writing Markdown documents.

    Traceable to: FR-002 (file-driven documentation), UC-002 (Phase 2 analysis)
    Adapters in adapters/persistence/markdown_writer.py implement this.
    """

    @abstractmethod
    def read(self, doc_path: str) -> str:
        """Read a document from the repository.

        Args:
            doc_path: Relative path from repo root (e.g., "docs/workflow-state.md").

        Returns:
            Document content as a string.
        """

    @abstractmethod
    def write(self, doc_path: str, content: str) -> None:
        """Write or overwrite a document in the repository.

        Args:
            doc_path: Relative path from repo root.
            content: Full document content to write.
        """

    @abstractmethod
    def append(self, doc_path: str, content: str) -> None:
        """Append content to an existing document.

        Args:
            doc_path: Relative path from repo root.
            content: Content to append (will be added at end of file).
        """

    @abstractmethod
    def exists(self, doc_path: str) -> bool:
        """Check whether a document exists.

        Args:
            doc_path: Relative path from repo root.

        Returns:
            True if the file exists.
        """
