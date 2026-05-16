"""StageStatus Enum — Stage iteration status."""

from enum import StrEnum


class StageStatus(StrEnum):
    """Stage iteration status. INV-003 enforces unidirectional transitions."""

    PENDING = "pending"
    ITERATING = "iterating"
    PASSED = "passed"
    FAILED = "failed"
