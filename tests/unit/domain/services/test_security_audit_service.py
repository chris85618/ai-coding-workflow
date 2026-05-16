"""Unit tests for SecurityAuditService."""

from unittest.mock import MagicMock

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.services.security_audit_service import SecurityAuditService
from agentic_workflow.domain.value_objects.findings import Findings


class TestSecurityAuditService:
    """Covers SecurityAuditService logic and branches."""

    def test_audit_pipeline_collects_findings(self) -> None:
        """Collects findings from multiple layers."""
        pipeline = MagicMock(spec=Pipeline)
        layer_results = [
            {
                "layer": "app",
                "findings": [
                    {"severity": "HIGH", "message": "SQL injection"},
                    {"severity": "MEDIUM", "message": "XSS"},
                ],
            }
        ]
        findings = SecurityAuditService.audit_pipeline(pipeline, layer_results)
        assert len(findings) == 2
        assert "[app] HIGH: SQL injection" in findings

    def test_decide_gate_impact_block(self) -> None:
        """Blocks on CRITICAL findings."""
        findings = Findings(items=["[layer] CRITICAL: Exploit found"])
        decision = SecurityAuditService.decide_gate_impact(findings)
        assert decision == "block"

    def test_decide_gate_impact_rework(self) -> None:
        """Rework on HIGH findings."""
        findings = Findings(items=["[layer] HIGH: Risk detected"])
        decision = SecurityAuditService.decide_gate_impact(findings)
        assert decision == "rework"

    def test_decide_gate_impact_pass(self) -> None:
        """Passes on MEDIUM or below."""
        findings = Findings(items=["[layer] MEDIUM: Minor issue"])
        decision = SecurityAuditService.decide_gate_impact(findings)
        assert decision == "pass"
