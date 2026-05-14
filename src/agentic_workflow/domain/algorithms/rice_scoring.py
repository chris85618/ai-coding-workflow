"""ALG-004: RICE Scoring — Prioritization formula.

Traceable to: FR-010, FR-011, INV-015
Deterministic formula: RICE = (Reach * Impact * Confidence) / Effort
"""

from __future__ import annotations

import icontract

VALID_IMPACT_VALUES = frozenset({0.5, 1.0, 2.0, 3.0})


@icontract.require(lambda effort: effort > 0, "Effort must be positive")
@icontract.require(
    lambda reach: 1 <= reach <= 100, "Reach must be between 1 and 100"
)
@icontract.require(
    lambda impact: impact in VALID_IMPACT_VALUES,
    "Impact must be 0.5, 1.0, 2.0, or 3.0",
)
@icontract.require(
    lambda confidence: 0.5 <= confidence <= 1.0,
    "Confidence must be between 0.5 and 1.0",
)
@icontract.ensure(
    lambda result, reach, impact, confidence, effort: abs(
        result - (reach * impact * confidence) / effort
    ) < 1e-9,
    "RICE formula must be exact (INV-015)",
)
def rice_score(
    reach: int, impact: float, confidence: float, effort: float
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
