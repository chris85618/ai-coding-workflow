"""GateDecision Enum — Auto-gate decision result."""

from enum import StrEnum


class GateDecision(StrEnum):
    """Auto-gate decision result. Replaces HitlChoice (ADR-STR-003)."""

    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    FAIL = "fail"
