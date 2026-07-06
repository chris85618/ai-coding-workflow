"""GovernanceCostModel Domain Service — Dynamic HITL trigger (delayed intervention).

Traceable to: FR-071, ADR-STR-029, FEA-030, ALG-017
Pipeline v2: routine mid-stage HITL gates are removed. A human is summoned
only when the accumulated governance cost (kappa) crosses a dynamic threshold
or the loop diverges — the human acts as macro-governor, not micro-supervisor.
"""

from __future__ import annotations

import deal


class GovernanceCostModel:
    """ALG-017: Quantifies governance cost to decide when HITL is required.

    kappa = iterations * ITERATION_WEIGHT + debts * DEBT_WEIGHT.
    All methods are pure and stateless.
    """

    HITL_THRESHOLD: float = 10.0
    ITERATION_WEIGHT: float = 1.0
    DEBT_WEIGHT: float = 0.5

    @classmethod
    @deal.pre(lambda _: _.iteration_count >= 0 and _.debt_count >= 0)
    @deal.post(lambda result: result >= 0.0, message="Governance cost is non-negative")
    def accumulated_cost(cls, iteration_count: int, debt_count: int) -> float:
        """Compute the accumulated governance cost kappa for the session."""
        return iteration_count * cls.ITERATION_WEIGHT + debt_count * cls.DEBT_WEIGHT

    @classmethod
    @deal.pre(lambda _: _.iteration_count >= 0 and _.debt_count >= 0)
    @deal.has()
    def should_trigger_hitl(cls, iteration_count: int, debt_count: int, diverging: bool) -> bool:
        """Decide whether delayed HITL intervention must be summoned.

        Divergence always triggers HITL (unresolvable conflict); otherwise
        only a kappa above HITL_THRESHOLD does.
        """
        return diverging or cls.accumulated_cost(iteration_count, debt_count) > cls.HITL_THRESHOLD
