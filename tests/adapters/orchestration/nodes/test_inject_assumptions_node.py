"""Tests for node_inject_assumptions (FR-070, ADR-STR-029)."""

from unittest.mock import MagicMock, patch

from agentic_workflow.adapters.orchestration.nodes import node_inject_assumptions
from agentic_workflow.adapters.orchestration.state_mapper import WorkflowState


class TestInjectAssumptionsNode:
    """Covers session-start injection of L2 output-affecting assumptions."""

    def test_injects_asm_lines_from_registry_doc(self) -> None:
        """TC-V2-038: ASM lines from the registry document are injected."""
        fake_fs = MagicMock()
        fake_fs.resolve_path.return_value = "resolved/assumption-registry.md"
        fake_fs.read_text.return_value = "# Registry\n- ASM-001: no pragma\n- ASM-002: no ignore\nother line\n"
        with patch("agentic_workflow.adapters.orchestration.nodes.get_filesystem", return_value=fake_fs):
            result = node_inject_assumptions(WorkflowState(pipeline_id="p"))
        assert result["metadata"]["injected_assumptions"] == ["ASM-001: no pragma", "ASM-002: no ignore"]

    def test_missing_registry_injects_nothing(self) -> None:
        """TC-V2-039: Graceful degradation — a missing registry injects an empty list."""
        fake_fs = MagicMock()
        fake_fs.read_text.side_effect = FileNotFoundError("gone")
        with patch("agentic_workflow.adapters.orchestration.nodes.get_filesystem", return_value=fake_fs):
            result = node_inject_assumptions(WorkflowState(pipeline_id="p"))
        assert result["metadata"]["injected_assumptions"] == []
