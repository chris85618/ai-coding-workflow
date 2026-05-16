"""Adapter: Implementation of IPipelineRepository using Markdown files."""

from __future__ import annotations

from agentic_workflow.application.ports.doc_io.document_io_gateway import DocumentIOGateway
from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
from agentic_workflow.domain.aggregates.pipeline import Pipeline


class MarkdownPipelineRepository(IPipelineRepository):
    """Repository that persists Pipeline state to docs/workflow-state.md."""

    def __init__(self, io_gateway: DocumentIOGateway):
        """Initialize with a document IO gateway."""
        self._io = io_gateway
        self._state_file = "docs/workflow-state.md"

    def get_by_id(self, pipeline_id: str) -> Pipeline | None:
        """Get pipeline by ID.

        Note: Current implementation only supports one active pipeline.
        """
        current = self.get_current()
        if current and current.pipeline_id == pipeline_id:
            return current
        return None

    def save(self, pipeline: Pipeline) -> None:
        """Persist the pipeline to the markdown file."""
        # This would use a specialized 'WorkflowStateFormatter' to generate the MD content
        # For now, we stub the persistence call to the IO gateway
        # In a real impl, we'd map Pipeline object -> Markdown string
        content = f"# Workflow State — {pipeline.pipeline_id}\n\nPipeline Position: {pipeline.current_position}"
        self._io.write(self._state_file, content)

    def get_current(self) -> Pipeline | None:
        """Read the current state from workflow-state.md."""
        if not self._io.exists(self._state_file):
            return None

        # content = self._io.read(self._state_file)
        # Here we would parse the MD content back into a Pipeline object
        # Stubbing for now to show the pattern
        return Pipeline(pipeline_id="agentic-workflow-default")
