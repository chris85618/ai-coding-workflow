"""Unit tests for MarkdownPipelineRepository."""

from unittest.mock import MagicMock

import pytest

from agentic_workflow.adapters.persistence.markdown_pipeline_repository import MarkdownPipelineRepository
from agentic_workflow.application.ports.doc_io.document_io_gateway import DocumentIOGateway
from agentic_workflow.domain.aggregates.pipeline import Pipeline


class TestMarkdownPipelineRepository:
    """Test suite for MarkdownPipelineRepository."""

    @pytest.fixture
    def mock_io(self) -> MagicMock:
        """Create a mock document IO gateway."""
        return MagicMock(spec=DocumentIOGateway)

    def test_save(self, mock_io: MagicMock) -> None:
        """Verify saving a pipeline writes to the correct path."""
        repo = MarkdownPipelineRepository(mock_io)
        pipeline = Pipeline(pipeline_id="test-save")

        repo.save(pipeline)

        mock_io.write.assert_called_once()
        args = mock_io.write.call_args[0]
        assert "docs/workflow-state.md" in args[0]
        assert "test-save" in args[1]

    def test_get_current_not_exists(self, mock_io: MagicMock) -> None:
        """Verify get_current returns None if file doesn't exist."""
        mock_io.exists.return_value = False
        repo = MarkdownPipelineRepository(mock_io)

        result = repo.get_current()
        assert result is None

    def test_get_current_exists(self, mock_io: MagicMock) -> None:
        """Verify get_current returns a Pipeline if file exists."""
        mock_io.exists.return_value = True
        repo = MarkdownPipelineRepository(mock_io)

        result = repo.get_current()
        assert isinstance(result, Pipeline)
        assert result.pipeline_id == "agentic-workflow-default"

    def test_get_by_id(self, mock_io: MagicMock) -> None:
        """Verify get_by_id logic."""
        mock_io.exists.return_value = True
        repo = MarkdownPipelineRepository(mock_io)

        # Matches default id in stub
        result = repo.get_by_id("agentic-workflow-default")
        assert result is not None

        # Mismatch
        result = repo.get_by_id("other")
        assert result is None
