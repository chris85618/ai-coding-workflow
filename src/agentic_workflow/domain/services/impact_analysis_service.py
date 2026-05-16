"""Domain Service: Impact Analysis."""

from __future__ import annotations

from typing import Any


class ImpactAnalysisService:
    """Domain service for analyzing the impact of changes in the traceability matrix."""

    def analyze_change(
        self,
        *,
        _downstream: list[str] | None = None,
        _upstream: list[str] | None = None,
        _lateral: list[str] | None = None,
    ) -> dict[str, Any]:
        """Calculates the blast radius and severity of a change.

        Isolates the calculation logic from infrastructure or application concerns.
        """
        affected_downstream = _downstream if _downstream is not None else []
        inconsistent_upstream = _upstream if _upstream is not None else []
        affected_lateral_ids = _lateral if _lateral is not None else []

        # Logic for blast radius calculation
        blast_radius = len(affected_downstream) + len(inconsistent_upstream) + len(affected_lateral_ids)

        # Determine severity based on domain rules
        severity = self._determine_severity(blast_radius)

        return {
            "blast_radius": blast_radius,
            "severity": severity,
            "affected_downstream": affected_downstream,
            "inconsistent_upstream": inconsistent_upstream,
            "affected_lateral_ids": affected_lateral_ids,
            "requires_manual_resolution": severity == "MAJOR",
        }

    def _determine_severity(self, blast_radius: int) -> str:
        """Domain rule for severity mapping."""
        if blast_radius == 0:
            return "COSMETIC"
        if blast_radius <= 3:
            return "MINOR"
        if blast_radius <= 10:
            return "MODERATE"
        return "MAJOR"
