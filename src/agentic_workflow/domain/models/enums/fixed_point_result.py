"""FixedPointResult Enum — Iteration convergence check result."""

from enum import StrEnum


class FixedPointResult(StrEnum):
    """Iteration convergence check result."""

    REACHED = "reached"
    NOT_REACHED = "not_reached"
    DIVERGING = "diverging"
    MAX_ITERATIONS = "max_iterations"
