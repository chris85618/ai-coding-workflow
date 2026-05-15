"""SonarCloud Quality Gate Algorithm.

Traceable to: FR-015
Replaces: skills/workflow-skills/sonarcloud-gate.md
"""

from typing import Any


class SonarCloudGate:
    """Evaluates SonarCloud quality metrics against defined thresholds."""

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
    def evaluate(cls, metrics: dict[str, dict[str, Any]]) -> dict[str, Any]:
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
        return {
            "passed": passed,
            "failures": failures,
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
        elif isinstance(expected, str) and actual > expected:
            # Lexicographical comparison for ratings (e.g., 'B' > 'A')
            return f"{metric} ({scope}) failed: {actual} != {expected}"
        return None

    @classmethod
    def extract_tech_debt(cls, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Converts TODO/FIXME comments or remaining smells into DEBT items."""
        debts = []
        for idx, issue in enumerate(issues):
            if issue.get("type") in ["TODO", "FIXME", "CODE_SMELL"]:
                debts.append(
                    {
                        "id": f"DEBT-SONAR-{idx}",
                        "title": issue.get("message", "SonarCloud Issue"),
                        "priority": "P2"
                        if issue.get("severity") in ["MAJOR", "CRITICAL"]
                        else "P3",
                        "source": "程式碼品質",
                    }
                )
        return debts
