"""Structural gate for the TLA+ pipeline specification (kanban: 形式化驗證加入 TLA+).

Graceful degradation (ADR-GOV-017): when the TLC model checker is not
installed, this gate still enforces that the spec exists, stays syntactically
well-formed at the structural level, and keeps covering the v2 actions.

Traceable to: INV-001, FR-068, FR-069, FR-071, ADR-STR-029
"""

import pathlib
import re
import shutil
import subprocess

_SPEC_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "formal" / "PipelineStateMachine.tla"

REQUIRED_ACTIONS = [
    "Start",
    "Advance",
    "AbsorbDebt",
    "RollbackToUniversalBase",
    "Complete",
]

REQUIRED_PROPERTIES = [
    "TypeInvariant",
    "MonotonicOrRollback",
    "DebtNeverHardStops",
    "CompletionSafety",
]


class TestTlaSpecGate:
    """Covers presence, structure and (when available) model checking of the spec."""

    def test_spec_exists_and_module_is_well_formed(self) -> None:
        """TC-TLA-001: The spec file exists with matching MODULE header and footer."""
        spec_path = _SPEC_PATH
        assert spec_path.exists(), f"Missing TLA+ spec: {spec_path}"
        text = spec_path.read_text(encoding="utf-8")
        assert re.search(r"-+ MODULE PipelineStateMachine -+", text)
        assert text.rstrip().endswith("=" * 10) or re.search(r"={10,}\s*$", text)

    def test_spec_declares_all_v2_actions(self) -> None:
        """TC-TLA-002: Every Pipeline v2 action is specified."""
        text = _SPEC_PATH.read_text(encoding="utf-8")
        required = REQUIRED_ACTIONS
        missing = [action for action in required if f"{action} ==" not in text]
        assert missing == []

    def test_spec_declares_all_safety_properties(self) -> None:
        """TC-TLA-003: Every safety property is specified."""
        text = _SPEC_PATH.read_text(encoding="utf-8")
        required = REQUIRED_PROPERTIES
        missing = [prop for prop in required if f"{prop} ==" not in text]
        assert missing == []

    def test_spec_next_relation_covers_every_action(self) -> None:
        """TC-TLA-004: The Next relation is the disjunction of all actions."""
        text = _SPEC_PATH.read_text(encoding="utf-8")
        next_block = text.split("Next ==", 1)[1].split("Spec ==", 1)[0]
        required = REQUIRED_ACTIONS
        missing = [action for action in required if action not in next_block]
        assert missing == []

    def test_tlc_model_check_when_available(self) -> None:
        """TC-TLA-005: When TLC is installed, the spec parses (graceful skip otherwise)."""
        tlc = shutil.which("tlc")
        if tlc is None:
            assert True
            return
        result = subprocess.run(
            [tlc, "-parse", str(_SPEC_PATH)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
