"""Specification for Blast Radius severity."""

from __future__ import annotations

from dataclasses import dataclass

from agentic_workflow.domain.algorithms.base_specification import Specification


@dataclass(frozen=True)
class BlastRadiusInput:
    """Input for blast radius classification."""

    radius: int
    cross_stage_count: int


class CriticalImpactSpecification(Specification[BlastRadiusInput]):
    """Specification for CRITICAL impact."""

    RADIUS_THRESHOLD = 10
    STAGE_THRESHOLD = 3

    def is_satisfied_by(self, candidate: BlastRadiusInput) -> bool:
        """Check if blast radius impact is CRITICAL (INV-010)."""
        return candidate.radius >= self.RADIUS_THRESHOLD or candidate.cross_stage_count >= self.STAGE_THRESHOLD


class HighImpactSpecification(Specification[BlastRadiusInput]):
    """Specification for HIGH impact."""

    RADIUS_THRESHOLD = 5
    STAGE_THRESHOLD = 2

    def is_satisfied_by(self, candidate: BlastRadiusInput) -> bool:
        """Check if blast radius impact is HIGH (INV-011)."""
        return candidate.radius >= self.RADIUS_THRESHOLD or candidate.cross_stage_count >= self.STAGE_THRESHOLD


class ZeroImpactSpecification(Specification[BlastRadiusInput]):
    """Specification for COSMETIC (Zero) impact (INV-012)."""

    def is_satisfied_by(self, candidate: BlastRadiusInput) -> bool:
        """Check if blast radius impact is COSMETIC (INV-012)."""
        return candidate.radius == 0
