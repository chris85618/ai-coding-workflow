"""Tests for RepositoryCheckpointer adapter."""

from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import Checkpoint, CheckpointMetadata

from agentic_workflow.application.ports.repositories.checkpoint_repository import CheckpointRepository
from agentic_workflow.frameworks.langgraph.checkpointer import RepositoryCheckpointer


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

    def test_direct_save_checkpoint(self, checkpointer: RepositoryCheckpointer, mock_repo: MagicMock) -> None:
        """Call save_checkpoint directly."""
        mock_repo.save_checkpoint.return_value = "saved_id"
        res = checkpointer.save_checkpoint("t1", {"x": 1})
        assert res == "saved_id"
        mock_repo.save_checkpoint.assert_called_once_with("t1", {"x": 1})

    def test_direct_load_latest(self, checkpointer: RepositoryCheckpointer, mock_repo: MagicMock) -> None:
        """Call load_latest directly."""
        mock_repo.load_latest.return_value = {"x": 2}
        res = checkpointer.load_latest("t1")
        assert res == {"x": 2}
        mock_repo.load_latest.assert_called_once_with("t1")

    def test_direct_list_checkpoints(self, checkpointer: RepositoryCheckpointer, mock_repo: MagicMock) -> None:
        """Call list_checkpoints directly."""
        mock_repo.list_checkpoints.return_value = ["c1"]
        res = checkpointer.list_checkpoints("t1")
        assert res == ["c1"]
        mock_repo.list_checkpoints.assert_called_once_with("t1")

    def test_direct_delete_checkpoint(self, checkpointer: RepositoryCheckpointer, mock_repo: MagicMock) -> None:
        """Call delete_checkpoint directly."""
        mock_repo.delete_checkpoint.return_value = True
        res = checkpointer.delete_checkpoint("t1", "c1")
        assert res is True
        mock_repo.delete_checkpoint.assert_called_once_with("t1", "c1")
