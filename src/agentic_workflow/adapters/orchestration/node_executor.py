"""Orchestration Adapter — Single-Node Executor.

Traceable to: FR-077, FR-078, ADR-STR-033
Executes exactly one workflow node per invocation: load the latest
checkpointed state, apply the named node function, persist the merged
state. Router nodes return their route string without mutating state.
No sequencing lives here — the exported Archon workflow document is the
only orchestration authority (ADR-STR-033).
"""

from __future__ import annotations

from typing import cast

from agentic_workflow.adapters.orchestration.node_registry import (
    NODE_REGISTRY,
    ROUTER_REGISTRY,
)
from agentic_workflow.adapters.orchestration.state_mapper import WorkflowState
from agentic_workflow.application.ports.repositories.checkpoint_repository import (
    CheckpointRepository,
)


class NodeExecutor:
    """Runs one named node against the checkpointed pipeline state."""

    def __init__(self, checkpoint_repo: CheckpointRepository) -> None:
        """Bind the executor to a checkpoint repository."""
        self._checkpoints = checkpoint_repo

    def _load_state(self, pipeline_id: str) -> WorkflowState:
        """Load the latest checkpoint or seed a fresh state."""
        stored = self._checkpoints.load_latest(pipeline_id)
        if stored is None:
            return WorkflowState(pipeline_id=pipeline_id)
        return cast(WorkflowState, stored)

    def execute(self, pipeline_id: str, node_name: str) -> str:
        """Execute one node; return the route string ("" for state nodes).

        Raises:
            KeyError: If node_name is not a registered node or router.
        """
        routers = ROUTER_REGISTRY
        nodes = NODE_REGISTRY
        state = self._load_state(pipeline_id)
        router = routers.get(node_name)
        if router is not None:
            return router(state)
        node = nodes.get(node_name)
        if node is None:
            raise KeyError(f"Unknown workflow node: {node_name}")
        update = node(state)
        state.update(update)
        self._checkpoints.save_checkpoint(pipeline_id, dict(state))
        return ""
