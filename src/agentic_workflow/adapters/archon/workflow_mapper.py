"""Adapters Layer — Archon workflow document mapper.

Traceable to: FR-073, ADR-STR-030
Pure string logic that renders the canonical pipeline stage order as an
Archon YAML workflow document (worktree isolation, one step per stage,
closing quality-gate step). No I/O and no external dependencies, so the
orchestration engine stays a replaceable detail (DIP, ADR-STR-027).
"""

from __future__ import annotations

_HEADER_TEMPLATE = "name: agentic-workflow-{pipeline_id}\nisolation: worktree\nsteps:\n"

_STAGE_STEP_TEMPLATE = (
    "  - id: {stage_id}\n"
    "    agent: coding-agent\n"
    "    prompt: Execute pipeline stage {stage_id} of {pipeline_id} per docs/workflow-state.md,"
    " then run micro-validation before hand-off.\n"
)

_QUALITY_GATE_STEP = (
    "  - id: quality-gate\n"
    "    agent: coding-agent\n"
    "    prompt: Run ruff check, mypy and pytest; require 100 percent statement and branch coverage.\n"
)


class ArchonWorkflowMapper:
    """Maps a pipeline and its canonical stage order to an Archon YAML workflow."""

    def to_workflow_yaml(self, pipeline_id: str, stages: list[str]) -> str:
        """Render the Archon workflow document for pipeline_id over stages."""
        header_template = _HEADER_TEMPLATE
        stage_template = _STAGE_STEP_TEMPLATE
        gate_step = _QUALITY_GATE_STEP
        header = header_template.format(pipeline_id=pipeline_id)
        steps = [stage_template.format(stage_id=stage_id, pipeline_id=pipeline_id) for stage_id in stages]
        return header + "".join(steps) + gate_step
