"""Port Interface — External Agent Orchestrator Gateway (Archon et al.).

Traceable to: FR-073, FR-074, ADR-STR-030
Application-layer abstraction that makes the orchestration engine a
replaceable detail: any platform able to run an exported workflow document
(Archon, or a future fleet runner) plugs in behind this port.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class IAgentOrchestratorGateway(ABC):
    """Abstract interface for exporting and dispatching agent workflows."""

    @abstractmethod
    def export_workflow(self, pipeline_id: str, stages: list[str]) -> str:
        """Render the pipeline as an external workflow document."""

    @abstractmethod
    def dispatch(self, workflow_doc: str) -> bool:
        """Persist and dispatch the workflow document; True on success."""
