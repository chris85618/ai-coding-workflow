"""Unit tests for ChangeManagement algorithm. Traceable to FR-024, FR-025."""

from typing import Any

from agentic_workflow.domain.algorithms.change_management import (
    ChangeManagement,
    ChangeType,
)


class TestValidatePGVG:
    """Tests for PGVG validation logic."""

    def test_valid_content_returns_no_failures(self) -> None:
        """TC-131: Valid content check."""
        result = ChangeManagement.validate_pgvg("Normal content without issues.", "original", ChangeType.MODIFY)
        assert result == []

    def test_unbalanced_backticks_returns_failure(self) -> None:
        """TC-132: Unbalanced backticks detection."""
        result = ChangeManagement.validate_pgvg("```code without closing", "original", ChangeType.CREATE)
        assert any("backtick" in f for f in result)

    def test_even_backticks_are_fine(self) -> None:
        """TC-133: Balanced backticks check."""
        result = ChangeManagement.validate_pgvg("```code``` and ```more```", "original", ChangeType.FIX)
        assert result == []

    def test_create_change_type_accepted(self) -> None:
        """TC-134: CREATE type validation."""
        result = ChangeManagement.validate_pgvg("clean content", "orig", ChangeType.CREATE)
        assert isinstance(result, list)

    def test_fix_change_type_accepted(self) -> None:
        """TC-135: FIX type validation."""
        result = ChangeManagement.validate_pgvg("clean content", "orig", ChangeType.FIX)
        assert isinstance(result, list)


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


class TestAssertSessionEndHooks:
    """Tests for session end hooks assertion."""

    def _valid_change(self, cross_cutting: bool = False) -> dict[str, Any]:
        """Generate a valid change dictionary."""
        return {
            "step_0_classified": True,
            "step_1_generated": True,
            "step_2_pgvg": True,
            "step_3_micro_val": True,
            "step_4_rca_done": True,
            "is_cross_cutting": cross_cutting,
            "step_5_done": True,
        }

    def test_all_steps_present_returns_true(self) -> None:
        """TC-141: All steps present check."""
        assert ChangeManagement.assert_session_end_hooks([self._valid_change()]) is True

    def test_missing_step_0_returns_false(self) -> None:
        """TC-142: Missing Step 0 check."""
        change = self._valid_change()
        change["step_0_classified"] = False
        assert ChangeManagement.assert_session_end_hooks([change]) is False

    def test_missing_step_1_returns_false(self) -> None:
        """TC-143: Missing Step 1 check."""
        change = self._valid_change()
        change["step_1_generated"] = False
        assert ChangeManagement.assert_session_end_hooks([change]) is False

    def test_missing_step_2_returns_false(self) -> None:
        """TC-144: Missing Step 2 check."""
        change = self._valid_change()
        change["step_2_pgvg"] = False
        assert ChangeManagement.assert_session_end_hooks([change]) is False

    def test_missing_step_3_returns_false(self) -> None:
        """TC-145: Missing Step 3 check."""
        change = self._valid_change()
        change["step_3_micro_val"] = False
        assert ChangeManagement.assert_session_end_hooks([change]) is False

    def test_missing_step_4_returns_false(self) -> None:
        """TC-146: Missing Step 4 check."""
        change = self._valid_change()
        change["step_4_rca_done"] = False
        assert ChangeManagement.assert_session_end_hooks([change]) is False

    def test_cross_cutting_without_step5_returns_false(self) -> None:
        """TC-147: Missing Step 5 for cross-cutting check."""
        change = self._valid_change(cross_cutting=True)
        change["step_5_done"] = False
        assert ChangeManagement.assert_session_end_hooks([change]) is False

    def test_cross_cutting_with_step5_returns_true(self) -> None:
        """TC-148: Step 5 present for cross-cutting check."""
        assert ChangeManagement.assert_session_end_hooks([self._valid_change(cross_cutting=True)]) is True

    def test_empty_list_returns_true(self) -> None:
        """TC-149: Empty changes list check."""
        assert ChangeManagement.assert_session_end_hooks([]) is True

    def test_multiple_changes_all_valid(self) -> None:
        """TC-150: Multiple valid changes check."""
        changes = [self._valid_change(), self._valid_change(cross_cutting=True)]
        assert ChangeManagement.assert_session_end_hooks(changes) is True
