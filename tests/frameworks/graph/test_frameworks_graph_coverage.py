"""Tests for frameworks/graph.py to maximize branch coverage.

Traceable to: FR-001, FR-002, ADR-STR-003.
"""

from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
from agentic_workflow.frameworks.graph import (
    IterationGraphBuilder,
    MasterGraphBuilder,
    MicroValidationGraphBuilder,
    agent_alpha_critique,
    agent_beta_resolve,
    check_fixed_point,
    hitl_gate_choice,
    phase_0_init,
    phase_1_understanding,
    phase_2_analysis,
    phase_9_ship,
    phase_10_retro,
    root_cause_leftshift,
    stage_3_planning,
    stage_4_algorithm,
    stage_5_ooad,
    stage_6_formal,
    stage_7_bdd,
    stage_8_tdd,
    step_0_format,
    step_1_id_structure,
    step_2_forward_trace,
    step_3_backward_trace,
    step_4_semantic,
    step_5_5_lateral_trace,
    step_5_7_lesson_reuse,
    step_5_orphan,
    step_6_trigger_impact,
    step_7_record_change,
)

DUMMY_STATE = WorkflowState(
    pipeline_id="test-001",
    pipeline_status="running",
    current_position="phase0",
    last_gate_decision=None,
    metadata={},
)


class TestMicroValidationStepNodes:
    """Test individual step nodes in the micro-validation graph."""

    """Identity test suite for micro-validation graph nodes."""

    def test_step_0_format(self) -> None:
        """TC-041: Step 0 passthrough."""
        assert step_0_format(DUMMY_STATE) is DUMMY_STATE

    def test_step_1_id_structure(self) -> None:
        """TC-042: Step 1 passthrough."""
        assert step_1_id_structure(DUMMY_STATE) is DUMMY_STATE

    def test_step_2_forward_trace(self) -> None:
        """TC-043: Step 2 passthrough."""
        assert step_2_forward_trace(DUMMY_STATE) is DUMMY_STATE

    def test_step_3_backward_trace(self) -> None:
        """TC-044: Step 3 passthrough."""
        assert step_3_backward_trace(DUMMY_STATE) is DUMMY_STATE

    def test_step_4_semantic(self) -> None:
        """TC-045: Step 4 passthrough."""
        assert step_4_semantic(DUMMY_STATE) is DUMMY_STATE

    def test_step_5_orphan(self) -> None:
        """TC-046: Step 5 passthrough."""
        assert step_5_orphan(DUMMY_STATE) is DUMMY_STATE

    def test_step_5_5_lateral_trace(self) -> None:
        """TC-047: Step 5.5 passthrough."""
        assert step_5_5_lateral_trace(DUMMY_STATE) is DUMMY_STATE

    def test_step_5_7_lesson_reuse(self) -> None:
        """TC-048: Step 5.7 passthrough."""
        assert step_5_7_lesson_reuse(DUMMY_STATE) is DUMMY_STATE

    def test_step_6_trigger_impact(self) -> None:
        """TC-049: Step 6 passthrough."""
        assert step_6_trigger_impact(DUMMY_STATE) is DUMMY_STATE

    def test_step_7_record_change(self) -> None:
        """TC-050: Step 7 passthrough."""
        assert step_7_record_change(DUMMY_STATE) is DUMMY_STATE


