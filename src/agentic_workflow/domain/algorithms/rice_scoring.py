"""ALG-004: RICE Scoring — Prioritization formula.

Traceable to: FR-010, FR-011, INV-015
Deterministic formula: RICE = (Reach * Impact * Confidence) / Effort
OO Design: RiceScorer class encapsulates all logic (ALG-010 OO mandate).
Module-level function retained as backward-compat facade.
"""

from __future__ import annotations

import math

import deal

VALID_IMPACT_VALUES: frozenset[float] = frozenset({0.5, 1.0, 2.0, 3.0})

# Variable binding for constant access (TC-QUALITY-014).
_valid_impact_values = VALID_IMPACT_VALUES


class RiceScorer:
    """ALG-004: Calculates RICE prioritization scores.

    INV-015: RICE formula is exact — (reach * impact * confidence) / effort.
    Constraint values are class-level constants for testability and documentation.
    """

    VALID_IMPACT_VALUES: frozenset[float] = VALID_IMPACT_VALUES
    REACH_MIN: int = 1
    REACH_MAX: int = 100
    CONFIDENCE_MIN: float = 0.5
    CONFIDENCE_MAX: float = 1.0

    @classmethod
    @deal.pre(lambda _: _.effort > 0, message="Effort must be positive")
    @deal.pre(lambda _: 1 <= _.reach <= 100, message="Reach must be between 1 and 100")
    @deal.pre(
        lambda _: _.impact in _valid_impact_values,
        message="Impact must be 0.5, 1.0, 2.0, or 3.0",
    )
    @deal.pre(
        lambda _: 0.5 <= _.confidence <= 1.0,
        message="Confidence must be between 0.5 and 1.0",
    )
    @deal.ensure(
        # math.isclose keeps INV-015 well-defined even when a denormal effort
        # overflows the quotient to infinity (abs(inf - inf) is NaN).
        lambda _: math.isclose(_.result, (_.reach * _.impact * _.confidence) / _.effort, rel_tol=1e-9),
        message="RICE formula must be exact (INV-015)",
    )
    def score(
        cls,
        reach: int,
        impact: float,
        confidence: float,
        effort: float,
    ) -> float:
        """Calculate the RICE prioritization score.

        Args:
            reach: Number of users/items affected (1-100).
            impact: Business impact multiplier (0.5, 1.0, 2.0, 3.0).
            confidence: Estimate confidence (0.5-1.0).
            effort: Effort in person-days (>0).

        Returns:
            RICE score as a float.
        """
        return (reach * impact * confidence) / effort
