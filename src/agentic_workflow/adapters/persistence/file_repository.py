"""Persistence Adapter — Filesystem TraceableID Repository.

Implements: TraceableIDRepository port
Traceable to: FR-001, FR-018, ADR-STR-001
Storage: JSON file per ID prefix, located in {repo_root}/.agentic/ids/
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from agentic_workflow.adapters.filesystem import get_filesystem
from agentic_workflow.application.ports.repositories import TraceableIDRepository

if TYPE_CHECKING:
    from agentic_workflow.domain.entities.traceable_id import TraceableID


class FileTraceableIDRepository(TraceableIDRepository):
    """Filesystem-backed TraceableID repository.

    Each TraceableID is stored as a JSON file named ``{id_str}.json``
    inside ``{root}/.agentic/ids/``.

    Example file path: ``.agentic/ids/FR-001.json``

    Args:
        repo_root: Path to the repository root directory.
    """

    def __init__(self, repo_root: str = ".") -> None:
        """Initialize the repository at .agentic/ids relative to repo_root."""
        self._fs = get_filesystem()
        self._root = self._fs.resolve_path(self._fs.resolve_path(repo_root) + "/.agentic/ids")
        self._fs.mkdir(self._root, parents=True, exist_ok=True)

    def _path_for(self, id_str: str) -> str:
        """Return safe storage path for an ID string.

        Raises:
            ValueError: If the resolved path escapes the storage root (SEC-003).
        """
        safe = id_str.replace("/", "_").replace("\\", "_").replace("..", "__")
        resolved = self._fs.resolve_path(self._root + f"/{safe}.json")
        try:
            self._fs.relative_to(resolved, self._root)
        except ValueError as err:
            raise ValueError(f"Path traversal detected for ID {id_str!r} (SEC-003)") from err
        return resolved

    def save(self, traceable_id: TraceableID) -> None:
        """Persist a TraceableID as JSON.

        Args:
            traceable_id: The ID object to persist.
        """
        data = {
            "id_str": traceable_id.full_id,
            "prefix": traceable_id.prefix.value,
            "sequence": traceable_id.sequence,
            "title": traceable_id.title,
            "upstream_links": [
                {
                    "source_id": link.source_id,
                    "target_id": link.target_id,
                    "link_type": link.link_type.value,
                }
                for link in traceable_id.upstream_links
            ],
            "downstream_links": [
                {
                    "source_id": link.source_id,
                    "target_id": link.target_id,
                    "link_type": link.link_type.value,
                }
                for link in traceable_id.downstream_links
            ],
        }
        path = self._path_for(traceable_id.full_id)
        self._fs.write_text(path, json.dumps(data, indent=2), encoding="utf-8")

    def find_by_id(self, id_str: str) -> TraceableID | None:
        """Load a TraceableID from disk by its string identifier.

        Args:
            id_str: The string representation (e.g., "FR-001").

        Returns:
            The TraceableID if found, else None.
        """
        from agentic_workflow.domain.entities.traceable_id import TraceableID
        from agentic_workflow.domain.enums import IDPrefix, LinkType
        from agentic_workflow.domain.value_objects import TraceLink

        path = self._path_for(id_str)
        if not self._fs.exists(path):
            return None
        data = json.loads(self._fs.read_text(path, encoding="utf-8"))
        upstream_links = [
            TraceLink(
                source_id=lk["source_id"],
                target_id=lk["target_id"],
                link_type=LinkType(lk["link_type"]),
            )
            for lk in data.get("upstream_links", [])
        ]
        downstream_links = [
            TraceLink(
                source_id=lk["source_id"],
                target_id=lk["target_id"],
                link_type=LinkType(lk["link_type"]),
            )
            for lk in data.get("downstream_links", [])
        ]
        return TraceableID(
            prefix=IDPrefix(data["prefix"]),
            sequence=data["sequence"],
            title=data.get("title", ""),
            upstream_links=upstream_links,
            downstream_links=downstream_links,
        )

    def find_all(self) -> list[TraceableID]:
        """Return all persisted TraceableIDs.

        Returns:
            List of all stored IDs.
        """
        results = []
        # glob returns relative to self._root as list of strings
        for json_file in sorted(self._fs.glob(self._root, "*.json")):
            # Extract stem (e.g. FR-001.json → FR-001)
            file_name = json_file.replace("\\", "/").split("/")[-1]
            stem = file_name[:-5].replace("_", "-")
            obj = self.find_by_id(stem)
            if obj is not None:
                results.append(obj)
        return results

    def delete(self, id_str: str) -> bool:
        """Remove a TraceableID JSON file.

        Args:
            id_str: The string representation of the ID to remove.

        Returns:
            True if deleted, False if not found.
        """
        path = self._path_for(id_str)
        if self._fs.exists(path):
            return self._fs.remove(path)
        return False
