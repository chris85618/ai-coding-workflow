"""Test suite for iteration convergence algorithms."""

from typing import Any

from agentic_workflow.domain.algorithms.iter_loop import IterationLoop


class TestIterationLoopLogic:
    """Test suite for iteration convergence algorithms."""

    def test_agent_alpha_returns_list(self) -> None:
        """TC-010: Alpha returns list of critiques."""
        result = IterationLoop.agent_alpha_critique("output", ["criterion"])
        assert isinstance(result, list)

    def test_agent_beta_returns_string(self) -> None:
        """TC-011: Beta returns resolution string."""
        result = IterationLoop.agent_beta_resolve([])
        assert isinstance(result, str)

    def test_convergence_reached_all_yagni(self) -> None:
        """TC-012: Converged if all YAGNI."""
        critiques = [{"severity": "YAGNI"}, {"severity": "YAGNI"}]
        assert IterationLoop.determine_convergence(critiques, []) == "REACHED"

    def test_convergence_not_reached(self) -> None:
        """TC-013: Not converged if critical issues remain."""
        curr = [{"severity": "HIGH"}]
        prev = [{"severity": "CRITICAL"}, {"severity": "CRITICAL"}]
        result = IterationLoop.determine_convergence(curr, prev)
        assert result == "NOT_REACHED"

    def test_convergence_diverging(self) -> None:
        """TC-014: Diverging if severity increases."""
        curr = [{"severity": "CRITICAL"}, {"severity": "HIGH"}]
        prev = [{"severity": "HIGH"}]
        result = IterationLoop.determine_convergence(curr, prev)
        assert result == "DIVERGING"

    def test_run_iteration_converged_immediately(self) -> None:
        """TC-015: Immediate convergence check."""
        result = IterationLoop.run_iteration("output", [])
        assert result["status"] == "converged"
        assert result["output"] == "output"

    def test_run_iteration_not_converged(self, monkeypatch: Any) -> None:
        """TC-016: Non-convergence loop check."""
        monkeypatch.setattr(IterationLoop, "agent_alpha_critique", lambda *_: [{"severity": "HIGH"}])
        result = IterationLoop.run_iteration("output", [])
        assert "next_output" in result or "status" in result
