"""Domain Service — SecurityAuditService.

Performs multi-layer security audits and integrates findings into the Pipeline.
Traceable to: FR-016 (Three-Layer Security Audit)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import deal

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.value_objects.findings import Findings


class ISecurityAuditService(ABC):
    """Interface for Security Audit Service to satisfy Dependency Inversion."""

    @abstractmethod
    def audit_pipeline(self, pipeline: Pipeline, layer_results: list[dict[str, Any]]) -> Findings:
        """Process audit."""

    @abstractmethod
    def decide_gate_impact(self, findings: Findings) -> str:
        """Decide impact."""


class SecurityAuditService(ISecurityAuditService):
    """Domain service for orchestrating 3-layer security audits."""

    @deal.ensure(
        lambda _: len(_.result.items) == sum(len(res.get("findings", [])) for res in _.layer_results),
        message="Audit must surface every raw finding exactly once",
    )
    def audit_pipeline(self, pipeline: Pipeline, layer_results: list[dict[str, Any]]) -> Findings:
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

    @deal.has()
    @deal.post(lambda result: result in ("pass", "rework", "block"), message="Gate impact is a closed decision set")
    def decide_gate_impact(self, findings: Findings) -> str:
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
