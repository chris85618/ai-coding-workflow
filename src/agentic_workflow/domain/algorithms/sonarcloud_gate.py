"""SonarCloud Quality Gate Algorithm.

Traceable to: FR-015
Replaces: skills/workflow-skills/sonarcloud-gate.md
"""

from typing import Dict, Any

class SonarCloudGate:
    """Evaluates SonarCloud quality metrics against defined thresholds."""
    
    THRESHOLDS = {
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
    def evaluate(cls, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
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
                expected_val = threshold_data[scope]
                
                # Check based on type
                if isinstance(expected_val, float) or isinstance(expected_val, int):
                    if metric == "coverage":
                        if actual_val < expected_val:
                            failures.append(f"{metric} ({scope}) failed: {actual_val} < {expected_val}")
                    else:
                        if actual_val > expected_val:
                            failures.append(f"{metric} ({scope}) failed: {actual_val} > {expected_val}")
                elif isinstance(expected_val, str):
                    if actual_val > expected_val:  # 'B' > 'A'
                        failures.append(f"{metric} ({scope}) failed: {actual_val} != {expected_val}")
                        
        passed = len(failures) == 0
        return {
            "passed": passed,
            "failures": failures,
            "next_action": "continue" if passed else "trigger_autonomous_fix",
            "prompt_for_agent": "Analyze the SonarCloud failures and apply fixes." if not passed else None
        }

    @classmethod
    def extract_tech_debt(cls, issues: list) -> list:
        """Converts TODO/FIXME comments or remaining smells into DEBT items."""
        debts = []
        for idx, issue in enumerate(issues):
            if issue.get("type") in ["TODO", "FIXME", "CODE_SMELL"]:
                debts.append({
                    "id": f"DEBT-SONAR-{idx}",
                    "title": issue.get("message", "SonarCloud Issue"),
                    "priority": "P2" if issue.get("severity") in ["MAJOR", "CRITICAL"] else "P3",
                    "source": "程式碼品質"
                })
        return debts
