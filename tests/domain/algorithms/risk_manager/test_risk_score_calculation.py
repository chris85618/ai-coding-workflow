"""Tests for RiskManager score calculation."""

from agentic_workflow.domain.algorithms.risk_manager import RiskManager


class TestRiskScoreCalculation:
    """Tests for ALG-005 RiskManager score logic."""

    def test_score_low(self) -> None:
        """TC-227: Low risk score."""
        r = RiskManager.calculate_risk_score(1, 2)
        assert r["score"] == 2
        assert r["severity"] == "LOW"

    def test_score_medium(self) -> None:
        """TC-228: Medium risk score."""
        r = RiskManager.calculate_risk_score(3, 3)
        assert r["score"] == 9
        assert r["severity"] == "MEDIUM"

    def test_score_high(self) -> None:
        """TC-229: High risk score."""
        # 3*4=12 → HIGH (score 12: 10 < 12 <= 14)
        r = RiskManager.calculate_risk_score(3, 4)
        assert r["score"] == 12
        assert r["severity"] == "HIGH"

    def test_score_critical(self) -> None:
        """TC-230: Critical risk score."""
        r = RiskManager.calculate_risk_score(5, 5)
        assert r["score"] == 25
        assert r["severity"] == "CRITICAL"

    def test_score_boundary_low_medium(self) -> None:
        """TC-231: Low/Medium boundary."""
        r = RiskManager.calculate_risk_score(2, 2)
        assert r["severity"] == "LOW"  # 4 → LOW

    def test_score_boundary_medium(self) -> None:
        """TC-232: Medium boundary check."""
        r = RiskManager.calculate_risk_score(3, 2)
        assert r["score"] == 6
        assert r["severity"] == "MEDIUM"
