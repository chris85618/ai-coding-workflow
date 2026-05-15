"""CLS-002: Stage — Value Object for a single pipeline stage.

Traceable to: UC-003, INV-003, INV-004
INV-003: status transitions are unidirectional (PENDING→ITERATING→PASSED).
INV-004: iteration_count <= 10.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import icontract

from agentic_workflow.domain.models.enums import StageStatus

_STATUS_ORDER = {
    StageStatus.PENDING: 0,
    StageStatus.ITERATING: 1,
    StageStatus.PASSED: 2,
    StageStatus.FAILED: 2,
}

MAX_ITERATIONS = 10


@icontract.invariant(
    lambda self: self.iteration_count <= MAX_ITERATIONS,
    "Iteration count must not exceed maximum (INV-004)",
)
@dataclass
class Stage:
    """A single pipeline stage with iteration tracking.

    Attributes:
        stage_id: Unique stage identifier (e.g., "stage3").
        name: Human-readable stage name.
        status: Current execution status.
        iteration_count: Number of α/β iterations performed.
        findings: Accumulated findings from Agent α.
    """

    stage_id: str
    name: str
    status: StageStatus = StageStatus.PENDING
    iteration_count: int = 0
    findings: list[str] = field(default_factory=list)

    @icontract.snapshot(lambda self: _STATUS_ORDER[self.status], name="old_rank")
    @icontract.ensure(
        lambda OLD, self: _STATUS_ORDER[self.status] >= OLD.old_rank,
        "Status must transition unidirectionally (INV-003)",
    )
    def transition(self, new_status: StageStatus) -> None:
        """Transition stage to a new status.

        Args:
            new_status: The target status to transition to.

        Raises:
            ValueError: If the transition would be invalid.
        """
        if _STATUS_ORDER[new_status] < _STATUS_ORDER[self.status]:
            raise ValueError(f"Cannot regress from {self.status} to {new_status}")
        self.status = new_status

    @icontract.require(
        lambda self: self.iteration_count < MAX_ITERATIONS,
        "Iteration count already at maximum",
    )
    def increment_iteration(self) -> None:
        """Increment the iteration counter by one."""
        self.iteration_count += 1

    def add_finding(self, finding: str) -> None:
        """Append a finding from Agent alpha critique.

        Args:
            finding: Finding description string.
        """
        self.findings.append(finding)
