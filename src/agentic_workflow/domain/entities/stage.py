"""Entity for a single pipeline stage."""

from __future__ import annotations

from dataclasses import dataclass, field

import icontract

from agentic_workflow.domain.enums import StageStatus
from agentic_workflow.domain.value_objects.findings import Findings

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
    """A single pipeline stage entity.

    Attributes:
        stage_id: Unique stage identifier (e.g., "stage3").
        name: Human-readable stage name.
        status: Current execution status.
        iteration_count: Number of alpha/beta iterations performed.
        findings: Accumulated findings Value Object.
    """

    stage_id: str
    name: str
    status: StageStatus = StageStatus.PENDING
    iteration_count: int = 0
    findings: Findings = field(default_factory=Findings)

    @icontract.snapshot(lambda self: _STATUS_ORDER[self.status], name="old_rank")
    @icontract.ensure(
        lambda OLD, self: _STATUS_ORDER[self.status] >= OLD.old_rank,
        "Status must transition unidirectionally (INV-003)",
    )
    def transition(self, new_status: StageStatus) -> None:
        """Transition stage to a new status."""
        if _STATUS_ORDER[new_status] < _STATUS_ORDER[self.status]:
            raise ValueError(f"Cannot regress from {self.status} to {new_status}")
        self.status = new_status

    @icontract.require(
        lambda self: self.iteration_count < MAX_ITERATIONS,
        "Iteration count already at maximum",
    )
    def increment_iteration(self) -> None:
        """Increment the iteration counter."""
        self.iteration_count += 1

    def add_finding(self, finding: str) -> None:
        """Add a finding via VO update."""
        self.findings = self.findings.add(finding)
