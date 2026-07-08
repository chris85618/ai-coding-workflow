"""Success-path tests for phase and micro-validation step nodes (ADR-STR-033).

These paths were previously exercised through the LangGraph facade tests;
after the facade removal they are covered directly against the adapters.
"""

from typing import Any, cast
from unittest.mock import MagicMock, patch

from agentic_workflow.adapters.orchestration.nodes import (
    node_agent_alpha_critique,
    node_phase_0_init,
    node_phase_1_understanding,
    node_phase_2_analysis,
    node_phase_9_ship,
    node_phase_10_retro,
    node_step_0_format,
    node_step_1_id_structure,
    node_step_5_orphan,
    node_step_7_record_change,
    set_container,
)
from agentic_workflow.adapters.orchestration.state_mapper import WorkflowState
from agentic_workflow.domain.aggregates.pipeline import Pipeline


class TestPhaseNodeSuccessPaths:
    """Covers the success branches of phase nodes."""

    def teardown_method(self) -> None:
        """Reset the global container so later tests see a clean state."""
        set_container(None)

    def test_phase_0_init_starts_pipeline_via_container(self) -> None:
        """node_phase_0_init maps the started pipeline back into the state."""
        pipeline = Pipeline(pipeline_id="p0")
        pipeline.start()
        container = MagicMock()
        container.start_pipeline.execute.return_value = pipeline
        set_container(container)
        state = node_phase_0_init(WorkflowState(pipeline_id="p0"))
        assert state["pipeline_status"] == "running"

    def test_phase_1_understanding_writes_knowledge_graph(self) -> None:
        """node_phase_1_understanding persists the knowledge graph skeleton."""
        fs = MagicMock()
        with patch("agentic_workflow.adapters.filesystem.get_filesystem", return_value=fs):
            state = node_phase_1_understanding(WorkflowState(pipeline_id="p"))
        assert state["current_position"] == "phase1"
        fs.write_text.assert_called_once()

    def test_phase_2_analysis_writes_report(self) -> None:
        """node_phase_2_analysis persists the project analysis report."""
        fs = MagicMock()
        with patch("agentic_workflow.adapters.filesystem.get_filesystem", return_value=fs):
            state = node_phase_2_analysis(WorkflowState(pipeline_id="p"))
        assert state["current_position"] == "phase2"
        fs.write_text.assert_called_once()

    def test_phase_9_ship_writes_deployment_record(self) -> None:
        """node_phase_9_ship persists the deployment record."""
        fs = MagicMock()
        with patch("agentic_workflow.adapters.filesystem.get_filesystem", return_value=fs):
            state = node_phase_9_ship(WorkflowState(pipeline_id="p"))
        assert state["current_position"] == "phase9"
        fs.write_text.assert_called_once()

    def test_phase_10_retro_writes_lessons(self) -> None:
        """node_phase_10_retro persists the lessons learned document."""
        fs = MagicMock()
        with patch("agentic_workflow.adapters.filesystem.get_filesystem", return_value=fs):
            state = node_phase_10_retro(WorkflowState(pipeline_id="p"))
        assert state["current_position"] == "phase10"
        fs.write_text.assert_called_once()

    def test_agent_alpha_critique_records_findings(self) -> None:
        """node_agent_alpha_critique appends optimized-prompt findings to the state."""
        container = MagicMock()
        container.prompt_optimizer.optimize.return_value = "optimized prompt"
        container.reasoner.reason.return_value = "CRITICAL: gap found"
        set_container(container)
        state = node_agent_alpha_critique(WorkflowState(pipeline_id="p", metadata={}))
        assert state["current_findings"] == ["CRITICAL: gap found"]
        assert state["findings_history"] == [["CRITICAL: gap found"]]
        assert state["metadata"]["recent_findings"] == ["CRITICAL: gap found"]


class TestStepNodePassBranches:
    """Covers the passing branches of micro-validation step nodes."""

    def test_step_0_format_passes_on_valid_content(self) -> None:
        """A valid format keeps the gate open."""
        with patch(
            "agentic_workflow.domain.algorithms.micro_validation.MicroValidation.validate_format",
            return_value=True,
        ):
            state = node_step_0_format(WorkflowState(pipeline_id="p", metadata={}))
        assert state.get("gate_decision") is None

    def test_step_1_id_structure_passes_on_valid_ids(self) -> None:
        """Valid traceable ids keep the gate open."""
        with patch(
            "agentic_workflow.domain.algorithms.micro_validation.MicroValidation.validate_structure",
            return_value=True,
        ):
            state = node_step_1_id_structure(WorkflowState(pipeline_id="p", metadata={}))
        assert state.get("gate_decision") is None

    def test_step_5_orphan_passes_when_no_orphans(self) -> None:
        """A fully linked graph keeps the gate open."""
        metadata = {"recent_changed_ids": ["FR-001"]}
        with patch(
            "agentic_workflow.domain.algorithms.traceability_validator.TraceabilityValidator.orphan_check",
            return_value=[],
        ):
            state = node_step_5_orphan(WorkflowState(pipeline_id="p", metadata=metadata))
        assert state.get("gate_decision") is None

    def test_step_7_record_change_marks_metadata(self) -> None:
        """The change record lands in metadata on the happy path."""
        state = node_step_7_record_change(WorkflowState(pipeline_id="p", metadata={}))
        assert state["metadata"]["change_recorded"] is True

    def test_step_7_record_change_reports_error_on_bad_metadata(self) -> None:
        """A non-mapping metadata payload lands in last_error instead of raising."""
        state = WorkflowState(pipeline_id="p")
        state["metadata"] = cast(dict[str, Any], ())
        result = node_step_7_record_change(state)
        assert "not support item assignment" in str(result.get("last_error"))
