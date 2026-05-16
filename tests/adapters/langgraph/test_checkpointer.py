"""Tests for RepositoryCheckpointer adapter."""

from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from langgraph.checkpoint.base import Checkpoint, CheckpointMetadata
from langgraph.config import RunnableConfig  # type: ignore

from agentic_workflow.adapters.langgraph.checkpointer import RepositoryCheckpointer
from agentic_workflow.application.ports.repositories.checkpoint_repository import CheckpointRepository


class TestRepositoryCheckpointer:
    """Covers RepositoryCheckpointer adapter logic."""

    @pytest.fixture
    def mock_repo(self) -> MagicMock:
        """Fixture for mock repository."""
        return MagicMock(spec=CheckpointRepository)

    @pytest.fixture
    def checkpointer(self, mock_repo: MagicMock) -> RepositoryCheckpointer:
        """Fixture for checkpointer adapter."""
        return RepositoryCheckpointer(repository=mock_repo)

    def test_get_tuple_found(self, checkpointer: RepositoryCheckpointer, mock_repo: MagicMock) -> None:
        """Loads checkpoint from repository."""
        mock_repo.load_latest.return_value = {"checkpoint": {"v": 1}, "metadata": {"m": 1}}
        config = cast(RunnableConfig, {"configurable": {"thread_id": "t1"}})
        tup = checkpointer.get_tuple(config)

        assert tup is not None
        assert cast(dict[str, Any], tup.checkpoint) == {"v": 1}
        assert cast(dict[str, Any], tup.metadata) == {"m": 1}

    def test_get_tuple_not_found(self, checkpointer: RepositoryCheckpointer, mock_repo: MagicMock) -> None:
        """Returns None if not found."""
        mock_repo.load_latest.return_value = None
        config = cast(RunnableConfig, {"configurable": {"thread_id": "missing"}})
        assert checkpointer.get_tuple(config) is None

    def test_put(self, checkpointer: RepositoryCheckpointer, mock_repo: MagicMock) -> None:
        """Saves checkpoint to repository."""
        config = cast(RunnableConfig, {"configurable": {"thread_id": "t1"}})
        checkpoint = cast(Checkpoint, {"v": 2})
        metadata = cast(CheckpointMetadata, {"m": 2})

        result_config = checkpointer.put(config, checkpoint, metadata, {})

        assert result_config == config
        mock_repo.save_checkpoint.assert_called_once()
        args = mock_repo.save_checkpoint.call_args[0]
        assert args[0] == "t1"
        assert args[1]["checkpoint"] == checkpoint

    def test_list(self, checkpointer: RepositoryCheckpointer, mock_repo: MagicMock) -> None:
        """Lists checkpoints from repository."""
        mock_repo.list_checkpoints.return_value = ["c1", "c2"]
        # get_tuple will be called for each ID
        mock_repo.load_latest.return_value = {"checkpoint": {}}

        config = cast(RunnableConfig, {"configurable": {"thread_id": "t1"}})
        items = list(checkpointer.list(config))

        assert len(items) == 2
        assert mock_repo.list_checkpoints.called

    def test_list_with_missing(self, checkpointer: RepositoryCheckpointer, mock_repo: MagicMock) -> None:
        """Lists checkpoints and skips missing ones."""
        mock_repo.list_checkpoints.return_value = ["c1", "c2"]
        # Return something for c1, None for c2
        mock_repo.load_latest.side_effect = [{"checkpoint": {}}, None]

        config = cast(RunnableConfig, {"configurable": {"thread_id": "t1"}})
        items = list(checkpointer.list(config))

        assert len(items) == 1
        assert mock_repo.load_latest.call_count == 2
