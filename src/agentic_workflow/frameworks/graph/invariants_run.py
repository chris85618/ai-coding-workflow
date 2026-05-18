"""Frameworks Layer — Invariants Run Script.

Executes DAGInvariantVerifier on the compiled master graph.
"""

from __future__ import annotations

import sys
from typing import Any

from agentic_workflow.application.use_cases.verify_invariants import VerifyDAGInvariantsUseCase
from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier
from agentic_workflow.frameworks.graph.master_graph_builder import MasterGraphBuilder


def _print_verif_result(result: dict[str, Any]) -> None:
    passed_msg = "Stage 6 Formal Verification PASSED: All DAG invariants upheld."
    failed_msg = f"Stage 6 Formal Verification FAILED: {result.get('failures')}"
    msg = passed_msg if result["passed"] else failed_msg
    print(msg)


def run_verification() -> dict[str, Any]:
    """Builds the graph and runs formal verification."""
    use_case = VerifyDAGInvariantsUseCase(DAGInvariantVerifier())
    result = use_case.execute(MasterGraphBuilder.build())
    _print_verif_result(result)
    return result


if __name__ == "__main__":  # pragma: no cover
    res = run_verification()
    if not res["passed"]:
        sys.exit(1)
