"""ALG-003: BlastRadius — Impact severity classification.

Traceable to: FR-008, FR-009, INV-012
INV-012: blast_radius 0 → COSMETIC; blast_radius > 0 allows any severity.
Deterministic: pure calculation, no LLM.
"""

from __future__ import annotations

import icontract

from agentic_workflow.domain.models.enums import Severity


@icontract.ensure(
    lambda result, blast_radius: (blast_radius == 0 and result == Severity.COSMETIC)
    or blast_radius > 0,
    "Zero blast radius must classify as COSMETIC (INV-012)",
)
def classify_severity(blast_radius: int, cross_stage: int) -> Severity:
    """Classify impact severity based on blast radius and cross-stage count.

    Args:
        blast_radius: Number of directly affected IDs.
        cross_stage: Number of pipeline stages crossed by the change.

    Returns:
        Severity classification.
    """
    if blast_radius == 0:
        return Severity.COSMETIC
    if blast_radius >= 10 or cross_stage >= 3:
        return Severity.CRITICAL
    if blast_radius >= 5 or cross_stage >= 2:
        return Severity.HIGH
    if blast_radius >= 2:
        return Severity.MEDIUM
    return Severity.LOW
