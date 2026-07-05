"""Aggregate Root for the Pipeline domain."""

from __future__ import annotations

from dataclasses import dataclass, field

import deal

from agentic_workflow.domain.entities.stage import Stage
from agentic_workflow.domain.enums import GateDecision, PipelineStatus, StageStatus

_STAGE_ORDER = [
    "phase0",
    "phase1",
    "phase2",
    "stage3",
    "stage4",
    "stage5",
    "stage6",
    "stage7",
    "stage8",
    "phase9",
    "phase10",
]

# Variable binding for constant access (TC-QUALITY-014).
_stage_order = _STAGE_ORDER


def _default_stages() -> dict[str, Stage]:
    """Build the canonical stage entities for every pipeline position."""
    stage_order = _stage_order
    return {stage_id: Stage(stage_id=stage_id, name=stage_id.replace("_", " ").title()) for stage_id in stage_order}


@deal.inv(
    # hasattr tolerates the field-by-field assignments deal validates while the
    # dataclass __init__ is still populating the instance; once stages exists it
    # is always a complete mapping (default factory or __post_init__ check), so
    # the invariant holds at every observable moment — including plain setattr.
    lambda self: self.current_position in self.stages if hasattr(self, "stages") else True,
    message="Current position must always resolve to a stage entity (INV-016)",
)
@dataclass
class Pipeline:
    """Aggregate root representing the entire workflow pipeline.

    It manages the lifecycle of stages and enforces cross-stage invariants.
    """

    pipeline_id: str
    current_position: str = "phase0"
    status: PipelineStatus = PipelineStatus.NOT_STARTED
    last_gate_decision: GateDecision | None = None
    stages: dict[str, Stage] = field(default_factory=_default_stages)

    @property
    def current_stage(self) -> Stage:
        """Get the stage entity for the current position.

        INV-016 guarantees the current position always resolves to a stage.
        """
        return self.stages[self.current_position]

    def __post_init__(self) -> None:
        """Ensure all required stages are initialized.

        :raises ValueError: if the position is unknown or supplied stages are incomplete
        """
        stage_order = _stage_order
        if self.current_position not in stage_order:
            raise ValueError(f"Invalid position: {self.current_position}")

        # Aggregate consistency boundary: every pipeline position must have a stage
        missing = [stage_id for stage_id in stage_order if stage_id not in self.stages]
        if missing:
            raise ValueError(f"Stages missing required ids: {missing}")

    @deal.pre(
        lambda self: self.status == PipelineStatus.RUNNING,
        message="Pipeline must be running to advance",
    )
    @deal.pre(
        lambda self: self.last_gate_decision in (GateDecision.PASS, GateDecision.PASS_WITH_WARNINGS),
        message="Auto-gate must PASS before advance (INV-002-v2)",
    )
    @deal.ensure(
        # Advancing always lands one slot past a freshly PASSED stage, which
        # pins the post-state of the monotonic move without an OLD snapshot.
        lambda self, result: (
            _stage_order.index(self.current_position) > 0
            and self.stages[_stage_order[_stage_order.index(self.current_position) - 1]].status == StageStatus.PASSED
        ),
        message="Position must advance monotonically (INV-001)",
    )
    @deal.raises(ValueError)
    @deal.reason(
        ValueError,
        lambda self: _stage_order.index(self.current_position) >= len(_stage_order) - 1,
    )
    def advance(self) -> None:
        """Advance pipeline to the next stage.

        :raises ValueError: if the pipeline is already at the final stage
        """
        current_idx = _stage_order.index(self.current_position)
        if current_idx >= len(_stage_order) - 1:
            raise ValueError("Pipeline is already at final stage")

        # Mark current stage as PASSED before moving
        self.stages[self.current_position].transition(StageStatus.PASSED)

        self.current_position = _stage_order[current_idx + 1]

    @deal.pre(
        lambda self: self.status == PipelineStatus.NOT_STARTED,
        message="Can only start a pipeline that has not started",
    )
    def start(self) -> None:
        """Start the pipeline."""
        self.status = PipelineStatus.RUNNING

    @deal.pre(
        lambda self: self.status == PipelineStatus.RUNNING,
        message="Can only complete a running pipeline",
    )
    def complete(self) -> None:
        """Complete the pipeline."""
        self.status = PipelineStatus.COMPLETED

    def record_gate(self, decision: GateDecision) -> None:
        """Record gate decision for the current position."""
        self.last_gate_decision = decision

    def update_stage_findings(self, findings: list[str]) -> None:
        """Delegate findings update to the current stage entity."""
        for finding in findings:
            self.current_stage.add_finding(finding)

    def advance_stage(self, decision: GateDecision) -> None:
        """Centralized method to advance the stage.

        Mandates gate decision recording before movement.
        """
        self.record_gate(decision)
        if decision in (GateDecision.PASS, GateDecision.PASS_WITH_WARNINGS):
            self.advance()
        else:
            self.fail_validation(f"Gate failed with decision: {decision}")

    def fail_validation(self, reason: str) -> None:
        """Handle validation failure.

        Transitions current stage to FAILED and records the reason.
        INV-016 guarantees the current stage exists.
        """
        stage = self.stages[self.current_position]
        stage.transition(StageStatus.FAILED)
        stage.add_finding(f"Validation Error: {reason}")
        self.status = PipelineStatus.FAILED

    def increment_stage_iteration(self) -> None:
        """Delegate iteration increment to the current stage entity."""
        stage = self.current_stage
        stage.increment_iteration()
        if stage.status == StageStatus.PENDING:
            stage.transition(StageStatus.ITERATING)
