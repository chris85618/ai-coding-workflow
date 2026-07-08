"""Tests for the ArchonWorkflowMapper adapter (FR-073, FR-077, FR-078, ADR-STR-030, ADR-STR-033)."""

from agentic_workflow.adapters.archon.workflow_mapper import ArchonWorkflowMapper


class TestArchonWorkflowMapper:
    """Covers the pure string mapping from canonical positions to an Archon nodes DAG."""

    def test_header_names_pipeline_and_declares_nodes_dag(self) -> None:
        """TC-ARCHON-001: The header carries name, description, interactive flag and nodes array."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", ["phase0"])
        assert doc.startswith("name: agentic-workflow-main\n")
        assert "description: >\n" in doc
        assert "interactive: true\n" in doc
        assert "worktree:\n  enabled: false\n" in doc
        assert "nodes:\n" in doc
        assert "steps:" not in doc

    def test_positions_render_in_canonical_order(self) -> None:
        """TC-ARCHON-002: Position blocks preserve the given canonical order via depends_on chaining."""
        stages = ["phase0", "stage3", "phase9", "phase10"]
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", stages)
        markers = ["  - id: phase0\n", "  - id: stage3\n", "  - id: sonar-gate\n", "  - id: phase10\n"]
        positions = [doc.index(marker) for marker in markers]
        assert positions == sorted(positions)
        assert "depends_on: [inject]\n" in doc
        assert "depends_on: [stage3-gate]\n" in doc

    def test_stage_block_renders_loop_with_deterministic_convergence(self) -> None:
        """TC-ARCHON-018: Stage blocks carry the α/β loop with until_bash fixed-point check (ALG-001)."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", ["stage3"])
        assert "  - id: stage3-iterate\n" in doc
        assert "    loop:\n" in doc
        assert "      max_iterations:" in doc
        assert "      until: CONVERGED\n" in doc
        assert "      until_bash: |\n" in doc
        assert "--node alpha" in doc
        assert "--node beta" in doc
        assert "--node check_fixed_point" in doc
        assert "when: \"$stage3-route.output == 'rollback'\"" in doc
        assert "when: \"$stage3-route.output != 'rollback'\"" in doc
        assert "  - id: stage3-gate\n    approval:\n" in doc

    def test_phase_9_block_renders_gates_and_conditional_debt(self) -> None:
        """TC-ARCHON-019: Phase 9 carries sonar/security gates with conditional debt absorption."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", ["phase9"])
        markers = ["  - id: sonar-gate\n", "  - id: sonar-debt\n", "  - id: security-gate\n", "  - id: security-debt\n"]
        assert all(marker in doc for marker in markers)
        assert doc.count("--node route_debt") == 2
        assert "when: \"$sonar-route.output == 'debt'\"" in doc
        assert doc.count("trigger_rule: none_failed_min_one_success\n") == 2

    def test_every_workflow_node_command_uses_single_node_runner(self) -> None:
        """TC-ARCHON-020: All --node commands go through scripts/run_node.py (FR-077)."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", ["phase0", "stage3", "phase9", "phase10"])
        node_lines = [line for line in doc.splitlines() if "--node" in line]
        assert node_lines
        assert all("scripts/run_node.py" in line for line in node_lines)

    def test_quality_gate_node_closes_the_workflow(self) -> None:
        """TC-ARCHON-003: The final node is a deterministic quality gate bash node."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("main", ["phase0"])
        gate_pos = doc.index("  - id: quality-gate\n")
        stage_pos = doc.index("  - id: phase0\n")
        assert gate_pos > stage_pos
        assert ".venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests scripts" in doc
        assert ".venv/bin/python -m mypy src tests scripts" in doc
        assert "depends_on: [complete]\n" in doc

    def test_empty_stage_list_still_renders_init_and_gate(self) -> None:
        """TC-ARCHON-004: An empty position list degrades to init nodes plus quality gate."""
        doc = ArchonWorkflowMapper().to_workflow_yaml("empty", [])
        assert doc.startswith("name: agentic-workflow-empty\n")
        assert "  - id: inject\n" in doc
        assert "  - id: complete\n" in doc
        assert "  - id: quality-gate\n" in doc
