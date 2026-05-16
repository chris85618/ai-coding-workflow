"""Port Interfaces — DomainEventBus Contract.

Traceable to: EVT-001..EVT-010, FR-024
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DomainEventBus(ABC):
    """Abstract event bus for publishing and subscribing to domain events.

    Traceable to: EVT-001..EVT-010, FR-024
    In-memory adapter: adapters/events/in_memory_bus.py
    """

    @abstractmethod
    def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        """Publish an event to all subscribers.

        Args:
            event_type: Event type string (e.g., "ModelSelected").
            payload: Event payload dictionary.
        """

    @abstractmethod
    def subscribe(self, event_type: str, handler: Any) -> None:
        """Subscribe a handler to an event type.

        Args:
            event_type: Event type string to subscribe to.
            handler: Callable(event_type, payload) to invoke on publish.
        """
