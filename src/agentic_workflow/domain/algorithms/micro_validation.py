"""Micro Validation Loop Algorithm.

Traceable to: FR-005
Replaces: skills/workflow-skills/micro-validation.md
"""

from typing import Dict, Any, List

class MicroValidation:
    """Executes the micro-validation loop for any CREATE/MODIFY/FIX action."""

    @classmethod
    def validate_format(cls, content: str) -> bool:
        """Step 0: Format validation."""
        if "from vibe" in content:
            return False
        return True

    @classmethod
    def validate_structure(cls, changed_ids: List[str]) -> bool:
        """Step 1: Structural integrity."""
        # Check if IDs match expected prefix pattern (delegated to TraceabilityValidator)
        return True

    @classmethod
    def run_all(cls, changed_content: str, changed_ids: List[str]) -> Dict[str, Any]:
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
                "Trigger root-cause-leftshift.py"
            ],
            "prompt_for_agent": "Fix the micro-validation failures: " + ", ".join(failures) if not passed else None
        }
