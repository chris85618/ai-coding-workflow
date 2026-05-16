"""Tests for RiskManager treatment evaluation."""

from agentic_workflow.domain.algorithms.risk_manager import RiskManager


class TestRiskTreatmentEvaluation:
    """Tests for ALG-005 RiskManager treatment logic."""

    def test_treatment_critical(self) -> None:
        """TC-233: Critical risk treatment."""
        t = RiskManager.evaluate_treatment("CRITICAL")
        assert t["requires_hitl"] is True
        assert "Immediate" in t["priority"]

    def test_treatment_high(self) -> None:
        """TC-234: High risk treatment."""
        t = RiskManager.evaluate_treatment("HIGH")
        assert t["requires_hitl"] is True

    def test_treatment_medium(self) -> None:
        """TC-235: Medium risk treatment."""
        t = RiskManager.evaluate_treatment("MEDIUM")
        assert t["requires_hitl"] is False

    def test_treatment_low(self) -> None:
        """TC-236: Low risk treatment."""
        t = RiskManager.evaluate_treatment("LOW")
        assert t["requires_hitl"] is False

    def test_treatment_unknown_defaults_to_low(self) -> None:
        """TC-237: Unknown risk defaults to low."""
        t = RiskManager.evaluate_treatment("UNKNOWN")
        assert t["requires_hitl"] is False
