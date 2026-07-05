"""Filesystem-backed LangGraph checkpoint repository mapper and implementation."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, cast

from agentic_workflow.adapters.filesystem import get_filesystem
from agentic_workflow.application.ports.repositories import CheckpointRepository


class CheckpointRepositoryMapper:
    """Helper mapper for checkpoint repository."""

    @staticmethod
    def read_checkpoint(fs: Any, directory: str, filename: str) -> dict[str, Any]:
        """Read checkpoint data from a file."""
        full_path = fs.resolve_path(directory + f"/{filename}")
        return cast("dict[str, Any]", json.loads(fs.read_text(full_path, encoding="utf-8")))

    @staticmethod
    def get_pipeline_dir(fs: Any, root: str, pipeline_id: str) -> str:
        """Get or create the pipeline checkpoint directory path."""
        safe = pipeline_id.replace("/", "_").replace("\\", "_")
        d = root + f"/{safe}"
        fs.mkdir(d, parents=True, exist_ok=True)
        return d


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
        self._fs = get_filesystem()
        self._root = self._fs.resolve_path(self._fs.resolve_path(repo_root) + "/.agentic/checkpoints")
        self._fs.mkdir(self._root, parents=True, exist_ok=True)

    def save_checkpoint(self, pipeline_id: str, state: dict[str, Any]) -> str:
        """Save a pipeline checkpoint JSON file.

        Args:
            pipeline_id: Identifier for the pipeline being checkpointed.
            state: LangGraph state dictionary to persist.

        Returns:
            Checkpoint identifier (ISO 8601 UTC timestamp string).
        """
        utc = UTC
        checkpoint_id = datetime.now(utc).strftime("%Y%m%dT%H%M%S%fZ")
        d = CheckpointRepositoryMapper.get_pipeline_dir(self._fs, self._root, pipeline_id)
        path = d + f"/{checkpoint_id}.json"
        self._fs.write_text(path, json.dumps(state, indent=2, default=str), encoding="utf-8")
        return checkpoint_id

    def load_latest(self, pipeline_id: str) -> dict[str, Any] | None:
        """Load the most recent checkpoint for a pipeline.

        Args:
            pipeline_id: Identifier for the pipeline to restore.

        Returns:
            State dictionary if a checkpoint exists, else None.
        """
        d = CheckpointRepositoryMapper.get_pipeline_dir(self._fs, self._root, pipeline_id)
        cps = sorted(self._fs.glob(d, "*.json"), reverse=True)
        return CheckpointRepositoryMapper.read_checkpoint(self._fs, d, cps[0]) if cps else None

    def list_checkpoints(self, pipeline_id: str) -> list[str]:
        """List checkpoint identifiers newest first.

        Args:
            pipeline_id: Identifier for the target pipeline.

        Returns:
            List of checkpoint identifier strings.
        """
        d = CheckpointRepositoryMapper.get_pipeline_dir(self._fs, self._root, pipeline_id)
        files = sorted(self._fs.glob(d, "*.json"), reverse=True)
        return [f.replace("\\", "/").split("/")[-1][:-5] for f in files]

    def delete_checkpoint(self, pipeline_id: str, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint file.

        Args:
            pipeline_id: Pipeline identifier.
            checkpoint_id: Checkpoint identifier to delete.

        Returns:
            True if deleted, False if not found.
        """
        d = CheckpointRepositoryMapper.get_pipeline_dir(self._fs, self._root, pipeline_id)
        path = d + f"/{checkpoint_id}.json"
        return self._fs.remove(path) if self._fs.exists(path) else False
