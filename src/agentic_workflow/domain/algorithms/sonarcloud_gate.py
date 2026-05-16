"""Domain Algorithm — SonarCloud Quality Gate.

This module implements the SonarCloud quality gate evaluation logic,
parameter verification, and automated technical debt extraction for
the closed-loop feedback system (ADR-OPS-001).
"""

from typing import Any

from agentic_workflow.domain.models.sonarcloud_config import SonarCloudConfig


class SonarCloudGate:
    """Evaluates SonarCloud quality metrics against defined thresholds.

    Traceable to: FR-015, FR-035, FR-036
    """

    THRESHOLDS: dict[str, dict[str, Any]] = {
        "coverage": {"global": 80.0, "new": 85.0},
        "duplication": {"global": 5.0, "new": 3.0},
        "cyclomatic_complexity": {"global": 15, "new": 15},
        "cognitive_complexity": {"global": 15, "new": 15},
        "security_vulnerabilities": {"global": 0, "new": 0},
        "blocker_critical_smells": {"global": 0, "new": 0},
        "major_smells": {"global": 10, "new": 3},
        "tech_debt_ratio": {"global": 5.0, "new": 5.0},
        "reliability_rating": {"global": "A", "new": "A"},
    }

    @classmethod
    def verify_configuration(cls, config: SonarCloudConfig) -> dict[str, Any]:
        """Checks if required configuration parameters are set.

        Returns:
            Dict with 'valid' (bool) and 'missing_vars' (list).
        """
        valid = config.is_valid
        missing = config.missing_vars
        return {
            "valid": valid,
            "missing_vars": missing,
            "status": "active" if valid else "disabled",
        }

    @classmethod
    def evaluate(
        cls,
        metrics: dict[str, dict[str, Any]],
        issues: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Evaluates given metrics against the thresholds.

        metrics format:
        {
            "coverage": {"global": 82.0, "new": 90.0},
            ...
        }
        """
        failures = []
        for metric, threshold_data in cls.THRESHOLDS.items():
            if metric not in metrics:
                continue

            actual_data = metrics[metric]
            for scope in ["global", "new"]:
                if scope not in actual_data:
                    continue

                actual_val = actual_data[scope]
                expected_val = threshold_data.get(scope)

                failure = cls._check_threshold(metric, scope, actual_val, expected_val)
                if failure:
                    failures.append(failure)

        passed = len(failures) == 0
        tech_debts = cls.extract_tech_debt(issues or []) if not passed else []

        return {
            "passed": passed,
            "failures": failures,
            "tech_debts": tech_debts,
            "next_action": "continue" if passed else "trigger_autonomous_fix",
            "prompt_for_agent": "Analyze the SonarCloud failures and apply fixes."
            if not passed
            else None,
        }

    @staticmethod
    def _check_threshold(
        metric: str, scope: str, actual: Any, expected: Any
    ) -> str | None:
        """Checks a single metric value against its threshold."""
        if isinstance(expected, (float, int)):
            if metric == "coverage" and actual < expected:
                return f"{metric} ({scope}) failed: {actual} < {expected}"
            if metric != "coverage" and actual > expected:
                return f"{metric} ({scope}) failed: {actual} > {expected}"
        elif isinstance(expected, str):
            # Support numeric ratings (1.0=A from API) and
            # letter strings ('A' from tests).
            if isinstance(actual, str):
                actual_str = actual
            else:
                rating_map = {1.0: "A", 2.0: "B", 3.0: "C", 4.0: "D", 5.0: "E"}
                actual_str = rating_map.get(float(actual), "F")
            if actual_str > expected:  # Lower is better, but char 'B' > 'A'
                return f"{metric} ({scope}) failed: {actual_str} > {expected}"
        return None

    @classmethod
    def extract_tech_debt(cls, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Converts TODO/FIXME comments or remaining smells into DEBT items."""
        debts = []
        for idx, issue in enumerate(issues):
            issue_type = issue.get("type")
            if issue_type in ["TODO", "FIXME", "CODE_SMELL", "BUG", "VULNERABILITY"]:
                debts.append(
                    {
                        "id": f"DEBT-SONAR-{idx}",
                        "title": issue.get("message", "SonarCloud Issue"),
                        "priority": "P2"
                        if issue.get("severity") in ["MAJOR", "CRITICAL", "BLOCKER"]
                        else "P3",
                        "source": "SonarCloud Quality Gate",
                        "affected_file": issue.get("component", "unknown"),
                    }
                )
        return debts
