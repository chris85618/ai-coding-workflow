"""CLS-001: Pipeline — Aggregate Root.

Traceable to: UC-001, UC-003, INV-001, INV-002-v2
INV-001: stage sequence is monotonically increasing.
INV-002-v2: auto_gate must return PASS before advance() is called.
"""

from __future__ import annotations

from dataclasses import dataclass

import icontract

from agentic_workflow.domain.models.enums import GateDecision, PipelineStatus

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

    Attributes:
        pipeline_id: Unique pipeline identifier.
        current_position: Current stage key from _STAGE_ORDER.
        status: Overall pipeline execution status.
        last_gate_decision: Most recent auto-gate decision.
    """

    pipeline_id: str
    current_position: str = "phase0"
    status: PipelineStatus = PipelineStatus.NOT_STARTED
    last_gate_decision: GateDecision | None = None

    def __post_init__(self) -> None:
        """Validate invariants after construction."""
        if self.current_position not in _STAGE_ORDER:
            raise ValueError(f"Invalid position: {self.current_position}")

    @icontract.require(
        lambda self: self.status == PipelineStatus.RUNNING,
        "Pipeline must be running to advance",
    )
    @icontract.require(
        lambda self: (
            self.last_gate_decision
            in (GateDecision.PASS, GateDecision.PASS_WITH_WARNINGS)
        ),
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
        """Advance pipeline to the next stage.

        Requires last_gate_decision to be PASS (INV-002-v2).
        Ensures position increases monotonically (INV-001).
        """
        current_idx = _STAGE_ORDER.index(self.current_position)
        if current_idx >= len(_STAGE_ORDER) - 1:
            raise ValueError("Pipeline is already at final stage")
        self.current_position = _STAGE_ORDER[current_idx + 1]

    @icontract.require(
        lambda self: self.status == PipelineStatus.NOT_STARTED,
        "Can only start a pipeline that has not started",
    )
    def start(self) -> None:
        """Transition pipeline from NOT_STARTED to RUNNING."""
        self.status = PipelineStatus.RUNNING

    @icontract.require(
        lambda self: self.status == PipelineStatus.RUNNING,
        "Can only complete a running pipeline",
    )
    def complete(self) -> None:
        """Mark the pipeline as completed."""
        self.status = PipelineStatus.COMPLETED

    def record_gate(self, decision: GateDecision) -> None:
        """Record the result of an auto-gate check.

        Args:
            decision: The gate decision result.
        """
        self.last_gate_decision = decision
