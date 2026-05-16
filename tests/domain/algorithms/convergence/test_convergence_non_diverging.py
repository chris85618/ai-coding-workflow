"""Cover plateau and non-monotonic branches in convergence detection."""

from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector
from agentic_workflow.domain.enums import FixedPointResult


class TestConvergenceNonDiverging:
    """Cover plateau and non-monotonic branches."""

    def test_convergence_non_diverging_plateau(self) -> None:
        """Plateau (identical lengths) ->NOT_REACHED."""
        history = [["A", "B", "C"], ["A", "B", "C"], ["A", "B", "C"]]
        result = ConvergenceDetector.check_convergence(
            iteration_count=3,
            findings_per_iter=history,
            current_findings=["CRITICAL: still here"],
        )
        assert result == FixedPointResult.NOT_REACHED

    def test_convergence_decreasing_then_increasing_not_diverging(self) -> None:
        """Non-monotonic ([3, 2, 3]) ->NOT_REACHED."""
        history = [["A", "B", "C"], ["A", "B"], ["A", "B", "C"]]
        result = ConvergenceDetector.check_convergence(
            iteration_count=3,
            findings_per_iter=history,
            current_findings=["CRITICAL: still here"],
        )
        assert result == FixedPointResult.NOT_REACHED
