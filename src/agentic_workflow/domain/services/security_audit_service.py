"""Domain Service — SecurityAuditService.

Performs multi-layer security audits and integrates findings into the Pipeline.
Traceable to: FR-016 (Three-Layer Security Audit)
"""

from __future__ import annotations

from typing import Any

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.value_objects.findings import Findings


class SecurityAuditService:
    """Domain service for orchestrating 3-layer security audits."""

    @staticmethod
    def audit_pipeline(pipeline: Pipeline, layer_results: list[dict[str, Any]]) -> Findings:
        """Processes audit results and returns domain Findings.

        Args:
            pipeline: The pipeline aggregate root.
            layer_results: Raw results from various security tools.

        Returns:
            A Findings value object containing security issues.
        """
        findings_list = []
        for res in layer_results:
            layer = res.get("layer", "unknown")
            for f in res.get("findings", []):
                severity = f.get("severity", "MEDIUM")
                msg = f.get("message", "Security issue")
                findings_list.append(f"[{layer}] {severity}: {msg}")

        return Findings(items=findings_list)

    @staticmethod
    def decide_gate_impact(findings: Findings) -> str:
        """Determines the gate decision based on findings severity.

        Args:
            findings: The security findings.

        Returns:
            Gate decision string: "pass" | "rework" | "block"
        """
        if any("CRITICAL" in f for f in findings):
            return "block"
        if any("HIGH" in f for f in findings):
            return "rework"
        return "pass"
