"""Three-Layer Security Audit — ThreeLayerSecurityAudit class.

Traceable to: FR-016
Replaces: skills/workflow-skills/security-audit-3layer.md
"""

from typing import Any

from agentic_workflow.domain.algorithms.security_audit.security_audit_result import (
    SecurityAuditResult,
)


class ThreeLayerSecurityAudit:
    """Orchestrates the 3-layer security audit process."""

    @classmethod
    def run_layer1_app_security(cls) -> SecurityAuditResult:
        """Layer 1: App Security (OWASP Top 10, STRIDE).

        In the DAG, this should yield to an LLM agent prompt.
        """
        return SecurityAuditResult(
            layer="1_app_security",
            passed=True,
            findings=[],
        )

    @classmethod
    def run_layer2_agent_security(cls) -> SecurityAuditResult:
        """Layer 2: Agent Security (AgentShield).

        In the DAG, this executes `npx ecc-agentshield scan --opus --stream`.
        """
        # Mocked execution
        return SecurityAuditResult(
            layer="2_agent_security",
            passed=True,
            findings=[],
        )

    @classmethod
    def run_layer3_supply_chain(cls) -> SecurityAuditResult:
        """Layer 3: Supply Chain Security (SkillFortify).

        In the DAG, this executes `skillfortify scan . --format json`.
        """
        # Mocked execution
        return SecurityAuditResult(
            layer="3_supply_chain",
            passed=True,
            findings=[],
        )

    @classmethod
    def evaluate_audit(cls, results: list[SecurityAuditResult]) -> dict[str, Any]:
        """Evaluates results from all 3 layers."""
        all_passed = all(r.passed for r in results)
        high_critical_findings = []
        for r in results:
            for f in r.findings:
                if f.get("severity") in ["HIGH", "CRITICAL"]:
                    high_critical_findings.append(f)

        has_critical = any(f.get("severity") == "CRITICAL" for f in high_critical_findings)

        decision = "pass"
        if has_critical:
            decision = "block_escalate"
        elif not all_passed or high_critical_findings:
            decision = "rework"

        return {
            "passed": all_passed and not high_critical_findings,
            "decision": decision,
            "findings": high_critical_findings,
            "prompt_for_agent": (
                "A security issue was found. Execute mitigation strategy." if decision == "rework" else None
            ),
        }

    @classmethod
    def generate_risk_debt_entries(cls, findings: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Converts HIGH/CRITICAL findings into RISK and DEBT registry entries."""
        risks = []
        debts = []
        for idx, f in enumerate(findings):
            severity = f.get("severity", "HIGH")
            risks.append(
                {
                    "id": f"RISK-SEC-{idx}",
                    "category": "SECURITY",
                    "severity": severity,
                    "strategy": "MT",
                    "description": f.get("message", "Security vulnerability found"),
                }
            )
            debts.append(
                {
                    "id": f"DEBT-SEC-{idx}",
                    "priority": "P0" if severity == "CRITICAL" else "P1",
                    "source": "安全債",
                    "description": f.get("message", "Unresolved security issue"),
                }
            )
        return {"risks": risks, "debts": debts}
