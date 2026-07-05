"""Entity for a single pipeline stage."""

from __future__ import annotations

from dataclasses import dataclass, field

import deal

from agentic_workflow.domain.enums import StageStatus
from agentic_workflow.domain.value_objects.findings import Findings

_STATUS_ORDER = {
    StageStatus.PENDING: 0,
    StageStatus.ITERATING: 1,
    StageStatus.PASSED: 2,
    StageStatus.FAILED: 2,
}

MAX_ITERATIONS = 10

# Variable bindings for constant access (TC-QUALITY-014).
_status_order = _STATUS_ORDER
_max_iterations = MAX_ITERATIONS


@deal.inv(
    lambda self: getattr(self, "iteration_count", 0) <= _max_iterations,
    message="Iteration count must not exceed maximum (INV-004)",
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

    @deal.ensure(
        lambda self, new_status, result: self.status == new_status,
        message="Transition must land on the requested status (INV-003)",
    )
    @deal.raises(ValueError)
    @deal.reason(
        ValueError,
        lambda _: _status_order[_.new_status] < _status_order[_.self.status],
    )
    def transition(self, new_status: StageStatus) -> None:
        """Transition stage to a new status.

        :raises ValueError: if the transition would regress the status order
        """
        status_order = _status_order
        if status_order[new_status] < status_order[self.status]:
            raise ValueError(f"Cannot regress from {self.status} to {new_status}")
        self.status = new_status

    @deal.pre(
        lambda self: self.iteration_count < _max_iterations,
        message="Iteration count already at maximum",
    )
    def increment_iteration(self) -> None:
        """Increment the iteration counter."""
        self.iteration_count += 1

    def add_finding(self, finding: str) -> None:
        """Add a finding via VO update."""
        self.findings = self.findings.add(finding)
