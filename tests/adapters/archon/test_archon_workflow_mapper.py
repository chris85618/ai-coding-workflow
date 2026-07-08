"""Tests for the ArchonWorkflowMapper adapter (FR-073, FR-077, FR-078, ADR-STR-030, ADR-STR-033)."""

from agentic_workflow.adapters.archon.workflow_mapper import ArchonWorkflowMapper


class TestArchonWorkflowMapper:
    """Covers the pure string mapping from canonical positions to Archon YAML."""

    def test_header_names_pipeline_and_isolates_worktree(self) -> None:
        """TC-ARCHON-001: The document header carries the pipeline id and worktree isolation."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", ["phase0"])
        assert doc.startswith("name: agentic-workflow-main\n")
        assert "isolation: worktree\n" in doc

    def test_positions_render_in_canonical_order(self) -> None:
        """TC-ARCHON-002: Position blocks preserve the given canonical order."""
        stages = ["phase0", "stage3", "phase9", "phase10"]
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", stages)
        markers = ["- id: phase0\n", "- id: stage_3_planning\n", "- id: sonar_gate\n", "- id: phase10\n"]
        positions = [doc.index(marker) for marker in markers]
        assert positions == sorted(positions)

    def test_stage_block_renders_iteration_loop_with_routing(self) -> None:
        """TC-ARCHON-018: Stage blocks carry the α/β loop, fixed-point and HITL routing (ALG-001)."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", ["stage3"])
        assert "loop:\n" in doc
        assert "max_iterations:" in doc
        assert "--node alpha" in doc
        assert "--node beta" in doc
        assert "--node check_fixed_point" in doc
        assert "--node hitl_gate_choice" in doc
        assert "rollback: stage3-rollback" in doc
        assert "- id: stage3-align\n" in doc

    def test_phase_9_block_renders_gates_and_conditional_debt(self) -> None:
        """TC-ARCHON-019: Phase 9 carries sonar/security gates with conditional debt absorption."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", ["phase9"])
        markers = ["- id: sonar_gate\n", "- id: sonar_debt\n", "- id: security_audit\n", "- id: security_debt\n"]
        assert all(marker in doc for marker in markers)
        assert doc.count("--node route_debt") == 2
        assert "equals: debt" in doc

    def test_every_command_step_uses_single_node_runner(self) -> None:
        """TC-ARCHON-020: All command steps go through scripts/run_node.py (FR-077)."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", ["phase0", "stage3", "phase9", "phase10"])
        command_lines = [line for line in doc.splitlines() if "python" in line]
        assert command_lines
        assert all("scripts/run_node.py" in line for line in command_lines)

    def test_quality_gate_step_closes_the_workflow(self) -> None:
        """TC-ARCHON-003: The final step is the quality gate enforcing the coverage bar."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", ["phase0"])
        gate_pos = doc.index("- id: quality-gate")
        stage_pos = doc.index("- id: phase0")
        assert gate_pos > stage_pos
        assert "100 percent statement and branch coverage" in doc

    def test_empty_stage_list_still_renders_header_and_gate(self) -> None:
        """TC-ARCHON-004: An empty position list degrades to init steps plus quality gate."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("empty", [])
        assert doc.startswith("name: agentic-workflow-empty\n")
        assert "- id: quality-gate" in doc
        assert "- id: inject\n" in doc
        assert "- id: complete\n" in doc
