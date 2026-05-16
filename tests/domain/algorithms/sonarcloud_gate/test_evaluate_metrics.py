"""Test SonarCloudGate.evaluate logic for metric thresholds."""

from agentic_workflow.domain.algorithms.sonarcloud_gate import SonarCloudGate


def _passing_metrics() -> dict[str, dict[str, float | str]]:
    """Helper to create passing metrics."""
    return {
        "coverage": {"global": 90.0, "new": 90.0},
        "duplication": {"global": 2.0, "new": 1.0},
        "cyclomatic_complexity": {"global": 10.0, "new": 10.0},
        "cognitive_complexity": {"global": 10.0, "new": 10.0},
        "security_vulnerabilities": {"global": 0.0, "new": 0.0},
        "blocker_critical_smells": {"global": 0.0, "new": 0.0},
        "major_smells": {"global": 5.0, "new": 2.0},
        "tech_debt_ratio": {"global": 3.0, "new": 2.0},
        "reliability_rating": {"global": "A", "new": "A"},
    }


class TestEvaluateMetrics:
    """Test SonarCloudGate.evaluate logic for metric thresholds."""

    def test_all_passing_returns_passed_true(self) -> None:
        """Verify passing metrics result in PASS."""
        result = SonarCloudGate.evaluate(_passing_metrics())
        assert result["passed"] is True
        assert result["failures"] == []

    def test_metric_not_in_metrics_is_skipped(self) -> None:
        """Branch: metric not in metrics → continue."""
        result = SonarCloudGate.evaluate({})
        assert result["passed"] is True

    def test_scope_not_in_actual_data_skipped(self) -> None:
        """Branch: scope not in actual_data → continue."""
        result = SonarCloudGate.evaluate({"coverage": {"global": 90.0}})
        assert result["passed"] is True

    def test_coverage_below_threshold_fails(self) -> None:
        """Coverage: actual < expected → failure."""
        metrics = _passing_metrics()
        metrics["coverage"] = {"global": 70.0, "new": 90.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False
        assert any("coverage" in f for f in result["failures"])

    def test_duplication_above_threshold_fails(self) -> None:
        """Non-coverage metric: actual > expected → failure."""
        metrics = _passing_metrics()
        metrics["duplication"] = {"global": 10.0, "new": 1.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False
        assert any("duplication" in f for f in result["failures"])

    def test_passed_next_action_is_continue(self) -> None:
        """Verify next action for PASSED."""
        result = SonarCloudGate.evaluate(_passing_metrics())
        assert result["next_action"] == "continue"

    def test_failed_next_action_is_autonomous_fix(self) -> None:
        """Verify next action for FAILED."""
        metrics = _passing_metrics()
        metrics["coverage"] = {"global": 50.0, "new": 50.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["next_action"] == "trigger_autonomous_fix"

    def test_passed_prompt_is_none(self) -> None:
        """Verify prompt is None for PASSED."""
        result = SonarCloudGate.evaluate(_passing_metrics())
        assert result["prompt_for_agent"] is None

    def test_failed_prompt_contains_fix(self) -> None:
        """Verify prompt for FAILED."""
        metrics = _passing_metrics()
        metrics["coverage"] = {"global": 50.0, "new": 50.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["prompt_for_agent"] is not None
