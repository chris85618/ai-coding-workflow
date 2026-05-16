"""Persistence Adapter — LangGraph Checkpoint Repository.

Implements: CheckpointRepository port
Traceable to: FR-019-v2, FR-021-v2, UC-010 (workflow resume), ADR-STR-003
Storage: JSON files in {repo_root}/.agentic/checkpoints/{pipeline_id}/
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from agentic_workflow.application.ports.repositories import CheckpointRepository


class FileCheckpointRepository(CheckpointRepository):
    """Filesystem-backed LangGraph checkpoint repository.

    Checkpoints are stored as timestamped JSON files:
        ``.agentic/checkpoints/{pipeline_id}/{timestamp}.json``

    The latest checkpoint is the file with the lexicographically greatest
    name (ISO 8601 timestamps sort correctly).

    Args:
        repo_root: Path to the repository root directory.
    """

    def __init__(self, repo_root: str = ".") -> None:
        """Initializes the checkpoint repository.

        Args:
            repo_root: Path to the repository root directory.
        """
        self._root = Path(repo_root) / ".agentic" / "checkpoints"
        self._root.mkdir(parents=True, exist_ok=True)

    def _pipeline_dir(self, pipeline_id: str) -> Path:
        safe = pipeline_id.replace("/", "_").replace("\\", "_")
        d = self._root / safe
        d.mkdir(parents=True, exist_ok=True)
        return d

    def save_checkpoint(self, pipeline_id: str, state: dict[str, Any]) -> str:
        """Save a pipeline checkpoint JSON file.

        Args:
            pipeline_id: Identifier for the pipeline being checkpointed.
            state: LangGraph state dictionary to persist.

        Returns:
            Checkpoint identifier (ISO 8601 UTC timestamp string).
        """
        checkpoint_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        path = self._pipeline_dir(pipeline_id) / f"{checkpoint_id}.json"
        path.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
        return checkpoint_id

    def load_latest(self, pipeline_id: str) -> dict[str, Any] | None:
        """Load the most recent checkpoint for a pipeline.

        Args:
            pipeline_id: Identifier for the pipeline to restore.

        Returns:
            State dictionary if a checkpoint exists, else None.
        """
        d = self._pipeline_dir(pipeline_id)
        checkpoints = sorted(d.glob("*.json"), reverse=True)
        if not checkpoints:
            return None
        return cast("dict[str, Any]", json.loads(checkpoints[0].read_text(encoding="utf-8")))

    def list_checkpoints(self, pipeline_id: str) -> list[str]:
        """List checkpoint identifiers newest first.

        Args:
            pipeline_id: Identifier for the target pipeline.

        Returns:
            List of checkpoint identifier strings.
        """
        d = self._pipeline_dir(pipeline_id)
        return [f.stem for f in sorted(d.glob("*.json"), reverse=True)]

    def delete_checkpoint(self, pipeline_id: str, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint file.

        Args:
            pipeline_id: Pipeline identifier.
            checkpoint_id: Checkpoint identifier to delete.

        Returns:
            True if deleted, False if not found.
        """
        path = self._pipeline_dir(pipeline_id) / f"{checkpoint_id}.json"
        if path.exists():
            os.remove(path)
            return True
        return False
