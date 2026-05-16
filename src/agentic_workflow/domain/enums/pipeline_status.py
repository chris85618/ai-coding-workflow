"""PipelineStatus Enum — Pipeline execution status.

All enums are str-based for JSON serialization compatibility.
"""

from enum import StrEnum


class PipelineStatus(StrEnum):
    """Pipeline execution status. INV-001 enforces unidirectional transitions."""

    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
