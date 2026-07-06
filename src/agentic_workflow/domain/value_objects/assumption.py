"""Assumption Value Object — L2 output-affecting assumption (rigid constraint).

Traceable to: FR-070, ADR-STR-029, FEA-030
Pipeline v2: every retro emits rigid constraints that are injected into the
next session START node (self-bootstrapping left-shift, the Ouroboros closure).
"""

from __future__ import annotations

from dataclasses import dataclass, field

_ASSUMPTION_ID_PREFIX = "ASM-"


@dataclass(frozen=True)
class Assumption:
    """Immutable output-affecting assumption registered for injection.

    Construction enforces the ASM-xxx id format and a non-empty statement,
    replacing downstream guard checks (left-shifted validation).
    """

    assumption_id: str
    statement: str
    source_id: str = field(default="")
    active: bool = field(default=True)

    def __post_init__(self) -> None:
        """Validate the traceable id format and non-empty statement.

        :raises ValueError: if assumption_id or statement violate the contract
        """
        asm_prefix = _ASSUMPTION_ID_PREFIX
        if not self.assumption_id.startswith(asm_prefix):
            raise ValueError(f"Assumption id must start with {asm_prefix}: {self.assumption_id}")
        if not self.statement:
            raise ValueError("Assumption statement must be non-empty")
