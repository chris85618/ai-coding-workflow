"""Adapter: Implementation of IPipelineRepository using Markdown files.

Traceable to: FR-002, ADR-STR-021 (Repository Pattern), ADR-STR-029
Persists the Pipeline aggregate to docs/workflow-state.md as a parseable,
human-readable document and rehydrates it back — the fixed document is the
kanban/WBS single source of truth for pipeline position.
"""

from __future__ import annotations

import re

from agentic_workflow.application.ports.doc_io.document_io_gateway import DocumentIOGateway
from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository
from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.entities.stage import Stage
from agentic_workflow.domain.enums import GateDecision, PipelineStatus, StageStatus

_STATE_FILE = "docs/workflow-state.md"

_NO_GATE = "none"

_HEADER_TEMPLATE = (
    "# Workflow State — {pipeline_id}\n\n"
    "**Pipeline ID**: {pipeline_id}\n"
    "**Pipeline Position**: {position}\n"
    "**Pipeline Status**: {status}\n"
    "**Last Gate Decision**: {gate}\n\n"
    "## Stage Registry\n\n"
    "| Stage | Status | Iterations |\n"
    "|-------|--------|------------|\n"
)

_STAGE_ROW_TEMPLATE = "| {stage_id} | {status} | {iterations} |\n"

_FIELD_PATTERN = r"\*\*{field}\*\*: (.+)"

_STAGE_ROW_PATTERN = r"\| (\w+) \| (\w+) \| (\d+) \|"


class MarkdownPipelineRepository(IPipelineRepository):
    """Repository that persists Pipeline state to docs/workflow-state.md."""

    def __init__(self, io_gateway: DocumentIOGateway):
        """Initialize with a document IO gateway."""
        self._io = io_gateway
        self._state_file = _STATE_FILE

    def get_by_id(self, pipeline_id: str) -> Pipeline | None:
        """Get pipeline by ID.

        Note: Current implementation only supports one active pipeline.
        """
        current = self.get_current()
        if current and current.pipeline_id == pipeline_id:
            return current
        return None

    def save(self, pipeline: Pipeline) -> None:
        """Persist the pipeline aggregate to the markdown state document."""
        header_template = _HEADER_TEMPLATE
        row_template = _STAGE_ROW_TEMPLATE
        no_gate = _NO_GATE
        gate = pipeline.last_gate_decision.value if pipeline.last_gate_decision else no_gate
        header = header_template.format(
            pipeline_id=pipeline.pipeline_id,
            position=pipeline.current_position,
            status=pipeline.status.value,
            gate=gate,
        )
        rows = [
            row_template.format(stage_id=stage.stage_id, status=stage.status.value, iterations=stage.iteration_count)
            for stage in pipeline.stages.values()
        ]
        self._io.write(self._state_file, header + "".join(rows))

    def get_current(self) -> Pipeline | None:
        """Rehydrate the current Pipeline aggregate from workflow-state.md."""
        if not self._io.exists(self._state_file):
            return None
        content = self._io.read(self._state_file)
        fields = self._parse_fields(content)
        if fields is None:
            return None
        pipeline_id, position, status, gate = fields
        try:
            return Pipeline(
                pipeline_id=pipeline_id,
                current_position=position,
                status=PipelineStatus(status),
                last_gate_decision=self._parse_gate(gate),
                stages=self._parse_stages(content),
            )
        except ValueError:
            return None

    @staticmethod
    def _parse_fields(content: str) -> tuple[str, str, str, str] | None:
        """Extract the pipeline header fields; None when the document is not parseable."""
        field_pattern = _FIELD_PATTERN
        names = ["Pipeline ID", "Pipeline Position", "Pipeline Status", "Last Gate Decision"]
        matches = [re.search(field_pattern.format(field=re.escape(name)), content) for name in names]
        if any(match is None for match in matches):
            return None
        values = [match.group(1).strip() for match in matches if match is not None]
        return (values[0], values[1], values[2], values[3])

    @staticmethod
    def _parse_gate(gate: str) -> GateDecision | None:
        """Map the serialized gate field back to a GateDecision."""
        no_gate = _NO_GATE
        return None if gate == no_gate else GateDecision(gate)

    @staticmethod
    def _parse_stages(content: str) -> dict[str, Stage]:
        """Rebuild the stage entities from the stage registry table."""
        row_pattern = _STAGE_ROW_PATTERN
        rows = re.findall(row_pattern, content)
        return {
            stage_id: Stage(
                stage_id=stage_id,
                name=stage_id.replace("_", " ").title(),
                status=StageStatus(status),
                iteration_count=int(iterations),
            )
            for stage_id, status, iterations in rows
        }
