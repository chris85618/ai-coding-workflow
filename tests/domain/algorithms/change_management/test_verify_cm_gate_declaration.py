"""Tests for CM-GATE declaration verification."""

from agentic_workflow.domain.algorithms.change_management import ChangeManagement


class TestVerifyCmGateDeclaration:
    """Tests for CM-GATE declaration verification."""

    def test_returns_false_if_no_declaration(self) -> None:
        """TC-136: Missing declaration check."""
        assert ChangeManagement.verify_cm_gate_declaration("No gate here", ["file.py"]) is False

    def test_returns_true_if_cmgate_and_files_present(self) -> None:
        """TC-137: Valid CM-GATE check."""
        content = "CM-GATE: file.py | Type | Class | ADR"
        assert ChangeManagement.verify_cm_gate_declaration(content, ["file.py"]) is True

    def test_returns_true_if_batchcm_present(self) -> None:
        """TC-138: Valid BATCH-CM check."""
        content = "BATCH-CM: file.py | Type | Class | ADR"
        assert ChangeManagement.verify_cm_gate_declaration(content, ["file.py"]) is True

    def test_returns_false_if_file_missing_from_declaration(self) -> None:
        """TC-139: File missing from declaration check."""
        content = "CM-GATE: other.py | Type | Class"
        assert ChangeManagement.verify_cm_gate_declaration(content, ["file.py"]) is False

    def test_empty_files_list_returns_true_if_gate_present(self) -> None:
        """TC-140: Empty files list with gate check."""
        content = "CM-GATE: declared"
        assert ChangeManagement.verify_cm_gate_declaration(content, []) is True
