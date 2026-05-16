"""Test suite for three-layer security auditing."""

from agentic_workflow.domain.algorithms.security_audit import (
    SecurityAuditResult,
    ThreeLayerSecurityAudit,
)


class TestSecurityAuditLogic:
    """Test suite for three-layer security auditing."""

    def test_layer1_passes(self) -> None:
        """TC-017: Layer 1 audit pass."""
        r = ThreeLayerSecurityAudit.run_layer1_app_security()
        assert r.passed is True
        assert r.layer == "1_app_security"

    def test_layer2_passes(self) -> None:
        """TC-018: Layer 2 audit pass."""
        r = ThreeLayerSecurityAudit.run_layer2_agent_security()
        assert r.passed is True

    def test_layer3_passes(self) -> None:
        """TC-019: Layer 3 audit pass."""
        r = ThreeLayerSecurityAudit.run_layer3_supply_chain()
        assert r.passed is True

    def test_evaluate_all_pass(self) -> None:
        """TC-020: Full audit evaluation pass."""
        results = [
            ThreeLayerSecurityAudit.run_layer1_app_security(),
            ThreeLayerSecurityAudit.run_layer2_agent_security(),
            ThreeLayerSecurityAudit.run_layer3_supply_chain(),
        ]
        ev = ThreeLayerSecurityAudit.evaluate_audit(results)
        assert ev["passed"] is True
        assert ev["decision"] == "pass"

    def test_evaluate_with_high_finding_reworks(self) -> None:
        """TC-021: HIGH finding requires rework."""
        results = [
            SecurityAuditResult(
                layer="1",
                passed=False,
                findings=[{"severity": "HIGH", "message": "SQL injection"}],
            ),
        ]
        ev = ThreeLayerSecurityAudit.evaluate_audit(results)
        assert ev["decision"] == "rework"
        assert ev["passed"] is False

    def test_evaluate_with_critical_finding_blocks(self) -> None:
        """TC-022: CRITICAL finding blocks escalation."""
        results = [
            SecurityAuditResult(
                layer="1",
                passed=False,
                findings=[{"severity": "CRITICAL", "message": "RCE"}],
            ),
        ]
        ev = ThreeLayerSecurityAudit.evaluate_audit(results)
        assert ev["decision"] == "block_escalate"

    def test_generate_risk_debt_entries(self) -> None:
        """TC-023: Generate risk/debt from findings."""
        findings = [
            {"severity": "CRITICAL", "message": "XSS"},
            {"severity": "HIGH", "message": "CSRF"},
        ]
        out = ThreeLayerSecurityAudit.generate_risk_debt_entries(findings)
        assert len(out["risks"]) == 2
        assert out["risks"][0]["id"] == "RISK-SEC-0"
        assert out["debts"][0]["priority"] == "P0"
        assert out["debts"][1]["priority"] == "P1"

    def test_generate_empty_findings(self) -> None:
        """TC-024: Empty findings handling."""
        out = ThreeLayerSecurityAudit.generate_risk_debt_entries([])
        assert out == {"risks": [], "debts": []}

    def test_evaluate_low_severity_finding_not_collected(self) -> None:
        """TC-025: Low severity not collected."""
        results = [
            SecurityAuditResult(
                layer="1",
                passed=False,
                findings=[{"severity": "LOW", "message": "minor"}],
            ),
        ]
        ev = ThreeLayerSecurityAudit.evaluate_audit(results)
        assert ev["decision"] == "rework"
        assert ev["findings"] == []
