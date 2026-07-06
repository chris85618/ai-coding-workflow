"""DebtAccumulator Domain Service — Absorbs gate failures into dynamic debt.

Traceable to: FR-068, ADR-STR-029, FEA-030, ALG-016
Pipeline v2: SonarCloud / security-audit failures no longer hard-stop the
pipeline; they are converted into DEBT items that feed the next iteration
(the accumulator absorbs disturbance instead of breaking continuity).
"""

from __future__ import annotations

import deal

from agentic_workflow.domain.enums import DebtSource, GateDecision, Severity
from agentic_workflow.domain.value_objects.debt_item import DebtItem


class DebtAccumulator:
    """ALG-016: Converts gate failures into dynamic debt items.

    All methods are pure and stateless; persistence belongs to outer layers.
    """

    @classmethod
    @deal.pre(lambda _: _.start_index >= 1, message="Debt numbering is 1-based (INV-026)")
    @deal.post(lambda result: all(item.debt_id.startswith("DEBT-") for item in result))
    def absorb(
        cls,
        source: DebtSource,
        severity: Severity,
        descriptions: list[str],
        start_index: int,
    ) -> list[DebtItem]:
        """Convert failure descriptions into sequentially numbered debt items.

        Args:
            source: Origin of the failures being absorbed.
            severity: Severity assigned to every absorbed item.
            descriptions: Human-readable failure descriptions.
            start_index: 1-based index for the first generated DEBT id.

        Returns:
            One DebtItem per non-empty description, numbered from start_index.
        """
        non_empty = [text for text in descriptions if text]
        return [
            DebtItem(
                debt_id=f"DEBT-{start_index + offset:03d}",
                title=text[:80],
                source=source,
                severity=severity,
                description=text,
            )
            for offset, text in enumerate(non_empty)
        ]

    @classmethod
    @deal.pre(lambda _: _.debt_count >= 0, message="Debt count is a cardinality (non-negative)")
    @deal.post(
        lambda result: result in (GateDecision.PASS, GateDecision.PASS_WITH_WARNINGS),
        message="Absorbed debt never hard-fails the gate (ADR-STR-029)",
    )
    def gate_decision_for(cls, debt_count: int) -> GateDecision:
        """Derive the continuous-flow gate decision after absorption.

        Debt absorption guarantees the pipeline keeps moving: the worst
        outcome is PASS_WITH_WARNINGS, never FAIL.
        """
        if debt_count == 0:
            return GateDecision.PASS
        return GateDecision.PASS_WITH_WARNINGS
