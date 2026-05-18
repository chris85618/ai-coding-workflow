"""Frameworks Layer — Invariants Run Script.

Executes DAGInvariantVerifier on the compiled master graph.
"""

from __future__ import annotations

import sys
from typing import Any

from agentic_workflow.application.use_cases.verify_invariants import VerifyDAGInvariantsUseCase
from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier
from agentic_workflow.frameworks.graph.master_graph_builder import MasterGraphBuilder


class InvariantsRunner:
    """Runner class to execute DAGInvariantVerifier on the compiled master graph."""

    @staticmethod
    def print_verif_result(result: dict[str, Any]) -> None:
        """Print the verification result message."""
        passed_msg = "Stage 6 Formal Verification PASSED: All DAG invariants upheld."
        failed_msg = f"Stage 6 Formal Verification FAILED: {result.get('failures')}"
        msg = passed_msg if result["passed"] else failed_msg
        print(msg)

    @classmethod
    def run_verification(cls) -> dict[str, Any]:
        """Builds the graph and runs formal verification."""
        use_case = VerifyDAGInvariantsUseCase(DAGInvariantVerifier())
        result = use_case.execute(MasterGraphBuilder.build())
        cls.print_verif_result(result)
        return result


# Backward compatibility facades
run_verification = InvariantsRunner.run_verification


if __name__ == "__main__":  # pragma: no cover
    res = InvariantsRunner.run_verification()
    if not res["passed"]:
        sys.exit(1)
