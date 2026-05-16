"""Root Cause Left-Shift — InterventionType Enum.

Traceable to: FR-007, FR-023
"""

from enum import StrEnum


class InterventionType(StrEnum):
    """Types of interventions for left-shifting guards."""

    GUARD_STRENGTHENING = "GUARD_STRENGTHENING"
    NEW_GUARD = "NEW_GUARD"
    STEP_ADDITION = "STEP_ADDITION"
