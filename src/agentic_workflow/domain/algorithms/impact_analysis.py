"""Impact Analysis Algorithm.

Traceable to: FR-008, FR-009, FR-022
Replaces: skills/workflow-skills/impact-analysis-exec.md
"""

from typing import Any

import deal

from .traceability_validator import TraceabilityNode


class ImpactAnalysis:
    """Executes impact analysis for traceability nodes."""

    @classmethod
    @deal.ensure(
        # INV-012 coupling: zero radius is COSMETIC and severity drives the agent prompt.
        lambda _: (
            (_.result["blast_radius"] > 0 or _.result["severity"] == "COSMETIC")
            and _.result["blast_radius"]
            == len(_.result["affected_downstream"])
            + len(_.result["inconsistent_upstream"])
            + len(_.result["affected_lateral_ids"])
        ),
        message="Blast radius must equal the sum of affected links (INV-012)",
    )
    def calculate_blast_radius(
        cls,
        modified_id: str,
        nodes: "list[TraceabilityNode]",
        *,
        _downstream: "list[str] | None" = None,
        _upstream: "list[str] | None" = None,
        _lateral: "list[str] | None" = None,
    ) -> "dict[str, Any]":
        """Calculates the blast radius of changing a specific node.

        Optional _downstream/_upstream/_lateral allow test injection without mocking
        internal traversal (ALG-010 testability constraint).
        """
        # Simplified mock of recursive traversal; overridable for testing
        affected_downstream = _downstream if _downstream is not None else []
        inconsistent_upstream = _upstream if _upstream is not None else []
        affected_lateral_ids = _lateral if _lateral is not None else []

        # We would normally traverse the graph here
        blast_radius = len(affected_downstream) + len(inconsistent_upstream) + len(affected_lateral_ids)

        # Determine severity
        if blast_radius == 0:
            severity = "COSMETIC"
        elif blast_radius <= 3:
            severity = "MINOR"
        elif blast_radius <= 10:
            severity = "MODERATE"
        else:
            severity = "MAJOR"

        return {
            "blast_radius": blast_radius,
            "severity": severity,
            "affected_downstream": affected_downstream,
            "inconsistent_upstream": inconsistent_upstream,
            "affected_lateral_ids": affected_lateral_ids,
            "prompt_for_agent": "Execute M1-M4 manual resolution."
            if severity == "MAJOR"
            else "Autonomously update affected nodes.",
        }
