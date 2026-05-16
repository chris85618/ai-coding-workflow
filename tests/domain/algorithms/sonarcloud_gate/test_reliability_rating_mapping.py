"""Test SonarCloudGate reliability rating mapping logic."""

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


class TestReliabilityRatingMapping:
    """Test SonarCloudGate reliability rating mapping logic."""

    def test_reliability_rating_worse_fails(self) -> None:
        """String comparison: actual > expected (e.g., 'B' > 'A')."""
        metrics = _passing_metrics()
        metrics["reliability_rating"] = {"global": "B", "new": "A"}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False
        assert any("reliability_rating" in f for f in result["failures"])

    def test_reliability_rating_passing(self) -> None:
        """String comparison: actual <= expected (e.g., 'A' <= 'A')."""
        metrics = _passing_metrics()
        metrics["reliability_rating"] = {"global": "A", "new": "A"}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is True

    def test_reliability_rating_numeric_passing(self) -> None:
        """Numeric path: actual=1.0 (API format) maps to 'A', passes."""
        metrics = _passing_metrics()
        metrics["reliability_rating"] = {"global": 1.0, "new": 1.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is True

    def test_reliability_rating_numeric_fails(self) -> None:
        """Numeric path: actual=2.0 maps to 'B', fails against threshold 'A'."""
        metrics = _passing_metrics()
        metrics["reliability_rating"] = {"global": 2.0, "new": 1.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False
        assert any("reliability_rating" in f for f in result["failures"])

    def test_reliability_rating_numeric_unknown_maps_f(self) -> None:
        """Numeric path: unrecognised value maps to 'F', fails against 'A'."""
        metrics = _passing_metrics()
        metrics["reliability_rating"] = {"global": 9.0, "new": 1.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False

    def test_non_numeric_non_string_expected_value_skipped(self) -> None:
        """Branch 55\u219240: expected_val is neither float/int nor str."""
        original = SonarCloudGate.THRESHOLDS.copy()
        SonarCloudGate.THRESHOLDS = {
            "coverage": {"global": [80, 85]},  # list \u2014 neither float/int nor str
        }
        try:
            result = SonarCloudGate.evaluate({"coverage": {"global": [80, 85]}})
            assert result["passed"] is True
        finally:
            SonarCloudGate.THRESHOLDS = original
