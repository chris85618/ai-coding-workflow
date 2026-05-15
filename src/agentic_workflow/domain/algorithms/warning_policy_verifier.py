"""Domain Algorithm — Warning Policy Verifier.

Implements ALG-013: Automated compliance check for ADR-GOV-026.
Ensures logic fixes are prioritized over warning exclusions.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Any


class WarningPolicyVerifier:
    """ALG-013: Hardened Warning Policy Enforcement.

    Scans project configuration and changes to prevent improper warning exclusions.
    """

    @classmethod
    def verify_config(cls, pyproject_path: Path) -> Dict[str, Any]:
        """Verify the current pyproject.toml for warning policy compliance.

        Args:
            pyproject_path: Path to the pyproject.toml file.

        Returns:
            Dict containing 'passed' (bool) and 'violations' (list).
        """
        if not pyproject_path.exists():
            return {"passed": True, "violations": []}

        content = pyproject_path.read_text(encoding="utf-8")
        violations = []

        # Find the filterwarnings list
        # Simple regex for TOML list content - in production we'd use a TOML parser
        fw_match = re.search(r"filterwarnings\s*=\s*\[(.*?)\]", content, re.DOTALL)
        if not fw_match:
            return {"passed": True, "violations": []}

        fw_list_str = fw_match.group(1)
        # Extract individual rules
        rules = [r.strip().strip('"').strip("'") for r in fw_list_str.split(",") if r.strip()]

        for rule in rules:
            # Rule 1: No internal exclusions
            if "agentic_workflow" in rule:
                violations.append(f"Internal code warning exclusion detected: {rule}. Fix the logic instead.")

            # Rule 2: Must be scoped (regex .* at the end for 3rd party)
            # Basic check: if it's an ignore, it must have a colon and a module name with scope
            if rule.startswith("ignore") and ":" in rule:
                _, scope = rule.split(":", 1)
                if not scope.endswith(".*") and not re.search(r"\[.*\]", scope):
                     # If it doesn't look scoped, flag it
                     violations.append(f"Broad or unscoped warning exclusion detected: {rule}. Use regex scope (e.g., 'pkg.*').")

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    @classmethod
    def verify_change_justification(cls, commit_msg: str, violations: List[str]) -> bool:
        """Verify if detected violations are justified in the commit message/ADR.

        Args:
            commit_msg: The commit message or ADR context.
            violations: List of detected violations.

        Returns:
            True if all violations are explicitly justified with "FAILED_REFAC_EVIDENCE".
        """
        # Enforcement: Every exclusion MUST have a justification keyword
        # In this hardening, we mandate the string 'FAILED_REFAC_EVIDENCE'
        return all("FAILED_REFAC_EVIDENCE" in commit_msg for _ in violations)
