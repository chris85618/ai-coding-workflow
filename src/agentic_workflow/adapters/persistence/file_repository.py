"""Persistence Adapter — Filesystem TraceableID Repository.

Implements: TraceableIDRepository port
Traceable to: FR-001, FR-018, ADR-STR-001
Storage: JSON file per ID prefix, located in {repo_root}/.agentic/ids/
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from agentic_workflow.application.ports.repositories import TraceableIDRepository

if TYPE_CHECKING:
    from agentic_workflow.domain.models.traceable_id import TraceableID


class FileTraceableIDRepository(TraceableIDRepository):
    """Filesystem-backed TraceableID repository.

    Each TraceableID is stored as a JSON file named ``{id_str}.json``
    inside ``{root}/.agentic/ids/``.

    Example file path: ``.agentic/ids/FR-001.json``

    Args:
        repo_root: Path to the repository root directory.
    """

    def __init__(self, repo_root: str = ".") -> None:
        self._root = Path(repo_root) / ".agentic" / "ids"
        self._root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, id_str: str) -> Path:
        """Return safe storage path for an ID string.

        Raises:
            ValueError: If the resolved path escapes the storage root (SEC-003).
        """
        safe = id_str.replace("/", "_").replace("\\", "_").replace("..", "__")
        resolved = (self._root / f"{safe}.json").resolve()
        try:
            resolved.relative_to(self._root.resolve())
        except ValueError:
            raise ValueError(
                f"Path traversal detected for ID {id_str!r} (SEC-003)"
            )
        return resolved

    def save(self, traceable_id: "TraceableID") -> None:
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
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def find_by_id(self, id_str: str) -> "TraceableID | None":
        """Load a TraceableID from disk by its string identifier.

        Args:
            id_str: The string representation (e.g., "FR-001").

        Returns:
            The TraceableID if found, else None.
        """
        from agentic_workflow.domain.models.traceable_id import TraceableID, TraceLink
        from agentic_workflow.domain.models.enums import IDPrefix, LinkType

        path = self._path_for(id_str)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
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

    def find_all(self) -> list["TraceableID"]:
        """Return all persisted TraceableIDs.

        Returns:
            List of all stored IDs.
        """
        results = []
        for json_file in sorted(self._root.glob("*.json")):
            # Reconstruct id_str from filename (e.g. FR-001.json → FR-001)
            stem = json_file.stem.replace("_", "-")
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
        if path.exists():
            os.remove(path)
            return True
        return False
