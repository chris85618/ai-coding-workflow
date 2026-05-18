"""Filesystem-backed TraceableID Repository."""

from __future__ import annotations

import json
from typing import Any

from agentic_workflow.adapters.filesystem import get_filesystem
from agentic_workflow.application.ports.repositories import TraceableIDRepository
from agentic_workflow.domain.entities.traceable_id import TraceableID
from agentic_workflow.domain.enums import IDPrefix
from agentic_workflow.domain.enums.link_type import LinkType
from agentic_workflow.domain.value_objects.trace_link import TraceLink


class FileTraceableIDRepositoryMapper(TraceableIDRepository):
    """Filesystem-backed TraceableID repository.

    Each TraceableID is stored as a JSON file named ``{id_str}.json``
    inside ``{root}/.agentic/ids/``.
    """

    def __init__(self, repo_root: str = ".") -> None:
        """Initialize the repository at .agentic/ids relative to repo_root."""
        self._fs = get_filesystem()
        self._root = self._fs.resolve_path(self._fs.resolve_path(repo_root) + "/.agentic/ids")
        self._fs.mkdir(self._root, parents=True, exist_ok=True)

    def _check_traversal(self, resolved: str) -> None:
        """Check for path traversal."""
        try:
            self._fs.relative_to(resolved, self._root)
        except ValueError as exc:
            raise ValueError("Path traversal detected") from exc

    def _path_for(self, id_str: str) -> str:
        """Return safe storage path for an ID string."""
        safe = id_str.replace("/", "_").replace("\\", "_").replace("..", "__")
        resolved = self._fs.resolve_path(self._root + f"/{safe}.json")
        self._check_traversal(resolved)
        return resolved

    @staticmethod
    def _serialize_links(links: list[TraceLink]) -> list[dict[str, str]]:
        """Serialize trace links."""
        return [{"source_id": lk.source_id, "target_id": lk.target_id, "link_type": lk.link_type.value} for lk in links]

    @staticmethod
    def _deserialize_links(data: list[dict[str, str]]) -> list[TraceLink]:
        """Deserialize trace links."""
        return [
            TraceLink(source_id=lk["source_id"], target_id=lk["target_id"], link_type=LinkType(lk["link_type"]))
            for lk in data
        ]

    def _to_dict(self, t_id: TraceableID) -> dict[str, Any]:
        """Convert TraceableID to dict."""
        k = ["id_str", "prefix", "sequence", "title", "upstream_links", "downstream_links"]
        v = [t_id.full_id, t_id.prefix.value, t_id.sequence, t_id.title, self._serialize_links(t_id.upstream_links), self._serialize_links(t_id.downstream_links)]  # fmt: skip # noqa: E501
        return dict(zip(k, v, strict=True))

    def _from_dict(self, data: dict[str, Any]) -> TraceableID:
        """Construct TraceableID from dict."""
        up, down = data.get("upstream_links", []), data.get("downstream_links", [])
        return TraceableID(prefix=IDPrefix(data["prefix"]), sequence=data["sequence"], title=data.get("title", ""), upstream_links=self._deserialize_links(up), downstream_links=self._deserialize_links(down))  # fmt: skip # noqa: E501

    def save(self, traceable_id: TraceableID) -> None:
        """Persist a TraceableID as JSON."""
        data = self._to_dict(traceable_id)
        self._fs.write_text(self._path_for(traceable_id.full_id), json.dumps(data, indent=2), encoding="utf-8")

    def find_by_id(self, id_str: str) -> TraceableID | None:
        """Load a TraceableID from disk by its string identifier."""
        path = self._path_for(id_str)
        if not self._fs.exists(path):
            res: TraceableID | None = None
        else:
            res = self._from_dict(json.loads(self._fs.read_text(path, encoding="utf-8")))
        return res

    def find_all(self) -> list[TraceableID]:
        """Return all persisted TraceableIDs."""
        files = sorted(self._fs.glob(self._root, "*.json"))
        return [obj for f in files if (
            obj := self.find_by_id(f.replace("\\", "/").split("/")[-1][:-5].replace("_", "-"))
        ) is not None]

    def delete(self, id_str: str) -> bool:
        """Remove a TraceableID JSON file."""
        path = self._path_for(id_str)
        return self._fs.remove(path) if self._fs.exists(path) else False


FileTraceableIDRepository = FileTraceableIDRepositoryMapper
