"""ALG-001: Convergence — Iteration fixed-point detection.

Traceable to: FR-012, FR-013, CLS-003, INV-004, INV-005-v2
Deterministic: no LLM, no I/O. Pure state machine logic.
"""

from __future__ import annotations

import icontract

from agentic_workflow.domain.models.enums import FixedPointResult, Severity

MAX_ITERATIONS = 10
DIVERGENCE_WINDOW = 3


@icontract.require(lambda iteration_count: iteration_count >= 0)
@icontract.require(lambda findings_per_iter: len(findings_per_iter) >= 0)
def check_convergence(
    iteration_count: int,
    findings_per_iter: list[list[str]],
    current_findings: list[str],
) -> FixedPointResult:
    """Determine whether the α/β iteration loop has converged.

    Fixed-point is reached when all remaining findings are YAGNI.
    Diverging is detected when finding count increases over last N iterations.

    Args:
        iteration_count: Number of completed iterations so far.
        findings_per_iter: List of finding lists from previous iterations.
        current_findings: Findings from the most recent Agent alpha critique.

    Returns:
        FixedPointResult indicating convergence status.
    """
    if iteration_count >= MAX_ITERATIONS:
        return FixedPointResult.MAX_ITERATIONS

    # Fixed-point: only YAGNI findings remain
    non_yagni = [f for f in current_findings if not f.startswith("YAGNI:")]
    if not non_yagni:
        return FixedPointResult.REACHED

    # Divergence detection: count increasing over last DIVERGENCE_WINDOW iters
    if len(findings_per_iter) >= DIVERGENCE_WINDOW:
        recent_counts = [len(f) for f in findings_per_iter[-DIVERGENCE_WINDOW:]]
        if all(
            recent_counts[i] <= recent_counts[i + 1]
            for i in range(len(recent_counts) - 1)
        ) and recent_counts[-1] > recent_counts[0]:
            return FixedPointResult.DIVERGING

    return FixedPointResult.NOT_REACHED


@icontract.require(lambda result: isinstance(result, FixedPointResult))
def should_auto_pass(result: FixedPointResult) -> bool:
    """Determine if the auto-gate should PASS given a convergence result.

    Per ADR-STR-003: both REACHED and DIVERGING auto-pass (no blocking).
    MAX_ITERATIONS also auto-passes with a warning logged.

    Args:
        result: The convergence check result.

    Returns:
        True if the gate should PASS, False if iteration should continue.
    """
    return result in (
        FixedPointResult.REACHED,
        FixedPointResult.DIVERGING,
        FixedPointResult.MAX_ITERATIONS,
    )
