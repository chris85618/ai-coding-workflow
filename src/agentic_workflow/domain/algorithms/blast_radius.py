"""ALG-003: BlastRadius — Impact severity classification.

Traceable to: FR-008, FR-009, INV-012
INV-012: blast_radius 0 → COSMETIC; blast_radius > 0 allows any severity.
Deterministic: pure calculation, no LLM.
OO Design: BlastRadiusClassifier class encapsulates all logic (ALG-010 OO mandate).
"""

from __future__ import annotations

import deal

from agentic_workflow.domain.enums import Severity


class BlastRadiusClassifier:
    """ALG-003: Classifies impact severity from blast radius and cross-stage count.

    INV-012: blast_radius == 0 must always yield Severity.COSMETIC.
    All classification thresholds are class-level constants for testability.
    """

    # Severity thresholds (inclusive lower bound)
    CRITICAL_RADIUS: int = 10
    CRITICAL_STAGES: int = 3
    HIGH_RADIUS: int = 5
    HIGH_STAGES: int = 2
    MEDIUM_RADIUS: int = 2

    @classmethod
    @deal.pre(
        lambda _: _.blast_radius >= 0 and _.cross_stage >= 0,
        message="Blast radius and cross-stage counts are cardinalities and cannot be negative",
    )
    @deal.ensure(
        lambda _: (_.blast_radius == 0 and _.result == Severity.COSMETIC) or _.blast_radius > 0,
        message="Zero blast radius must classify as COSMETIC (INV-012)",
    )
    def classify(cls, blast_radius: int, cross_stage: int) -> Severity:
        """Classify impact severity based on blast radius and cross-stage count.

        Args:
            blast_radius: Number of directly affected IDs.
            cross_stage: Number of pipeline stages crossed by the change.

        Returns:
            Severity classification.
        """
        if blast_radius == 0:
            return Severity.COSMETIC
        if blast_radius >= cls.CRITICAL_RADIUS or cross_stage >= cls.CRITICAL_STAGES:
            return Severity.CRITICAL
        if blast_radius >= cls.HIGH_RADIUS or cross_stage >= cls.HIGH_STAGES:
            return Severity.HIGH
        if blast_radius >= cls.MEDIUM_RADIUS:
            return Severity.MEDIUM
        return Severity.LOW
