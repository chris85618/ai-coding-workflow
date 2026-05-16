"""Severity Enum — Finding or impact severity classification."""

from enum import StrEnum


class Severity(StrEnum):
    """Finding or impact severity classification.

    COSMETIC: blast_radius == 0 (INV-012)
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    COSMETIC = "cosmetic"
    YAGNI = "yagni"
