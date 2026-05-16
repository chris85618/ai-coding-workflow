"""Value Object for canonical Traceable IDs (e.g., FR-001)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from agentic_workflow.domain.enums.id_prefix import IDPrefix


@dataclass(frozen=True)
class TraceableIdVO:
    """Immutable Value Object for a Traceable ID.

    Enforces format validation (PREFIX-SEQ) in the constructor.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the ID format on initialization."""
        pattern = r"^([A-Z]+)-(\d{3})$"
        match = re.match(pattern, self.value)
        if not match:
            raise ValueError(f"Invalid Traceable ID format: {self.value}. Expected PREFIX-001.")

        prefix_str, _ = match.groups()
        # Verify prefix is valid in the system
        try:
            IDPrefix(prefix_str)
        except ValueError as err:
            raise ValueError(f"Unknown ID prefix: {prefix_str}") from err

    @classmethod
    def create(cls, prefix: IDPrefix, sequence: int) -> TraceableIdVO:
        """Factory method to create a VO from components."""
        return cls(f"{prefix.value}-{sequence:03d}")

    def __str__(self) -> str:
        """Return the string representation of the ID."""
        return self.value
