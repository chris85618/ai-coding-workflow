"""MCP Adapter — In-Process Event Bus (for tests + local dev).

Implements: DomainEventBus port
Traceable to: EVT-001..EVT-010, FR-024
Lightweight in-memory bus; no external dependencies required.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agentic_workflow.application.ports.doc_io import DomainEventBus


class InMemoryEventBus(DomainEventBus):
    """Simple in-process pub/sub event bus.

    Suitable for local development and unit testing.
    Not thread-safe; use a proper message broker for production.
    """

    def __init__(self) -> None:
        """Initializes the in-memory event bus."""
        self._handlers: dict[str, list[Callable[..., None]]] = {}
        self._published: list[dict[str, Any]] = []

    def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        """Publish an event synchronously to all subscribers.

        Args:
            event_type: Event type string (e.g., "ModelSelected").
            payload: Event payload dictionary.
        """
        event = {"type": event_type, "payload": payload}
        self._published.append(event)
        for handler in self._handlers.get(event_type, []):
            handler(event_type, payload)

    def subscribe(self, event_type: str, handler: Any) -> None:
        """Register a handler for an event type.

        Args:
            event_type: Event type string to subscribe to.
            handler: Callable(event_type, payload) to invoke on publish.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def get_published_events(self) -> list[dict[str, Any]]:
        """Return all published events (for test assertions).

        Returns:
            List of event dictionaries with 'type' and 'payload' keys.
        """
        return list(self._published)

    def clear(self) -> None:
        """Reset published event log (useful between tests)."""
        self._published.clear()
