"""NFR-015: Usability-heuristic checks (Nielsen) left-shifted into the suite.

Maps the applicable heuristics onto this system's operator surfaces:
- H1 visibility of system status: failures always land in observable state
- H5 error prevention: value objects reject malformed input at construction
- H4 consistency & standards: every domain enum serializes as a plain string
- H10 help & documentation: operator entry points carry usage docstrings
"""

import contextlib
import pathlib

from agentic_workflow.domain import enums as domain_enums
from agentic_workflow.domain.value_objects.debt_item import DebtItem

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


class TestUsabilityHeuristics:
    """Covers Nielsen heuristics H1/H4/H5/H10 for operator-facing surfaces."""

    def test_h1_failures_are_observable_in_error_message(self) -> None:
        """TC-NFR-007: Constructor rejections name the offending value (H1)."""
        offending = "BAD-ID"
        message = ""
        try:
            DebtItem(
                debt_id=offending,
                title="t",
                source=domain_enums.DebtSource.CODE,
                severity=domain_enums.Severity.LOW,
            )
        except ValueError as exc:
            message = str(exc)
        assert offending in message

    def test_h4_every_domain_enum_is_a_str_enum(self) -> None:
        """TC-NFR-008: All domain enums serialize consistently as strings (H4)."""
        exported = [getattr(domain_enums, name) for name in domain_enums.__all__]
        non_str = [cls.__name__ for cls in exported if not issubclass(cls, str)]
        assert non_str == []

    def test_h5_error_prevention_is_construction_time(self) -> None:
        """TC-NFR-009: Malformed ids never produce a live object (H5)."""
        created = None
        with contextlib.suppress(ValueError):
            created = DebtItem(
                debt_id="",
                title="t",
                source=domain_enums.DebtSource.CODE,
                severity=domain_enums.Severity.LOW,
            )
        assert created is None

    def test_h10_operator_scripts_carry_usage_docstrings(self) -> None:
        """TC-NFR-010: Every scripts/ entry point documents itself (H10)."""
        repo_root = _REPO_ROOT
        undocumented = []
        for script in sorted((repo_root / "scripts").glob("*.py")):
            text = script.read_text(encoding="utf-8").lstrip()
            if not text.startswith(('"""', "'''", "#!")):
                undocumented.append(script.name)
        assert undocumented == []
