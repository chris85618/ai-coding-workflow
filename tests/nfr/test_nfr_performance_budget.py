"""NFR-013: Performance budgets for hot domain algorithms (left-shifted).

Budgets are deliberately generous (10x expected) so the suite stays
deterministic on slow CI machines while still catching complexity regressions
(e.g. an accidental O(n^2) in a loop that must stay O(n)).
"""

import time

from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector
from agentic_workflow.domain.enums import DebtSource, Severity
from agentic_workflow.domain.services.debt_accumulator import DebtAccumulator
from agentic_workflow.domain.services.governance_cost_model import GovernanceCostModel

PERF_BUDGET_SECONDS = 1.0


class TestPerformanceBudget:
    """Covers latency budgets for pure domain hot paths."""

    def _elapsed(self, start: float) -> float:
        """Return seconds elapsed since start."""
        return time.perf_counter() - start

    def test_convergence_check_on_large_history(self) -> None:
        """TC-NFR-001: 10k-iteration findings history converges within budget."""
        budget = PERF_BUDGET_SECONDS
        history = [[f"HIGH: issue {i}"] * 3 for i in range(10_000)]
        start = time.perf_counter()
        ConvergenceDetector.check_convergence(
            iteration_count=1, findings_per_iter=history, current_findings=["HIGH: x"]
        )
        assert self._elapsed(start) < budget

    def test_debt_absorption_of_bulk_failures(self) -> None:
        """TC-NFR-002: Absorbing 10k failure descriptions stays within budget."""
        budget = PERF_BUDGET_SECONDS
        descriptions = [f"failure {i}" for i in range(10_000)]
        start = time.perf_counter()
        items = DebtAccumulator.absorb(DebtSource.QUALITY_GATE, Severity.HIGH, descriptions, start_index=1)
        assert self._elapsed(start) < budget
        assert len(items) == 10_000

    def test_governance_cost_is_constant_time(self) -> None:
        """TC-NFR-003: 10k kappa evaluations (incl. contract checks) stay within budget."""
        budget = PERF_BUDGET_SECONDS
        start = time.perf_counter()
        for i in range(10_000):
            GovernanceCostModel.should_trigger_hitl(i % 20, i % 40, diverging=False)
        assert self._elapsed(start) < budget
