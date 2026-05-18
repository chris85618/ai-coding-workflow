"""LangGraph Checkpointer Adapter — RepositoryCheckpointer.

Bridges LangGraph's BaseCheckpointSaver to our CheckpointRepository port.
Ensures LangGraph's persistence is encapsulated in a domain-aligned repository.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from langgraph.checkpoint.serde.base import SerializerProtocol

from agentic_workflow.application.ports.repositories import CheckpointRepository


class CheckpointHelperBuilder:
    """Helper builder for checkpointer state conversions."""

    @staticmethod
    def cast_checkpoint(data: Any) -> Checkpoint:
        """Type cast to Checkpoint."""
        return cast(Checkpoint, data)

    @staticmethod
    def cast_metadata(data: Any) -> CheckpointMetadata:
        """Type cast to CheckpointMetadata."""
        return cast(CheckpointMetadata, data)

    @staticmethod
    def build_tup(config: RunnableConfig, state: dict[str, Any]) -> CheckpointTuple:
        """Build a CheckpointTuple from state dict."""
        cp = CheckpointHelperBuilder.cast_checkpoint(state.get("checkpoint", state))
        md = CheckpointHelperBuilder.cast_metadata(state.get("metadata", {}))
        return CheckpointTuple(config=config, checkpoint=cp, metadata=md, parent_config=state.get("parent_config"))

    @staticmethod
    def make_tuple(config: RunnableConfig, state: dict[str, Any] | None) -> CheckpointTuple | None:
        """Make a CheckpointTuple if state exists."""
        return CheckpointHelperBuilder.build_tup(config, state) if state is not None else None

    @staticmethod
    def iter_tuples(ck: RepositoryCheckpointerMapper, tid: str, ids: list[str]) -> Iterator[CheckpointTuple]:
        """Iterate and build CheckpointTuples."""
        cfgs = map(
            lambda cid: cast(RunnableConfig, {"configurable": {"thread_id": tid, "checkpoint_id": cid}}),
            ids,
        )
        tups = map(ck.get_tuple, cfgs)
        return filter(None, tups)


class RepositoryCheckpointerMapper(BaseCheckpointSaver[Any]):
    """LangGraph Checkpointer that delegates to a CheckpointRepository.

    Allows LangGraph to persist its state through our clean architecture
    repository adapters (e.g., FileCheckpointRepository).
    """

    def __init__(
        self,
        repository: CheckpointRepository,
        *,
        serde: SerializerProtocol | None = None,
    ) -> None:
        """Initializes the checkpointer."""
        super().__init__(serde=serde)
        self.repository = repository

    def save_checkpoint(self, pipeline_id: str, state: dict[str, Any]) -> str:
        """Port implementation."""
        return self.repository.save_checkpoint(pipeline_id, state)

    def load_latest(self, pipeline_id: str) -> dict[str, Any] | None:
        """Port implementation."""
        return self.repository.load_latest(pipeline_id)

    def list_checkpoints(self, pipeline_id: str) -> list[str]:
        """Port implementation."""
        return self.repository.list_checkpoints(pipeline_id)

    def delete_checkpoint(self, pipeline_id: str, checkpoint_id: str) -> bool:
        """Port implementation."""
        return self.repository.delete_checkpoint(pipeline_id, checkpoint_id)

    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        """Get a checkpoint tuple from the repository."""
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        return CheckpointHelperBuilder.make_tuple(config, self.repository.load_latest(thread_id))

    def list(
        self,
        config: RunnableConfig | None,
        *,
        filter: dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> Iterator[CheckpointTuple]:
        """List checkpoints from the repository."""
        thread_id = (config or {}).get("configurable", {}).get("thread_id", "default")
        ids = self.repository.list_checkpoints(thread_id)
        return CheckpointHelperBuilder.iter_tuples(self, thread_id, ids)

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any],
    ) -> RunnableConfig:
        """Save a checkpoint to the repository."""
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        payload = {"checkpoint": checkpoint, "metadata": metadata, "new_versions": new_versions}
        self.repository.save_checkpoint(thread_id, payload)
        return config


RepositoryCheckpointer = RepositoryCheckpointerMapper
