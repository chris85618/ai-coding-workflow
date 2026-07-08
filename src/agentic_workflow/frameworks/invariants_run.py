"""Frameworks Layer — Invariants Run Script.

Executes DAGInvariantVerifier on the exported Archon workflow document
(ADR-STR-033: the exported topology is the orchestration authority).
"""

from __future__ import annotations

import sys
from typing import Any

from agentic_workflow.application.use_cases.verify_invariants import VerifyDAGInvariantsUseCase
from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.algorithms.invariants_verifier import DAGInvariantVerifier
from agentic_workflow.frameworks.archon_orchestrator import ArchonOrchestrator


class InvariantsRunner:
    """Runner class to execute DAGInvariantVerifier on the exported workflow topology."""

    @staticmethod
    def print_verif_result(result: dict[str, Any]) -> None:
        """Print the verification result message."""
        passed_msg = "Stage 6 Formal Verification PASSED: All DAG invariants upheld."
        failed_msg = f"Stage 6 Formal Verification FAILED: {result.get('failures')}"
        msg = passed_msg if result["passed"] else failed_msg
        print(msg)

    @classmethod
    def run_verification(cls) -> dict[str, Any]:
        """Exports the workflow document and runs formal verification."""
        use_case = VerifyDAGInvariantsUseCase(DAGInvariantVerifier())
        positions = list(Pipeline(pipeline_id="invariants-check").stages)
        workflow_doc = ArchonOrchestrator().export_workflow("invariants-check", positions)
        result = use_case.execute(workflow_doc)
        cls.print_verif_result(result)
        return result


# Backward compatibility facades
run_verification = InvariantsRunner.run_verification


if __name__ == "__main__":  # pragma: no cover
    res = InvariantsRunner.run_verification()
    if not res["passed"]:
        sys.exit(1)
