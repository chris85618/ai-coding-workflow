"""Cover missing branches in ALG-001 convergence.py."""

from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector
from agentic_workflow.domain.enums import FixedPointResult


class TestConvergenceBranches:
    """Cover missing branches in ALG-001 convergence.py."""

    def test_diverging_result(self) -> None:
        """DIVERGING: finding count increasing over 3 iterations."""
        history = [["A"], ["A", "B"], ["A", "B", "C"]]
        result = ConvergenceDetector.check_convergence(
            iteration_count=3,
            findings_per_iter=history,
            current_findings=["A", "B", "C", "D"],
        )
        assert result == FixedPointResult.DIVERGING

    def test_not_reached_short_history(self) -> None:
        """NOT_REACHED: insufficient history for divergence detection."""
        history = [["A"]]
        result = ConvergenceDetector.check_convergence(
            iteration_count=1,
            findings_per_iter=history,
            current_findings=["CRITICAL: issue"],
        )
        assert result == FixedPointResult.NOT_REACHED

    def test_max_iterations_boundary(self) -> None:
        """MAX_ITERATIONS: iteration_count >= 10."""
        result = ConvergenceDetector.check_convergence(
            iteration_count=10,
            findings_per_iter=[],
            current_findings=["CRITICAL: still here"],
        )
        assert result == FixedPointResult.MAX_ITERATIONS

    def test_should_auto_pass_not_reached(self) -> None:
        """NOT_REACHED should NOT auto-pass."""
        assert ConvergenceDetector.should_auto_pass(FixedPointResult.NOT_REACHED) is False

    def test_diverging_auto_pass(self) -> None:
        """DIVERGING should auto-pass per ADR-STR-003."""
        assert ConvergenceDetector.should_auto_pass(FixedPointResult.DIVERGING) is True

    def test_max_iterations_auto_pass(self) -> None:
        """MAX_ITERATIONS should auto-pass with warning."""
        assert ConvergenceDetector.should_auto_pass(FixedPointResult.MAX_ITERATIONS) is True
