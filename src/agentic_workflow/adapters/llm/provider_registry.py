"""LLM Provider Registry — Centralized Provider Management.

Traceable to: ADR-STR-009, CLS-028
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_workflow.adapters.llm.providers.anthropic import AnthropicProvider
from agentic_workflow.adapters.llm.providers.openai import OpenAIProvider

if TYPE_CHECKING:
    from agentic_workflow.application.ports.llm_provider import LLMProvider


class LLMProviderRegistry:
    """Registry for LLM providers."""

    def __init__(self) -> None:
        """Initialize the registry with default providers."""
        self._providers: dict[str, LLMProvider] = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
        }

    def get_provider(self, name: str) -> LLMProvider:
        """Get a provider by name.

        Args:
            name: Provider name (case-insensitive).

        Returns:
            The registered LLMProvider instance.

        Raises:
            ValueError: If the provider is not registered.
        """
        name = name.lower()
        if name not in self._providers:
            raise ValueError(f"Unsupported LLM provider: {name!r}")
        return self._providers[name]
