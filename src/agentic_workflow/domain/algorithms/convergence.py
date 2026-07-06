"""ALG-001: Convergence — Iteration fixed-point detection.

Traceable to: FR-012, FR-013, CLS-003, INV-004, INV-005-v2
Deterministic: no LLM, no I/O. Pure state machine logic.
OO Design: ConvergenceDetector class encapsulates all logic (ALG-010 OO mandate).
"""

from __future__ import annotations

import deal

from agentic_workflow.domain.entities.stage import MAX_ITERATIONS
from agentic_workflow.domain.enums import FixedPointResult

DIVERGENCE_WINDOW = 3


class ConvergenceDetector:
    """ALG-001: Detects fixed-point convergence in the α/β iteration loop.

    Encapsulates convergence and auto-gate logic.
    All methods are stateless and may be called as class methods.
    """

    MAX_ITERATIONS: int = MAX_ITERATIONS
    DIVERGENCE_WINDOW: int = DIVERGENCE_WINDOW

    @classmethod
    @deal.pre(lambda _: _.iteration_count >= 0)
    def check_convergence(
        cls,
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
        if iteration_count >= cls.MAX_ITERATIONS:
            return FixedPointResult.MAX_ITERATIONS

        # Fixed-point: only YAGNI findings remain
        non_yagni = [f for f in current_findings if not f.startswith("YAGNI:")]
        if not non_yagni:
            return FixedPointResult.REACHED

        # Divergence detection: count increasing over last DIVERGENCE_WINDOW iters
        if len(findings_per_iter) >= cls.DIVERGENCE_WINDOW:
            recent_counts = [len(f) for f in findings_per_iter[-cls.DIVERGENCE_WINDOW :]]
            if (
                all(recent_counts[i] <= recent_counts[i + 1] for i in range(len(recent_counts) - 1))
                and recent_counts[-1] > recent_counts[0]
            ):
                return FixedPointResult.DIVERGING

        return FixedPointResult.NOT_REACHED

    @classmethod
    @deal.pre(lambda _: isinstance(_.result, FixedPointResult))
    @deal.post(
        lambda result: result in ("beta", "exit_loop", "rollback"),
        message="Loop routing is a closed decision set (ADR-STR-029)",
    )
    def route_fixed_point(cls, result: FixedPointResult) -> str:
        """Route the iteration loop for a convergence outcome (Pipeline v2).

        NOT_REACHED continues the loop via beta; DIVERGING enters the
        degradation path (rollback to universal base); REACHED and
        MAX_ITERATIONS exit toward the alignment check.

        Args:
            result: The convergence check result.

        Returns:
            Edge name: "beta" | "exit_loop" | "rollback".
        """
        if result is FixedPointResult.NOT_REACHED:
            return "beta"
        if result is FixedPointResult.DIVERGING:
            return "rollback"
        return "exit_loop"

    @classmethod
    @deal.pre(lambda _: isinstance(_.result, FixedPointResult))
    def should_auto_pass(cls, result: FixedPointResult) -> bool:
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