class TestIterationGraphNodes:
    """Test logical nodes in the iteration graph."""

    """Test suite for iteration graph logical nodes."""

    def test_agent_alpha_critique(self) -> None:
        """TC-051: Alpha critique passthrough."""
        assert agent_alpha_critique(DUMMY_STATE) is DUMMY_STATE

    def test_agent_beta_resolve(self) -> None:
        """TC-052: Beta resolve passthrough."""
        assert agent_beta_resolve(DUMMY_STATE) is DUMMY_STATE

    def test_root_cause_leftshift(self) -> None:
        """TC-053: RCA leftshift passthrough."""
        assert root_cause_leftshift(DUMMY_STATE) is DUMMY_STATE

    def test_check_fixed_point_returns_beta(self) -> None:
        """TC-054: Fixed point check returns beta."""
        beta_state = DUMMY_STATE.copy()
        beta_state["current_findings"] = ["CRITICAL: missing validation"]
        result = check_fixed_point(beta_state)
        assert result == "beta"

    def test_check_fixed_point_returns_exit_loop(self) -> None:
        """TC-054b: Fixed point check returns exit_loop when converged."""
        converged_state = DUMMY_STATE.copy()
        converged_state["current_findings"] = ["YAGNI: unnecessary log"]
        result = check_fixed_point(converged_state)
        assert result == "exit_loop"

    def test_hitl_gate_choice_returns_pass(self) -> None:
        """TC-055: HITL choice returns pass."""
        result = hitl_gate_choice(DUMMY_STATE)
        assert result == "pass"

    def test_iterate_stage(self) -> None:
        """TC-055b: Test iterate_stage facade."""
        from unittest.mock import MagicMock

        from agentic_workflow.adapters.langgraph.nodes import set_container
        from agentic_workflow.frameworks.dependency_container import DependencyContainer
        from agentic_workflow.frameworks.graph import iterate_stage

        container = DependencyContainer(
            pipeline_repo=MagicMock(),
            checkpoint_repo=MagicMock(),
            doc_io=MagicMock(),
            reasoner=MagicMock(),
        )
        mock_pipeline = MagicMock()
        mock_pipeline.pipeline_id = "test-001"
        mock_pipeline.status.value = "running"
        mock_pipeline.current_position = "stage3"

        mock_stage = MagicMock()
        mock_stage.iteration_count = 0
        mock_stage.stage_id = "stage3"
        mock_stage.status.value = "pending"
        mock_pipeline.stages = {"stage3": mock_stage}

        import typing

        typing.cast(MagicMock, container.pipeline_repo).get_by_id.return_value = mock_pipeline

        try:
            set_container(container)
            res = iterate_stage(DUMMY_STATE)
            assert res is not None
        finally:
            set_container(None)


class TestMasterPipelineNodes:
    """Test major phase/stage nodes in the master pipeline."""

    """Test suite for master pipeline graph nodes."""

    def test_phase_0_init(self) -> None:
        """TC-056: Phase 0 passthrough."""
        assert phase_0_init(DUMMY_STATE) is DUMMY_STATE

    def test_phase_1_understanding(self) -> None:
        """TC-057: Phase 1 passthrough."""
        assert phase_1_understanding(DUMMY_STATE) is DUMMY_STATE

    def test_phase_2_analysis(self) -> None:
        """TC-058: Phase 2 passthrough."""
        assert phase_2_analysis(DUMMY_STATE) is DUMMY_STATE

    def test_stage_3_planning(self) -> None:
        """TC-059: Stage 3 passthrough."""
        assert stage_3_planning(DUMMY_STATE) is DUMMY_STATE

    def test_stage_4_algorithm(self) -> None:
        """TC-060: Stage 4 passthrough."""
        assert stage_4_algorithm(DUMMY_STATE) is DUMMY_STATE

    def test_stage_5_ooad(self) -> None:
        """TC-061: Stage 5 passthrough."""
        assert stage_5_ooad(DUMMY_STATE) is DUMMY_STATE

    def test_stage_6_formal(self) -> None:
        """TC-062: Stage 6 passthrough."""
        assert stage_6_formal(DUMMY_STATE) is DUMMY_STATE

    def test_stage_7_bdd(self) -> None:
        """TC-063: Stage 7 passthrough."""
        assert stage_7_bdd(DUMMY_STATE) is DUMMY_STATE

    def test_stage_8_tdd(self) -> None:
        """TC-064: Stage 8 passthrough."""
        assert stage_8_tdd(DUMMY_STATE) is DUMMY_STATE

    def test_phase_9_ship(self) -> None:
        """TC-065: Phase 9 passthrough."""
        assert phase_9_ship(DUMMY_STATE) is DUMMY_STATE

    def test_phase_10_retro(self) -> None:
        """TC-066: Phase 10 passthrough."""
        assert phase_10_retro(DUMMY_STATE) is DUMMY_STATE


class TestGraphBuilders:
    """Test functions that compile LangGraph instances."""

    """Test suite for graph compilation builders."""

    def test_build_micro_validation_graph_compiles(self) -> None:
        """TC-067: Micro validation graph builds."""
        graph = MicroValidationGraphBuilder.build()
        assert graph is not None
        assert hasattr(graph, "invoke")

    def test_build_iteration_graph_compiles(self) -> None:
        """TC-068: Iteration graph builds."""
        graph = IterationGraphBuilder.build()
        assert graph is not None
        assert hasattr(graph, "invoke")

    def test_build_graph_compiles(self) -> None:
        """TC-069: Master graph builds."""
        graph = MasterGraphBuilder.build()
        assert graph is not None
        assert hasattr(graph, "invoke")
