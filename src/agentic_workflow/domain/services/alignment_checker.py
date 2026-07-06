"""AlignmentChecker Domain Service — Diverge → Converge → Align closure.

Traceable to: FR-072, ADR-STR-029, FEA-030, ALG-020
Feedback-control reframing (Self-Correction as Feedback Control): after the
dual-agent loop converges, the result is aligned against documentation,
traceability and consistency evidence. Any misalignment is fed back to the
divergent agent (alpha) for deep extension until a full solution emerges.
"""

from __future__ import annotations

import deal

_ALIGN_PREFIX = "ALIGN:"

# Variable binding for constant access (TC-QUALITY-014).
_align_prefix = _ALIGN_PREFIX


class AlignmentChecker:
    """ALG-020: Validates converged output against the recorded design reality.

    All methods are pure and stateless; evidence gathering belongs to outer
    layers (traceability matrix, docs, consistency scans).
    """

    ALIGN_PREFIX: str = _ALIGN_PREFIX

    @classmethod
    @deal.post(
        lambda result: all(finding.startswith(_align_prefix) for finding in result),
        message="Misalignments are tagged for alpha feedback routing",
    )
    def find_misalignments(
        cls,
        traceability_issues: list[str],
        consistency_issues: list[str],
    ) -> list[str]:
        """Merge alignment evidence into tagged findings for the loop.

        Args:
            traceability_issues: Broken links found in the traceability chain.
            consistency_issues: Contradictions between output and design docs.

        Returns:
            ALIGN-tagged findings; empty when the fixed point is a full solution.
        """
        merged = [issue for issue in traceability_issues + consistency_issues if issue]
        return [f"{_align_prefix} {issue}" for issue in merged]

    @classmethod
    @deal.has()
    def is_aligned(cls, misalignments: list[str]) -> bool:
        """True when no misalignment remains — the fixed point is a full solution."""
        return not misalignments
