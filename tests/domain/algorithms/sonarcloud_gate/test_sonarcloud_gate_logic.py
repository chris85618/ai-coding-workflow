"""Test suite for SonarCloud quality gates."""

from typing import Any

from agentic_workflow.domain.algorithms.sonarcloud_gate import SonarCloudGate


class TestSonarCloudGateLogic:
    """Test suite for SonarCloud quality gates."""

    def _good_metrics(self) -> dict[str, Any]:
        """Helper: returns passing metrics."""
        return {
            "coverage": {"global": 82.0, "new": 90.0},
            "duplication": {"global": 2.0, "new": 1.0},
            "cyclomatic_complexity": {"global": 10, "new": 8},
            "cognitive_complexity": {"global": 10, "new": 8},
            "security_vulnerabilities": {"global": 0, "new": 0},
            "blocker_critical_smells": {"global": 0, "new": 0},
            "major_smells": {"global": 5, "new": 2},
            "tech_debt_ratio": {"global": 3.0, "new": 2.0},
            "reliability_rating": {"global": "A", "new": "A"},
        }

    def test_all_pass_returns_passed(self) -> None:
        """TC-026: All passing metrics."""
        result = SonarCloudGate.evaluate(self._good_metrics())
        assert result["passed"] is True
        assert result["next_action"] == "continue"
        assert result["prompt_for_agent"] is None

    def test_low_coverage_fails(self) -> None:
        """TC-027: Low coverage fail."""
        metrics = self._good_metrics()
        metrics["coverage"] = {"global": 70.0, "new": 70.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False
        assert result["next_action"] == "trigger_autonomous_fix"
        assert result["prompt_for_agent"] is not None

    def test_high_duplication_fails(self) -> None:
        """TC-028: High duplication fail."""
        metrics = self._good_metrics()
        metrics["duplication"] = {"global": 10.0, "new": 5.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False

    def test_bad_reliability_rating_fails(self) -> None:
        """TC-029: Bad reliability rating fail."""
        metrics = self._good_metrics()
        metrics["reliability_rating"] = {"global": "B", "new": "A"}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False

    def test_missing_metric_skipped(self) -> None:
        """TC-030: Skip missing metrics."""
        result = SonarCloudGate.evaluate({"coverage": {"global": 85.0, "new": 90.0}})
        assert result["passed"] is True

    def test_extract_tech_debt_todo(self) -> None:
        """TC-031: Extract tech debt from TODOs."""
        issues = [
            {"type": "TODO", "message": "Refactor this", "severity": "MAJOR"},
            {"type": "TODO", "message": "Clean up", "severity": "MINOR"},
        ]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert len(debts) == 2
        assert debts[0]["priority"] == "P2"
        assert debts[1]["priority"] == "P3"

    def test_extract_tech_debt_non_debt_type_ignored(self) -> None:
        """TC-032: Ignore non-debt types."""
        issues = [{"type": "INFO", "message": "not a debt"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert debts == []

    def test_extract_tech_debt_code_smell(self) -> None:
        """TC-033: Extract debt from code smells."""
        issues = [{"type": "CODE_SMELL", "message": "smell", "severity": "CRITICAL"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert debts[0]["priority"] == "P2"

    def test_metric_with_only_global_scope_evaluates_global(self) -> None:
        """TC-034: Evaluate global if no new scope."""
        metrics = {"coverage": {"global": 85.0}}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is True

    def test_metric_with_only_new_scope(self) -> None:
        """TC-035: Evaluate new if no global scope."""
        metrics = {"coverage": {"new": 90.0}}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is True
