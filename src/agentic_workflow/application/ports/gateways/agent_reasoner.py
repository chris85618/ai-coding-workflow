"""Port: Interface for Agent Reasoning (LLM)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IAgentReasoner(ABC):
    """Interface for LLM-based reasoning services.

    Isolates domain and application layers from specific LLM providers.
    """

    @abstractmethod
    def reason(self, prompt: str, system_message: str | None = None) -> str:
        """Send a prompt to the reasoner and get a text response.

        Args:
            prompt: The main user-style prompt.
            system_message: Optional system-style instruction.

        Returns:
            The raw text response from the reasoner.
        """
        pass

    @abstractmethod
    def extract_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        """Send a prompt and expect a structured response matching a schema.

        Args:
            prompt: The main prompt.
            schema: JSON Schema or similar definition of the expected output.

        Returns:
            Parsed dictionary matching the schema.
        """
        pass
