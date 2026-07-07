"""Adapters Layer — Offline reasoner (pure degradation path).

Traceable to: FR-076, ADR-GOV-017, ADR-STR-029
Deterministic LLM-free implementation of the reasoner port so the master
pipeline stays executable end-to-end (self-bootstrap, Ouroboros closure)
when no LLM provider is configured. External models are accelerators, not
prerequisites.
"""

from __future__ import annotations

from typing import Any

from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner

_DEGRADED_PREFIX = "[offline-degraded] "


class OfflineReasoner(IAgentReasoner):
    """Deterministic reasoner used when no LLM provider is configured."""

    def reason(self, prompt: str, system_message: str | None = None) -> str:
        """Echo the prompt intent under a degraded-mode marker."""
        prefix = _DEGRADED_PREFIX
        return prefix + prompt

    def extract_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        """Return an empty-valued structure matching the schema's properties."""
        return {key: "" for key in schema.get("properties", {})}
