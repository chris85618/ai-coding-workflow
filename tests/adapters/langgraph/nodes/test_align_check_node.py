"""Tests for node_align_check (FR-072, ADR-STR-029)."""

from typing import Any

from agentic_workflow.adapters.langgraph.nodes import node_align_check
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState


class TestAlignCheckNode:
    """Covers the diverge → converge → align closure node."""

    def test_aligned_state_passes(self) -> None:
        """TC-V2-043: No alignment evidence issues certifies the fixed point."""
        result = node_align_check(WorkflowState(pipeline_id="p"))
        assert result["gate_decision"] == "pass"
        assert result["metadata"]["alignment_issues"] == []

    def test_misaligned_state_feeds_back_to_alpha(self) -> None:
        """TC-V2-044: Misalignments fail the gate and extend current findings."""
        metadata: dict[str, Any] = {
            "traceability_issues": ["FR-001 orphan"],
            "consistency_issues": ["doc drift"],
        }
        state = WorkflowState(pipeline_id="p", metadata=metadata, current_findings=["HIGH: bug"])
        result = node_align_check(state)
        assert result["gate_decision"] == "fail"
        assert result["current_findings"] == ["HIGH: bug", "ALIGN: FR-001 orphan", "ALIGN: doc drift"]
        assert result["metadata"]["alignment_issues"] == ["ALIGN: FR-001 orphan", "ALIGN: doc drift"]
