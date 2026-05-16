"""Aggregate Root for the Pipeline domain."""

from __future__ import annotations

from dataclasses import dataclass, field

import icontract

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


@dataclass
class Pipeline:
    """Aggregate root representing the entire workflow pipeline.

    It manages the lifecycle of stages and enforces cross-stage invariants.
    """

    pipeline_id: str
    current_position: str = "phase0"
    status: PipelineStatus = PipelineStatus.NOT_STARTED
    last_gate_decision: GateDecision | None = None
    stages: dict[str, Stage] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Ensure all required stages are initialized."""
        if self.current_position not in _STAGE_ORDER:
            raise ValueError(f"Invalid position: {self.current_position}")

        # Initialize default stages if not provided
        if not self.stages:
            for stage_id in _STAGE_ORDER:
                name = stage_id.replace("_", " ").title()
                self.stages[stage_id] = Stage(stage_id=stage_id, name=name)

    @icontract.require(
        lambda self: self.status == PipelineStatus.RUNNING,
        "Pipeline must be running to advance",
    )
    @icontract.require(
        lambda self: self.last_gate_decision in (GateDecision.PASS, GateDecision.PASS_WITH_WARNINGS),
        "Auto-gate must PASS before advance (INV-002-v2)",
    )
    @icontract.snapshot(
        lambda self: _STAGE_ORDER.index(self.current_position),
        name="old_idx",
    )
    @icontract.ensure(
        lambda OLD, self: _STAGE_ORDER.index(self.current_position) > OLD.old_idx,
        "Position must advance monotonically (INV-001)",
    )
    def advance(self) -> None:
        """Advance pipeline to the next stage."""
        current_idx = _STAGE_ORDER.index(self.current_position)
        if current_idx >= len(_STAGE_ORDER) - 1:
            raise ValueError("Pipeline is already at final stage")

        # Mark current stage as PASSED before moving
        self.stages[self.current_position].transition(StageStatus.PASSED)

        self.current_position = _STAGE_ORDER[current_idx + 1]

    def start(self) -> None:
        """Start the pipeline."""
        if self.status != PipelineStatus.NOT_STARTED:
            raise ValueError("Can only start a pipeline that has not started")
        self.status = PipelineStatus.RUNNING

    def complete(self) -> None:
        """Complete the pipeline."""
        if self.status != PipelineStatus.RUNNING:
            raise ValueError("Can only complete a running pipeline")
        self.status = PipelineStatus.COMPLETED

    def record_gate(self, decision: GateDecision) -> None:
        """Record gate decision for the current position."""
        self.last_gate_decision = decision

    def update_stage_findings(self, findings: list[str]) -> None:
        """Delegate findings update to the current stage entity."""
        stage = self.stages.get(self.current_position)
        if not stage:
            raise ValueError(f"Current stage {self.current_position} not found")
        for finding in findings:
            stage.add_finding(finding)

    def increment_stage_iteration(self) -> None:
        """Delegate iteration increment to the current stage entity."""
        stage = self.stages.get(self.current_position)
        if not stage:
            raise ValueError(f"Current stage {self.current_position} not found")
        stage.increment_iteration()
        if stage.status == StageStatus.PENDING:
            stage.transition(StageStatus.ITERATING)
