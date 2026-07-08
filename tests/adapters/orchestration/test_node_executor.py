"""Tests for the single-node executor (FR-077, FR-078, ADR-STR-033)."""

from typing import Any
from unittest.mock import patch

import pytest

from agentic_workflow.adapters.orchestration import node_registry
from agentic_workflow.adapters.orchestration.node_executor import NodeExecutor
from agentic_workflow.adapters.orchestration.state_mapper import WorkflowState
from agentic_workflow.application.ports.repositories.checkpoint_repository import (
    CheckpointRepository,
)


class InMemoryCheckpointRepository(CheckpointRepository):
    """In-memory checkpoint repository double."""

    def __init__(self) -> None:
        """Initialize the empty checkpoint store."""
        self.store: dict[str, dict[str, Any]] = {}

    def save_checkpoint(self, pipeline_id: str, state: dict[str, Any]) -> str:
        """Save the state as the latest checkpoint for pipeline_id."""
        self.store[pipeline_id] = state
        return "ckpt-1"

    def load_latest(self, pipeline_id: str) -> dict[str, Any] | None:
        """Load the latest checkpoint for pipeline_id."""
        return self.store.get(pipeline_id)

    def list_checkpoints(self, pipeline_id: str) -> list[str]:
        """List checkpoint identifiers for pipeline_id."""
        return ["ckpt-1"] if pipeline_id in self.store else []

    def delete_checkpoint(self, pipeline_id: str, checkpoint_id: str) -> bool:
        """Delete the checkpoint for pipeline_id."""
        return self.store.pop(pipeline_id, None) is not None


def fake_node(state: WorkflowState) -> WorkflowState:
    """Return a partial state update recording the node execution."""
    return WorkflowState(pipeline_status="running", metadata={"seen": state.get("pipeline_id", "")})


def fake_router(state: WorkflowState) -> str:
    """Route based on the checkpointed state without mutating it."""
    return "left" if state.get("pipeline_status") == "running" else "right"


class TestNodeExecutor:
    """Covers TC-ARCHON-009~012: one node per invocation, no sequencing."""

    def test_state_node_seeds_fresh_state_and_persists(self) -> None:
        """TC-ARCHON-009: With no prior checkpoint the executor seeds state and persists the merge."""
        repo = InMemoryCheckpointRepository()
        executor = NodeExecutor(repo)
        with patch.dict(node_registry.NODE_REGISTRY, {"fake": fake_node}):
            route = executor.execute("p1", "fake")
        assert route == ""
        saved = repo.store["p1"]
        assert saved["pipeline_id"] == "p1"
        assert saved["pipeline_status"] == "running"
        assert saved["metadata"] == {"seen": "p1"}

    def test_state_node_loads_existing_checkpoint(self) -> None:
        """TC-ARCHON-010: An existing checkpoint is loaded and merged with the node update."""
        repo = InMemoryCheckpointRepository()
        repo.store["p2"] = {"pipeline_id": "p2", "iteration_count": 3}
        executor = NodeExecutor(repo)
        with patch.dict(node_registry.NODE_REGISTRY, {"fake": fake_node}):
            executor.execute("p2", "fake")
        saved = repo.store["p2"]
        assert saved["iteration_count"] == 3
        assert saved["pipeline_status"] == "running"

    def test_router_returns_route_without_persisting(self) -> None:
        """TC-ARCHON-011: Router nodes print their route and never mutate the checkpoint."""
        repo = InMemoryCheckpointRepository()
        repo.store["p3"] = {"pipeline_id": "p3", "pipeline_status": "running"}
        executor = NodeExecutor(repo)
        with patch.dict(node_registry.ROUTER_REGISTRY, {"fake_route": fake_router}):
            route = executor.execute("p3", "fake_route")
        assert route == "left"
        assert repo.store["p3"] == {"pipeline_id": "p3", "pipeline_status": "running"}

    def test_unknown_node_raises_key_error(self) -> None:
        """TC-ARCHON-012: Unregistered node names fail loudly."""
        executor = NodeExecutor(InMemoryCheckpointRepository())
        with pytest.raises(KeyError, match="Unknown workflow node"):
            executor.execute("p4", "no_such_node")

    def test_container_provides_node_executor(self) -> None:
        """TC-ARCHON-021: DependencyContainer.node_executor wires the checkpoint repository."""
        from unittest.mock import MagicMock

        from agentic_workflow.frameworks.dependency_container import DependencyContainer

        container = DependencyContainer(
            pipeline_repo=MagicMock(),
            checkpoint_repo=InMemoryCheckpointRepository(),
            doc_io=MagicMock(),
            reasoner=MagicMock(),
        )
        assert isinstance(container.node_executor, NodeExecutor)
