"""Port Interface — Prompt Optimizer Gateway (DSPy et al.).

Traceable to: FR-075, ADR-STR-031
Application-layer abstraction that makes prompt optimization a replaceable
detail: any engine able to enrich a base prompt with labeled demonstrations
(DSPy, or a pure few-shot fallback) plugs in behind this port.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class IPromptOptimizer(ABC):
    """Abstract interface for optimizing agent prompts with demonstrations."""

    @abstractmethod
    def optimize(self, base_prompt: str, examples: list[tuple[str, str]]) -> str:
        """Return base_prompt enriched with (input, expected-output) demonstrations."""
