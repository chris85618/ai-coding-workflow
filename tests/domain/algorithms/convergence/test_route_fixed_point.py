"""Tests for ConvergenceDetector.route_fixed_point (ADR-STR-029 Pipeline v2 routing)."""

from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector
from agentic_workflow.domain.enums import FixedPointResult


class TestRouteFixedPoint:
    """Covers the closed three-way loop routing decision set."""

    def test_not_reached_routes_to_beta(self) -> None:
        """TC-V2-034: NOT_REACHED continues the dual-agent loop."""
        assert ConvergenceDetector.route_fixed_point(FixedPointResult.NOT_REACHED) == "beta"

    def test_diverging_routes_to_rollback(self) -> None:
        """TC-V2-035: DIVERGING enters the degradation path."""
        assert ConvergenceDetector.route_fixed_point(FixedPointResult.DIVERGING) == "rollback"

    def test_reached_routes_to_exit_loop(self) -> None:
        """TC-V2-036: REACHED exits toward the alignment check."""
        assert ConvergenceDetector.route_fixed_point(FixedPointResult.REACHED) == "exit_loop"

    def test_max_iterations_routes_to_exit_loop(self) -> None:
        """TC-V2-037: MAX_ITERATIONS exits toward the alignment check."""
        assert ConvergenceDetector.route_fixed_point(FixedPointResult.MAX_ITERATIONS) == "exit_loop"
