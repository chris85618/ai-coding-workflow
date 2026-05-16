"""Orchestrator — PhaseStatus Enum.

Traceable to: FR-002, FR-003, FR-017, FR-018
"""

from enum import StrEnum


class PhaseStatus(StrEnum):
    """Status of a workflow phase."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
