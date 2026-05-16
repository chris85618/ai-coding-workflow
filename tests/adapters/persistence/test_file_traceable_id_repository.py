"""TC-128, TC-129: FileTraceableIDRepository tests."""

import pathlib
from typing import Any
from unittest.mock import patch

import pytest

from agentic_workflow.adapters.persistence.file_repository import (
    FileTraceableIDRepository,
)


class TestFileTraceableIDRepository:
    """TC-128, TC-129: Repository tests."""

    def test_file_repository_path_traversal(self, tmp_path: Any) -> None:
        """TC-128: Repository path traversal protection."""
        repo = FileTraceableIDRepository(str(tmp_path))
        with (
            patch.object(pathlib.Path, "relative_to", side_effect=ValueError),
            pytest.raises(ValueError, match="Path traversal detected"),
        ):
            repo._path_for("FR-001")

    def test_file_repository_find_all_with_none(self, tmp_path: Any) -> None:
        """TC-129: Repository find_all handling of missing files."""
        repo = FileTraceableIDRepository(str(tmp_path))
        bad_file = tmp_path / ".agentic" / "ids" / "FOO_001.json"
        bad_file.parent.mkdir(parents=True, exist_ok=True)
        bad_file.write_text("{}")

        results = repo.find_all()
        assert len(results) == 0
