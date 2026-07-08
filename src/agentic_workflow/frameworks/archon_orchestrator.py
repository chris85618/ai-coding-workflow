"""Frameworks Layer — Archon implementation of the agent orchestrator gateway.

Traceable to: FR-073, FR-074, ADR-STR-030, ADR-STR-033
Thin archon CLI wrapper over the registered FilesystemIO and
SubprocessExecutor (DIP, ADR-STR-027). Workflows live in
.archon/workflows/<name>.yaml and are dispatched by name via
`archon workflow run <name>` (archon CLI v0.5+). When the archon binary
is not installed the subprocess executor reports a non-zero exit code,
so dispatch degrades gracefully by returning False (ADR-GOV-017).
"""

from __future__ import annotations

from agentic_workflow.adapters.archon.workflow_mapper import ArchonWorkflowMapper
from agentic_workflow.adapters.filesystem import get_filesystem
from agentic_workflow.adapters.subprocess import get_executor
from agentic_workflow.application.ports.gateways.agent_orchestrator_gateway import (
    IAgentOrchestratorGateway,
)

WORKFLOW_DOC_DIR = ".archon/workflows"

_DISPATCH_TIMEOUT_SECONDS = 3600


class ArchonOrchestrator(IAgentOrchestratorGateway):
    """Archon-backed orchestrator gateway used for external workflow dispatch."""

    def export_workflow(self, pipeline_id: str, stages: list[str]) -> str:
        """Render the pipeline as an Archon workflow document."""
        return ArchonWorkflowMapper().to_workflow_yaml(pipeline_id, stages)

    def dispatch(self, workflow_doc: str) -> bool:
        """Persist the workflow document and dispatch it by name via the archon CLI."""
        doc_dir = WORKFLOW_DOC_DIR
        timeout_seconds = _DISPATCH_TIMEOUT_SECONDS
        name = ArchonWorkflowMapper().workflow_name(workflow_doc)
        get_filesystem().mkdir(doc_dir)
        get_filesystem().write_text(f"{doc_dir}/{name}.yaml", workflow_doc)
        return get_executor().run_cmd_list(["archon", "workflow", "run", name], timeout=timeout_seconds)[0] == 0
