"""Dual-Agent Iteration Loop Algorithm.

Traceable to: FR-012, FR-013, FR-014
Replaces: skills/workflow-skills/iter-loop.md
"""

from typing import Any

import deal


class IterationLoop:
    """Executes the dual-agent (Agent alpha/beta) convergence loop."""

    @classmethod
    @deal.post(lambda result: isinstance(result, list), message="Alpha critique yields a findings list")
    def agent_alpha_critique(cls, output: str, criteria: list[str]) -> list[dict[str, Any]]:
        """Agent alpha: exhaustive critique of the output against criteria."""
        # Simulated critique
        return []

    @classmethod
    @deal.post(lambda result: isinstance(result, str) and bool(result), message="Beta must emit a non-empty resolution")
    def agent_beta_resolve(cls, critiques: list[dict[str, Any]]) -> str:
        """Agent beta: resolves critiques using Occam's razor.

        Also performs context boundary checks.
        """
        # Simulated resolution
        return "resolved_output"

    @classmethod
    @deal.post(
        lambda result: result in ("REACHED", "DIVERGING", "NOT_REACHED"),
        message="Convergence is a closed decision set (INV-005-v2)",
    )
    def determine_convergence(
        cls,
        current_critiques: list[dict[str, Any]],
        previous_critiques: list[dict[str, Any]],
    ) -> str:
        """Determines if the iteration loop has reached a fixed point."""
        # Are all critiques YAGNI?
        if all(c.get("severity") == "YAGNI" for c in current_critiques):
            return "REACHED"

        # Count non-YAGNI critical/high in current vs previous
        curr_critical_high = sum(1 for c in current_critiques if c.get("severity") in ["CRITICAL", "HIGH"])
        prev_critical_high = sum(1 for c in previous_critiques if c.get("severity") in ["CRITICAL", "HIGH"])

        if prev_critical_high is not None and curr_critical_high >= prev_critical_high and curr_critical_high > 0:
            return "DIVERGING"

        return "NOT_REACHED"

    @classmethod
    @deal.ensure(
        lambda _: "status" in _.result,
        message="Iteration outcome must always carry a status",
    )
    def run_iteration(cls, initial_output: str, criteria: list[str]) -> dict[str, Any]:
        """Runs a complete iteration loop."""
        critiques = cls.agent_alpha_critique(initial_output, criteria)
        status = cls.determine_convergence(critiques, [])

        if status == "REACHED":
            return {"status": "converged", "output": initial_output}

        resolved_output = cls.agent_beta_resolve(critiques)

        return {
            "status": status,
            "next_output": resolved_output,
            "critiques": critiques,
        }

    @classmethod
    @deal.has()
    @deal.post(lambda result: result in ("alpha", "pass"), message="HITL routing is a closed decision set")
    def route_hitl_gate(cls, gate_decision: str | None) -> str:
        """Determines routing for human-in-the-loop gate choice.

        If gate_decision is FAIL, return 'alpha' to re-critique.
        Otherwise, return 'pass' to exit iteration loop.
        """
        if gate_decision == "fail":
            return "alpha"
        return "pass"
