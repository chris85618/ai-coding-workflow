"""Tests for session end hooks assertion."""

from typing import Any

from agentic_workflow.domain.algorithms.change_management import ChangeManagement


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
