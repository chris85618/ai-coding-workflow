"""Unit tests for MarkdownPipelineRepository round-trip persistence (FR-002, ADR-STR-021)."""

from unittest.mock import MagicMock

import pytest

from agentic_workflow.adapters.persistence.markdown_pipeline_repository import MarkdownPipelineRepository
from agentic_workflow.application.ports.doc_io.document_io_gateway import DocumentIOGateway
from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.enums import GateDecision, PipelineStatus, StageStatus


class TestMarkdownPipelineRepository:
    """Test suite for MarkdownPipelineRepository."""

    @pytest.fixture
    def mock_io(self) -> MagicMock:
        """Create a mock document IO gateway."""
        return MagicMock(spec=DocumentIOGateway)

    def _round_trip(self, mock_io: MagicMock, pipeline: Pipeline) -> Pipeline | None:
        """Save the pipeline, then feed the written document back into get_current."""
        repo = MarkdownPipelineRepository(mock_io)
        repo.save(pipeline)
        written = mock_io.write.call_args[0][1]
        mock_io.exists.return_value = True
        mock_io.read.return_value = written
        return repo.get_current()

    def test_save_writes_parseable_state_document(self, mock_io: MagicMock) -> None:
        """TC-BOOT-005: Saving writes id, position, status, gate and stage table to the state file."""
        repo = MarkdownPipelineRepository(mock_io)
        repo.save(Pipeline(pipeline_id="test-save"))

        mock_io.write.assert_called_once()
        path, content = mock_io.write.call_args[0]
        assert "docs/workflow-state.md" in path
        assert "**Pipeline ID**: test-save" in content
        assert "**Pipeline Position**: phase0" in content
        assert "**Pipeline Status**: not_started" in content
        assert "**Last Gate Decision**: none" in content
        assert "| phase0 | pending | 0 |" in content

    def test_get_current_not_exists(self, mock_io: MagicMock) -> None:
        """Verify get_current returns None if file doesn't exist."""
        mock_io.exists.return_value = False
        repo = MarkdownPipelineRepository(mock_io)

        assert repo.get_current() is None

    def test_round_trip_preserves_aggregate_state(self, mock_io: MagicMock) -> None:
        """TC-BOOT-006: save then get_current rehydrates id, position, status, gate and stages."""
        pipeline = Pipeline(pipeline_id="self-bootstrap")
        pipeline.start()
        pipeline.record_gate(GateDecision.PASS)
        pipeline.increment_stage_iteration()
        pipeline.advance()

        restored = self._round_trip(mock_io, pipeline)

        assert restored is not None
        assert restored.pipeline_id == "self-bootstrap"
        assert restored.current_position == "phase1"
        assert restored.status == PipelineStatus.RUNNING
        assert restored.last_gate_decision == GateDecision.PASS
        assert restored.stages["phase0"].status == StageStatus.PASSED
        assert restored.stages["phase0"].iteration_count == 1
        assert restored.stages["phase1"].status == StageStatus.PENDING

    def test_get_by_id_matches_persisted_pipeline(self, mock_io: MagicMock) -> None:
        """TC-BOOT-007: get_by_id resolves the persisted id and rejects others."""
        repo = MarkdownPipelineRepository(mock_io)
        repo.save(Pipeline(pipeline_id="self-bootstrap"))
        written = mock_io.write.call_args[0][1]
        mock_io.exists.return_value = True
        mock_io.read.return_value = written

        assert repo.get_by_id("self-bootstrap") is not None
        assert repo.get_by_id("other") is None

    def test_get_current_degrades_to_none_on_human_document(self, mock_io: MagicMock) -> None:
        """TC-BOOT-008: A human-authored state document without machine fields yields None."""
        mock_io.exists.return_value = True
        mock_io.read.return_value = "# Workflow State — Unified Agentic Workflow System\n\n**Pipeline Position**: X\n"
        repo = MarkdownPipelineRepository(mock_io)

        assert repo.get_current() is None

    def test_get_current_degrades_to_none_on_corrupt_values(self, mock_io: MagicMock) -> None:
        """TC-BOOT-009: Unknown enum values or incomplete stage tables yield None, not exceptions."""
        mock_io.exists.return_value = True
        mock_io.read.return_value = (
            "**Pipeline ID**: x\n"
            "**Pipeline Position**: phase0\n"
            "**Pipeline Status**: exploded\n"
            "**Last Gate Decision**: none\n"
        )
        repo = MarkdownPipelineRepository(mock_io)

        assert repo.get_current() is None
