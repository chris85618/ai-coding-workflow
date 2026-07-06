"""DebtSource Enum — Technical debt origin."""

from enum import StrEnum


class DebtSource(StrEnum):
    """Technical debt origin."""

    DESIGN = "design"
    CODE = "code"
    DOCUMENTATION = "documentation"
    TEST = "test"
    QUALITY_GATE = "quality_gate"
    SECURITY = "security"
    VALIDATION = "validation"
