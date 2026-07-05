"""Micro Validation Loop Algorithm.

Traceable to: FR-005
Replaces: skills/workflow-skills/micro-validation.md
"""

from typing import Any

import deal

from agentic_workflow.domain.algorithms.traceability_validator import (
    TraceabilityValidator,
)


class MicroValidation:
    """Executes the micro-validation loop for any CREATE/MODIFY/FIX action."""

    @classmethod
    @deal.has()
    @deal.post(lambda result: isinstance(result, bool))
    def validate_format(cls, content: str) -> bool:
        """Step 0: Format validation."""
        return "from vibe" not in content

    @classmethod
    @deal.has()
    @deal.post(lambda result: isinstance(result, bool))
    def validate_structure(cls, changed_ids: list[str]) -> bool:
        """Step 1: Structural integrity."""
        # Check if IDs match prefix pattern (delegated to TraceabilityValidator)
        if not changed_ids:
            return True
        return all(TraceabilityValidator.validate_id_format(node_id) for node_id in changed_ids)

    @classmethod
    @deal.ensure(
        lambda _: _.result["passed"] == (len(_.result["failures"]) == 0),
        message="Suite pass flag must equal the absence of failures",
    )
    def run_all(cls, changed_content: str, changed_ids: list[str]) -> dict[str, Any]:
        """Runs the complete micro-validation suite."""
        failures = []

        if not cls.validate_format(changed_content):
            failures.append("FORMAT_ERROR: Invalid format or foreign residue found.")

        if not cls.validate_structure(changed_ids):
            failures.append("STRUCTURAL_ERROR: ID format mismatch.")

        passed = len(failures) == 0

        return {
            "passed": passed,
            "failures": failures,
            "next_actions": [
                "Trigger impact-analysis-exec.py" if passed else "rework",
                "Trigger root-cause-leftshift.py",
            ],
            "prompt_for_agent": "Fix the micro-validation failures: " + ", ".join(failures) if not passed else None,
        }
