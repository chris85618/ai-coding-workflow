"""Tests for the OfflineReasoner degradation path (FR-076, ADR-GOV-017)."""

from agentic_workflow.adapters.llm.offline_reasoner import OfflineReasoner
from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner


class TestOfflineReasoner:
    """Covers the deterministic LLM-free reasoner used for self-bootstrap runs."""

    def test_reason_echoes_prompt_under_degraded_marker(self) -> None:
        """TC-BOOT-001: reason() is deterministic and marks degraded mode."""
        response = OfflineReasoner().reason("Critique stage content", system_message="be strict")
        assert response == "[offline-degraded] Critique stage content"

    def test_extract_structured_matches_schema_properties(self) -> None:
        """TC-BOOT-002: extract_structured() returns every schema property, empty-valued."""
        schema: dict[str, dict[str, dict[str, str]]] = {"properties": {"decision": {}, "reason": {}}}
        assert OfflineReasoner().extract_structured("classify", schema) == {"decision": "", "reason": ""}

    def test_extract_structured_handles_schema_without_properties(self) -> None:
        """TC-BOOT-003: A schema without properties degrades to an empty dict."""
        assert OfflineReasoner().extract_structured("classify", {}) == {}

    def test_implements_agent_reasoner_port(self) -> None:
        """TC-BOOT-004: The adapter is a concrete IAgentReasoner implementation."""
        assert isinstance(OfflineReasoner(), IAgentReasoner)
