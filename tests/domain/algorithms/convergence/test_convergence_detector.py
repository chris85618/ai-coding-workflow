"""ALG-001 OO class interface."""

from agentic_workflow.domain.enums import FixedPointResult


class TestConvergenceDetector:
    """ALG-001 OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector

        self.cls = ConvergenceDetector

    def test_class_constants_exist(self) -> None:
        """TC-166: Convergence constants check."""
        assert self.cls.MAX_ITERATIONS == 10
        assert self.cls.DIVERGENCE_WINDOW == 3

    def test_all_yagni_returns_reached(self) -> None:
        """TC-167: All YAGNI convergence."""
        result = self.cls.check_convergence(0, [], ["YAGNI: ok", "YAGNI: fine"])
        assert result == FixedPointResult.REACHED

    def test_max_iterations_returns_max_iterations(self) -> None:
        """TC-168: Max iterations reached."""
        result = self.cls.check_convergence(10, [], ["issue"])
        assert result == FixedPointResult.MAX_ITERATIONS

    def test_diverging_detection(self) -> None:
        """TC-169: Divergence detection."""
        findings_per_iter = [["a"], ["a", "b"], ["a", "b", "c"]]
        result = self.cls.check_convergence(3, findings_per_iter, ["a", "b", "c", "d"])
        assert result == FixedPointResult.DIVERGING

    def test_not_reached_when_not_all_yagni(self) -> None:
        """TC-170: Convergence not reached."""
        result = self.cls.check_convergence(0, [], ["CRITICAL: issue"])
        assert result == FixedPointResult.NOT_REACHED

    def test_should_auto_pass_reached(self) -> None:
        """TC-171: Auto-pass on REACHED."""
        assert self.cls.should_auto_pass(FixedPointResult.REACHED) is True

    def test_should_auto_pass_diverging(self) -> None:
        """TC-172: Auto-pass on DIVERGING."""
        assert self.cls.should_auto_pass(FixedPointResult.DIVERGING) is True

    def test_should_auto_pass_max_iterations(self) -> None:
        """TC-173: Auto-pass on MAX_ITERATIONS."""
        assert self.cls.should_auto_pass(FixedPointResult.MAX_ITERATIONS) is True

    def test_should_not_pass_not_reached(self) -> None:
        """TC-174: No auto-pass on NOT_REACHED."""
        assert self.cls.should_auto_pass(FixedPointResult.NOT_REACHED) is False
