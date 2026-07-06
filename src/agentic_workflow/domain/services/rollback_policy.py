"""RollbackPolicy Domain Service — EC2 Neutrality degradation path.

Traceable to: FR-069, ADR-STR-029, FEA-030, ALG-018
Pipeline v2: when the dual-agent loop DIVERGES (intent drift / hallucination),
the system rolls back to the last invariant-clean universal base instead of
letting the drift contaminate downstream stages.
"""

from __future__ import annotations

import deal

from agentic_workflow.domain.enums import FixedPointResult
from agentic_workflow.domain.value_objects.rollback_decision import RollbackDecision

_UNIVERSAL_BASE_REF = "universal-base"


class RollbackPolicy:
    """ALG-018: Maps convergence outcomes onto the rigid degradation path."""

    UNIVERSAL_BASE_REF: str = _UNIVERSAL_BASE_REF

    @classmethod
    @deal.post(
        lambda result: isinstance(result, RollbackDecision),
        message="Policy always yields an explicit decision (no silent pass)",
    )
    def decide(cls, convergence: FixedPointResult, target_ref: str | None = None) -> RollbackDecision:
        """Decide whether the pipeline must roll back to the universal base.

        Only DIVERGING triggers the degradation path; every other outcome
        continues through the normal loop or alignment exit.
        """
        ref = target_ref or cls.UNIVERSAL_BASE_REF
        if convergence is FixedPointResult.DIVERGING:
            return RollbackDecision(
                should_rollback=True,
                target_ref=ref,
                reason="Intent drift detected: DIVERGING iteration trend (EC2 Neutrality)",
            )
        return RollbackDecision(should_rollback=False, target_ref=ref, reason="No divergence detected")
