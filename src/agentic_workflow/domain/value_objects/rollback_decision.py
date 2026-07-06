"""RollbackDecision Value Object — Degradation-path verdict on divergence.

Traceable to: FR-069, ADR-STR-029, FEA-030
Pipeline v2: DIVERGING iterations trigger a rigid degradation path back to the
universal base (EC2 Neutrality) instead of silently auto-passing.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RollbackDecision:
    """Immutable verdict describing whether and where to roll back."""

    should_rollback: bool
    target_ref: str = field(default="universal-base")
    reason: str = field(default="")

    def __post_init__(self) -> None:
        """Validate that a rollback target is always resolvable.

        :raises ValueError: if target_ref is empty
        """
        if not self.target_ref:
            raise ValueError("RollbackDecision target_ref must be non-empty")
