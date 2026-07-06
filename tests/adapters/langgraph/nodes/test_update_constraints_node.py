"""Tests for node_update_constraints (FR-070, ADR-STR-029 Ouroboros closure)."""

from typing import Any
from unittest.mock import MagicMock, patch

from agentic_workflow.adapters.langgraph.nodes import node_update_constraints
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState


class TestUpdateConstraintsNode:
    """Covers persisting retro lessons as assumptions for the next session."""

    def test_lessons_become_registered_assumptions(self) -> None:
        """TC-V2-048: Lessons are appended to the registry document as ASM lines."""
        fake_fs = MagicMock()
        fake_fs.resolve_path.return_value = "resolved/assumption-registry.md"
        fake_fs.exists.return_value = True
        fake_fs.read_text.return_value = "# Assumption Registry (L2 Output-Affecting)\n- ASM-001: old\n"
        metadata: dict[str, Any] = {"lessons": ["always run pytest"], "injected_assumptions": ["ASM-001: old"]}
        with patch("agentic_workflow.adapters.langgraph.nodes.get_filesystem", return_value=fake_fs):
            result = node_update_constraints(WorkflowState(pipeline_id="p", metadata=metadata))
        assert result["metadata"]["registered_assumptions"] == ["ASM-002"]
        written = fake_fs.write_text.call_args[0][1]
        assert "- ASM-002: always run pytest" in written
        assert "- ASM-001: old" in written

    def test_missing_registry_creates_header(self) -> None:
        """TC-V2-049: A fresh registry document gets the standard header."""
        fake_fs = MagicMock()
        fake_fs.exists.return_value = False
        metadata: dict[str, Any] = {"lessons": ["lesson"]}
        with patch("agentic_workflow.adapters.langgraph.nodes.get_filesystem", return_value=fake_fs):
            node_update_constraints(WorkflowState(pipeline_id="p", metadata=metadata))
        written = fake_fs.write_text.call_args[0][1]
        assert written.startswith("# Assumption Registry (L2 Output-Affecting)")

    def test_no_lessons_skips_persistence(self) -> None:
        """TC-V2-050: Nothing to register leaves the filesystem untouched."""
        fake_fs = MagicMock()
        with patch("agentic_workflow.adapters.langgraph.nodes.get_filesystem", return_value=fake_fs):
            result = node_update_constraints(WorkflowState(pipeline_id="p"))
        fake_fs.write_text.assert_not_called()
        assert result["metadata"]["registered_assumptions"] == []

    def test_filesystem_error_is_recorded(self) -> None:
        """TC-V2-051: Persistence errors are surfaced via last_error."""
        fake_fs = MagicMock()
        fake_fs.exists.side_effect = OSError("disk")
        metadata: dict[str, Any] = {"lessons": ["lesson"]}
        with patch("agentic_workflow.adapters.langgraph.nodes.get_filesystem", return_value=fake_fs):
            result = node_update_constraints(WorkflowState(pipeline_id="p", metadata=metadata))
        assert result["last_error"] is not None
