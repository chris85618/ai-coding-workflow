"""LangGraph Checkpointer Adapter — RepositoryCheckpointer.

Bridges LangGraph's BaseCheckpointSaver to our CheckpointRepository port.
Ensures LangGraph's persistence is encapsulated in a domain-aligned repository.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from langgraph.checkpoint.base import (  # type: ignore
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    SerializerProtocol,
)
from langgraph.config import RunnableConfig  # type: ignore

from agentic_workflow.application.ports.repositories import CheckpointRepository


class RepositoryCheckpointer(BaseCheckpointSaver[Any]):
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
        """Initializes the checkpointer.

        Args:
            repository: The CheckpointRepository to delegate to.
            serde: Optional serializer for state data.
        """
        super().__init__(serde=serde)
        self.repository = repository

    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        """Get a checkpoint tuple from the repository."""
        thread_id = config.get("configurable", {}).get("thread_id", "default")

        # In our current repository adapter, we simplify to latest.
        # Future enhancement: implement load_version(thread_id, checkpoint_id)
        state = self.repository.load_latest(thread_id)

        if state is None:
            return None

        # Reconstruct LangGraph CheckpointTuple
        # This requires metadata which our repository doesn't currently store explicitly.
        # We'll create a minimal one.
        checkpoint = cast_checkpoint(state.get("checkpoint", state))
        metadata = cast_metadata(state.get("metadata", {}))

        return CheckpointTuple(
            config=config,
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=state.get("parent_config"),
        )

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

        for cid in ids:
            tup = self.get_tuple({"configurable": {"thread_id": thread_id, "checkpoint_id": cid}})
            if tup:
                yield tup

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any],
    ) -> RunnableConfig:
        """Save a checkpoint to the repository."""
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        state = {
            "checkpoint": checkpoint,
            "metadata": metadata,
            "new_versions": new_versions,
        }
        self.repository.save_checkpoint(thread_id, state)
        return config


# Helper functions to satisfy type checker if needed
def cast_checkpoint(data: Any) -> Checkpoint:
    """Type cast to Checkpoint."""
    return data  # type: ignore


def cast_metadata(data: Any) -> CheckpointMetadata:
    """Type cast to CheckpointMetadata."""
    return data  # type: ignore
