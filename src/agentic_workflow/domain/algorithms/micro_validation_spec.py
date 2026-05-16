"""Specification for Micro-Validation results."""

from __future__ import annotations

from dataclasses import dataclass

from agentic_workflow.domain.algorithms.base_specification import Specification


@dataclass
class MicroValidationResult:
    """Result object for micro-validation."""

    has_errors: bool
    error_count: int
    warning_count: int
    messages: list[str]


class ZeroErrorSpecification(Specification[MicroValidationResult]):
    """Specification requiring zero errors."""

    def is_satisfied_by(self, candidate: MicroValidationResult) -> bool:
        """Check if result has zero errors."""
        return not candidate.has_errors and candidate.error_count == 0


class ZeroWarningSpecification(Specification[MicroValidationResult]):
    """Specification requiring zero warnings."""

    def is_satisfied_by(self, candidate: MicroValidationResult) -> bool:
        """Check if result has zero warnings."""
        return candidate.warning_count == 0
