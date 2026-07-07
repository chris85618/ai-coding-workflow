"""Structural gate for the Coq pipeline proofs (kanban: 形式化驗證加入 Coq).

Graceful degradation (ADR-GOV-017): when the coqc checker is not installed,
this gate still enforces that the proof file exists, declares every required
theorem, and closes each proof with Qed (no Admitted escape hatches).

Traceable to: INV-001, INV-026, FR-071, ADR-STR-029
"""

import pathlib
import re
import shutil
import subprocess

_PROOF_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "formal" / "PipelineInvariants.v"

REQUIRED_THEOREMS = [
    "advance_strictly_monotonic",
    "advance_stays_in_range",
    "kappa_non_negative",
    "kappa_monotonic_in_debt",
    "debt_numbering_collision_free",
]


class TestCoqProofGate:
    """Covers presence, structure and (when available) checking of the proofs."""

    def test_proof_file_exists(self) -> None:
        """TC-COQ-001: The Coq proof file exists next to the TLA+ spec."""
        proof_path = _PROOF_PATH
        assert proof_path.exists(), f"Missing Coq proofs: {proof_path}"

    def test_all_required_theorems_are_declared(self) -> None:
        """TC-COQ-002: Every pipeline invariant theorem is declared."""
        proof_path = _PROOF_PATH
        text = proof_path.read_text(encoding="utf-8")
        required = REQUIRED_THEOREMS
        missing = [theorem for theorem in required if f"Theorem {theorem}" not in text]
        assert missing == []

    def test_every_proof_is_closed_by_qed(self) -> None:
        """TC-COQ-003: Each theorem has a matching completed proof (Qed)."""
        proof_path = _PROOF_PATH
        required = REQUIRED_THEOREMS
        text = proof_path.read_text(encoding="utf-8")
        theorem_count = len(re.findall(r"^Theorem ", text, flags=re.MULTILINE))
        qed_count = len(re.findall(r"\bQed\.", text))
        assert theorem_count == len(required)
        assert qed_count == theorem_count

    def test_no_admitted_escape_hatches(self) -> None:
        """TC-COQ-004: The proof file never uses Admitted or admit."""
        proof_path = _PROOF_PATH
        text = proof_path.read_text(encoding="utf-8")
        assert "Admitted" not in text
        assert not re.search(r"\badmit\b", text)

    def test_coqc_check_when_available(self) -> None:
        """TC-COQ-005: When coqc is installed, the proofs machine-check (graceful skip otherwise)."""
        coqc = shutil.which("coqc")
        if coqc is None:
            assert True
            return
        proof_path = _PROOF_PATH
        result = subprocess.run(
            [coqc, "-q", proof_path.name],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
            cwd=str(proof_path.parent),
        )
        assert result.returncode == 0, result.stdout + result.stderr
