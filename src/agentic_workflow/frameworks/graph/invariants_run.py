"""Frameworks Layer — Invariants Run Script.

Executes DAGInvariantVerifier on the compiled master graph.
"""

from __future__ import annotations

import sys
from typing import Any

from agentic_workflow.application.use_cases.verify_invariants import VerifyDAGInvariantsUseCase
from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier
from agentic_workflow.frameworks.graph.master_graph_builder import MasterGraphBuilder


def run_verification() -> dict[str, Any]:
    """Builds the graph and runs formal verification."""
    graph = MasterGraphBuilder.build()
    verifier = DAGInvariantVerifier()
    use_case = VerifyDAGInvariantsUseCase(verifier)
    result = use_case.execute(graph)
    if result["passed"]:
        print("Stage 6 Formal Verification PASSED: All DAG invariants upheld.")
    else:
        print(f"Stage 6 Formal Verification FAILED: {result['failures']}")
    return result


if __name__ == "__main__":  # pragma: no cover
    res = run_verification()
    if not res["passed"]:
        sys.exit(1)
