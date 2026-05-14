"""Port Interfaces — Document IO and Event Bus Contracts.

Traceable to: FR-002 (docs persistence), FR-024 (change management),
ADR-STR-001
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


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


class DomainEventBus(ABC):
    """Abstract event bus for domain events.

    Traceable to: EVT-001..EVT-010, FR-024 (cross-file sync)
    Decouples event producers (domain) from consumers (adapters/UI).
    """

    @abstractmethod
    def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        """Publish a domain event.

        Args:
            event_type: Event type name (e.g., "GitCommitCreated", "ModelSelected").
            payload: Event payload dictionary.
        """

    @abstractmethod
    def subscribe(self, event_type: str, handler: Any) -> None:
        """Register a handler for an event type.

        Args:
            event_type: Event type name to subscribe to.
            handler: Callable that accepts (event_type: str, payload: dict).
        """

    @abstractmethod
    def get_published_events(self) -> list[dict[str, Any]]:
        """Return all events published since creation (for testing).

        Returns:
            List of event dictionaries with 'type' and 'payload' keys.
        """
