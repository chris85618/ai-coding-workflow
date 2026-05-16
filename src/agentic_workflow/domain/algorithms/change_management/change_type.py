"""Change Management — ChangeType Enum.

Traceable to: FR-024, FR-025
"""

from enum import StrEnum


class ChangeType(StrEnum):
    """Types of changes supported by the protocol."""

    CREATE = "CREATE"
    MODIFY = "MODIFY"
    FIX = "FIX"
