"""Frameworks Layer — Archon implementation of the agent orchestrator gateway.

Traceable to: FR-073, FR-074, ADR-STR-030
Thin archon CLI wrapper over the registered FilesystemIO and
SubprocessExecutor (DIP, ADR-STR-027). When the archon binary is not
installed the subprocess executor reports a non-zero exit code, so
dispatch degrades gracefully by returning False (ADR-GOV-017).
"""

from __future__ import annotations

from agentic_workflow.adapters.archon.workflow_mapper import ArchonWorkflowMapper
from agentic_workflow.adapters.filesystem import get_filesystem
from agentic_workflow.adapters.subprocess import get_executor
from agentic_workflow.application.ports.gateways.agent_orchestrator_gateway import (
    IAgentOrchestratorGateway,
)

_WORKFLOW_DOC_DIR = ".archon"
WORKFLOW_DOC_PATH = ".archon/agentic-workflow.yaml"


class ArchonOrchestrator(IAgentOrchestratorGateway):
    """Archon-backed orchestrator gateway used for external workflow dispatch."""

    def export_workflow(self, pipeline_id: str, stages: list[str]) -> str:
        """Render the pipeline as an Archon workflow document."""
        return ArchonWorkflowMapper().to_workflow_yaml(pipeline_id, stages)

    def dispatch(self, workflow_doc: str) -> bool:
        """Persist the workflow document and dispatch it via the archon CLI."""
        doc_dir = _WORKFLOW_DOC_DIR
        doc_path = WORKFLOW_DOC_PATH
        get_filesystem().mkdir(doc_dir)
        get_filesystem().write_text(doc_path, workflow_doc)
        code, _, _ = get_executor().run_cmd_list(["archon", "run", doc_path])
        return code == 0
