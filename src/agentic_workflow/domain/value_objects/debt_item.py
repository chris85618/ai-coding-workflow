"""DebtItem Value Object — Dynamic debt absorbed from gate failures.

Traceable to: FR-068, ADR-STR-029, FEA-030
Pipeline v2: gate failures are absorbed as debt instead of hard-stopping the flow.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import deal

from agentic_workflow.domain.enums import DebtSource, Severity

_DEBT_ID_PREFIX = "DEBT-"


@dataclass(frozen=True)
class DebtItem:
    """Immutable dynamic-debt record produced by the debt accumulator.

    Construction enforces the DEBT-xxx traceable id format so downstream
    registries never receive malformed identifiers (left-shifted validation).
    """

    debt_id: str
    title: str
    source: DebtSource
    severity: Severity
    description: str = field(default="")

    def __post_init__(self) -> None:
        """Validate the traceable id format and non-empty title.

        :raises ValueError: if debt_id or title violate the format contract
        """
        debt_prefix = _DEBT_ID_PREFIX
        if not self.debt_id.startswith(debt_prefix):
            raise ValueError(f"DebtItem id must start with {debt_prefix}: {self.debt_id}")
        if not self.title:
            raise ValueError("DebtItem title must be non-empty")

    @deal.post(lambda result: isinstance(result, dict) and "debt_id" in result)
    def as_dict(self) -> dict[str, str]:
        """Serialize the debt item into a JSON-compatible mapping."""
        return {
            "debt_id": self.debt_id,
            "title": self.title,
            "source": self.source.value,
            "severity": self.severity.value,
            "description": self.description,
        }
