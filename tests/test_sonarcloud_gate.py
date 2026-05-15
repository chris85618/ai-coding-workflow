"""Tests for SonarCloudGate — 100% statement + branch coverage.
Consolidated from: test_governance_algorithms.py, test_quality_gate.py
Traceable to: FR-015, ALG
"""
import pytest
from agentic_workflow.domain.algorithms.sonarcloud_gate import SonarCloudGate


# ── Helpers ────────────────────────────────────────────────────────────────────
def _passing_metrics():
    return {
        "coverage": {"global": 90.0, "new": 90.0},
        "duplication": {"global": 2.0, "new": 1.0},
        "cyclomatic_complexity": {"global": 10, "new": 10},
        "cognitive_complexity": {"global": 10, "new": 10},
        "security_vulnerabilities": {"global": 0, "new": 0},
        "blocker_critical_smells": {"global": 0, "new": 0},
        "major_smells": {"global": 5, "new": 2},
        "tech_debt_ratio": {"global": 3.0, "new": 2.0},
        "reliability_rating": {"global": "A", "new": "A"},
    }


# ── evaluate ──────────────────────────────────────────────────────────────────
class TestEvaluate:
    def test_all_passing_returns_passed_true(self):
        result = SonarCloudGate.evaluate(_passing_metrics())
        assert result["passed"] is True
        assert result["failures"] == []

    def test_metric_not_in_metrics_is_skipped(self):
        """Branch: metric not in metrics → continue."""
        result = SonarCloudGate.evaluate({})
        assert result["passed"] is True

    def test_scope_not_in_actual_data_skipped(self):
        """Branch: scope not in actual_data → continue."""
        result = SonarCloudGate.evaluate({"coverage": {"global": 90.0}})
        # "new" scope missing → skipped, global passes
        assert result["passed"] is True

    def test_coverage_below_threshold_fails(self):
        """Coverage: actual < expected → failure."""
        metrics = _passing_metrics()
        metrics["coverage"] = {"global": 70.0, "new": 90.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False
        assert any("coverage" in f for f in result["failures"])

    def test_duplication_above_threshold_fails(self):
        """Non-coverage metric: actual > expected → failure."""
        metrics = _passing_metrics()
        metrics["duplication"] = {"global": 10.0, "new": 1.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False
        assert any("duplication" in f for f in result["failures"])

    def test_reliability_rating_worse_fails(self):
        """String comparison: actual > expected (e.g., 'B' > 'A')."""
        metrics = _passing_metrics()
        metrics["reliability_rating"] = {"global": "B", "new": "A"}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False
        assert any("reliability_rating" in f for f in result["failures"])

    def test_reliability_rating_passing(self):
        """String comparison: actual <= expected (e.g., 'A' <= 'A')."""
        metrics = _passing_metrics()
        metrics["reliability_rating"] = {"global": "A", "new": "A"}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is True

    def test_non_numeric_non_string_expected_value_skipped(self):
        """Branch 55→40: expected_val is neither float/int nor str → neither branch taken.
        The inner if/elif both skip, no failure appended.
        """
        metrics = {"coverage": {"global": 90.0}}
        # Override THRESHOLDS temporarily with a non-numeric non-string value
        original = SonarCloudGate.THRESHOLDS.copy()
        SonarCloudGate.THRESHOLDS = {
            "coverage": {"global": [80, 85]}  # list — neither float/int nor str
        }
        try:
            result = SonarCloudGate.evaluate({"coverage": {"global": [80, 85]}})
            # Neither branch taken → no failure
            assert result["passed"] is True
        finally:
            SonarCloudGate.THRESHOLDS = original

    def test_passed_next_action_is_continue(self):
        result = SonarCloudGate.evaluate(_passing_metrics())
        assert result["next_action"] == "continue"

    def test_failed_next_action_is_autonomous_fix(self):
        metrics = _passing_metrics()
        metrics["coverage"] = {"global": 50.0, "new": 50.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["next_action"] == "trigger_autonomous_fix"

    def test_passed_prompt_is_none(self):
        result = SonarCloudGate.evaluate(_passing_metrics())
        assert result["prompt_for_agent"] is None

    def test_failed_prompt_contains_fix(self):
        metrics = _passing_metrics()
        metrics["coverage"] = {"global": 50.0, "new": 50.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["prompt_for_agent"] is not None


# ── extract_tech_debt ──────────────────────────────────────────────────────────
class TestExtractTechDebt:
    def test_todo_issue_creates_debt(self):
        issues = [{"type": "TODO", "message": "Fix this", "severity": "MAJOR"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert len(debts) == 1
        assert "DEBT-SONAR-0" in debts[0]["id"]
        assert debts[0]["priority"] == "P2"

    def test_fixme_issue_creates_debt(self):
        issues = [{"type": "FIXME", "message": "Refactor", "severity": "MINOR"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert len(debts) == 1
        assert debts[0]["priority"] == "P3"

    def test_code_smell_creates_debt(self):
        issues = [{"type": "CODE_SMELL", "message": "Smell", "severity": "CRITICAL"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert len(debts) == 1
        assert debts[0]["priority"] == "P2"

    def test_non_matching_type_skipped(self):
        issues = [{"type": "BUG", "message": "Not a debt type"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert debts == []

    def test_empty_issues(self):
        assert SonarCloudGate.extract_tech_debt([]) == []

    def test_multiple_issues_indexed(self):
        issues = [
            {"type": "TODO", "message": "First", "severity": "MAJOR"},
            {"type": "FIXME", "message": "Second", "severity": "MINOR"},
        ]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert len(debts) == 2
        assert debts[0]["id"] == "DEBT-SONAR-0"
        assert debts[1]["id"] == "DEBT-SONAR-1"

    def test_missing_severity_defaults_p3(self):
        issues = [{"type": "TODO", "message": "No severity"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert debts[0]["priority"] == "P3"

    def test_missing_message_defaults_sonarcloud_issue(self):
        issues = [{"type": "TODO"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert "SonarCloud Issue" in debts[0]["title"]
