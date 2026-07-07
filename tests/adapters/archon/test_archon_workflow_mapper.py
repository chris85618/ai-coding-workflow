"""Tests for the ArchonWorkflowMapper adapter (FR-073, ADR-STR-030)."""

from agentic_workflow.adapters.archon.workflow_mapper import ArchonWorkflowMapper


class TestArchonWorkflowMapper:
    """Covers the pure string mapping from canonical stages to Archon YAML."""

    def test_header_names_pipeline_and_isolates_worktree(self) -> None:
        """TC-ARCHON-001: The document header carries the pipeline id and worktree isolation."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", ["phase0"])
        assert doc.startswith("name: agentic-workflow-main\n")
        assert "isolation: worktree\n" in doc

    def test_one_step_per_stage_in_canonical_order(self) -> None:
        """TC-ARCHON-002: Every stage yields exactly one step, preserving the given order."""
        stages = ["phase0", "stage3", "phase9"]
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", stages)
        positions = [doc.index(f"- id: {stage_id}\n") for stage_id in stages]
        assert positions == sorted(positions)
        assert doc.count("Execute pipeline stage") == len(stages)

    def test_quality_gate_step_closes_the_workflow(self) -> None:
        """TC-ARCHON-003: The final step is the quality gate enforcing the coverage bar."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", ["phase0"])
        gate_pos = doc.index("- id: quality-gate")
        stage_pos = doc.index("- id: phase0")
        assert gate_pos > stage_pos
        assert "100 percent statement and branch coverage" in doc

    def test_empty_stage_list_still_renders_header_and_gate(self) -> None:
        """TC-ARCHON-004: An empty stage list degrades to header plus quality gate only."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("empty", [])
        assert doc.startswith("name: agentic-workflow-empty\n")
        assert "- id: quality-gate" in doc
        assert "Execute pipeline stage" not in doc
