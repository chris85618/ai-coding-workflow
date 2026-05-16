"""DebtSource Enum — Technical debt origin."""

from enum import StrEnum


class DebtSource(StrEnum):
    """Technical debt origin."""

    DESIGN = "design"
    CODE = "code"
    DOCUMENTATION = "documentation"
    TEST = "test"
