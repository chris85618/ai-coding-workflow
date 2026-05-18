"""Persistence Adapter — Filesystem TraceableID Repository.

Traceable to: FR-001, FR-018, ADR-STR-001
Storage: JSON file per ID prefix, located in {repo_root}/.agentic/ids/
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from agentic_workflow.adapters.filesystem import get_filesystem
from agentic_workflow.application.ports.repositories import TraceableIDRepository

if TYPE_CHECKING:
    from agentic_workflow.domain.entities.traceable_id import TraceableID
    from agentic_workflow.domain.value_objects import TraceLink


def _validate_safe_path(fs: Any, path: str, root: str, id_str: str) -> None:
    try:
        fs.relative_to(path, root)
    except ValueError as err:
        raise ValueError(f"Path traversal detected for ID {id_str!r} (SEC-003)") from err


def _serialize_links(links: list[Any]) -> list[dict[str, str]]:
    return [{"source_id": lk.source_id, "target_id": lk.target_id, "link_type": lk.link_type.value} for lk in links]


def _serialize_id(traceable_id: TraceableID) -> dict[str, Any]:
    return {
        "id_str": traceable_id.full_id, "prefix": traceable_id.prefix.value, "sequence": traceable_id.sequence,
        "title": traceable_id.title, "upstream_links": _serialize_links(traceable_id.upstream_links),
        "downstream_links": _serialize_links(traceable_id.downstream_links),
    }


def _deserialize_links(data: list[dict[str, str]]) -> list[TraceLink]:
    from agentic_workflow.domain.enums import LinkType
    from agentic_workflow.domain.value_objects import TraceLink

    return [
        TraceLink(source_id=lk["source_id"], target_id=lk["target_id"], link_type=LinkType(lk["link_type"]))
        for lk in data
    ]


def _deserialize_id(json_str: str) -> TraceableID:
    from agentic_workflow.domain.entities.traceable_id import TraceableID
    from agentic_workflow.domain.enums import IDPrefix

    data = json.loads(json_str)
    up, down = _deserialize_links(data.get("upstream_links", [])), _deserialize_links(data.get("downstream_links", []))
    return TraceableID(IDPrefix(data["prefix"]), data["sequence"], data.get("title", ""), up, down)


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
        _validate_safe_path(self._fs, resolved, self._root, id_str)
        return resolved

    def save(self, traceable_id: TraceableID) -> None:
        """Persist a TraceableID as JSON.

        Args:
            traceable_id: The ID object to persist.
        """
        data = _serialize_id(traceable_id)
        self._fs.write_text(self._path_for(traceable_id.full_id), json.dumps(data, indent=2), encoding="utf-8")

    def find_by_id(self, id_str: str) -> TraceableID | None:
        """Load a TraceableID from disk by its string identifier.

        Args:
            id_str: The string representation (e.g., "FR-001").

        Returns:
            The TraceableID if found, else None.
        """
        path = self._path_for(id_str)
        return _deserialize_id(self._fs.read_text(path, encoding="utf-8")) if self._fs.exists(path) else None

    def find_all(self) -> list[TraceableID]:
        """Return all persisted TraceableIDs.

        Returns:
            List of all stored IDs.
        """
        files = sorted(self._fs.glob(self._root, "*.json"))
        stems = map(lambda f: f.replace("\\", "/").split("/")[-1][:-5].replace("_", "-"), files)
        objs = map(self.find_by_id, stems)
        return list(filter(None, objs))

    def delete(self, id_str: str) -> bool:
        """Remove a TraceableID JSON file.

        Args:
            id_str: The string representation of the ID to remove.

        Returns:
            True if deleted, False if not found.
        """
        path = self._path_for(id_str)
        return self._fs.remove(path) if self._fs.exists(path) else False
