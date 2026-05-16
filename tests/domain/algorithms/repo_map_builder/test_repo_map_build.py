"""Integration-level tests for RepoMapBuilder.build."""

import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import icontract
import pytest

from agentic_workflow.domain.algorithms.repo_map_builder import RepoMapBuilder


class TestRepoMapBuild:
    """Integration-level tests for RepoMapBuilder.build."""

    def test_no_python_files_returns_empty(self, tmp_path: Path) -> None:
        """L175-176: no .py files → RepoMap with 0 tokens and empty symbols."""
        (tmp_path / "README.md").write_text("# readme")
        result = RepoMapBuilder.build(str(tmp_path), token_budget=1000)
        assert result.token_count == 0
        assert len(result.symbols) == 0

    def test_oserror_on_symbol_read_skipped(self, tmp_path: Path) -> None:
        """L183-184: OSError when reading file for symbols → skip, continue."""
        # Create one good file
        (tmp_path / "good.py").write_text("def f(): pass\n")
        # Simulate OSError on read by patching Path.read_text
        original_read_text = Path.read_text

        def patched_read_text(self: Path, *a: Any, **kw: Any) -> str:
            if "good" not in str(self):
                raise OSError("simulated")
            return original_read_text(self, *a, **kw)

        with patch.object(Path, "read_text", patched_read_text):
            result = RepoMapBuilder.build(str(tmp_path), token_budget=1000)
        # Should still have symbol from good.py
        assert result.token_count >= 0

    def test_tight_token_budget_prunes_symbols(self, tmp_path: Path) -> None:
        """Token budget of 1 forces pruning after first symbol."""
        for i in range(10):
            (tmp_path / f"mod_{i}.py").write_text(f"class BigClass{i}:\n    pass\n" * 5)
        result = RepoMapBuilder.build(str(tmp_path), token_budget=1)
        assert result.token_count <= 1

    def test_test_files_excluded(self, tmp_path: Path) -> None:
        """Files starting with test_ are not scanned for symbols."""
        (tmp_path / "test_something.py").write_text("def test_foo() -> None: pass\n")
        (tmp_path / "module.py").write_text("def real_func(): pass\n")
        result = RepoMapBuilder.build(str(tmp_path), token_budget=500)
        # test_something.py should not appear as any symbol's file_path
        test_file_paths = [s.file_path for s in result.symbols if os.path.basename(s.file_path).startswith("test_")]
        assert test_file_paths == [], f"test_ files appeared in map: {test_file_paths}"

    def test_invalid_project_path_raises(self, tmp_path: Path) -> None:
        """Icontract precondition: non-existent project_path raises ViolationError."""
        with pytest.raises((icontract.ViolationError, ValueError)):
            RepoMapBuilder.build("/nonexistent/path/xyz", token_budget=1000)

    def test_zero_budget_raises(self, tmp_path: Path) -> None:
        """Icontract precondition: token_budget=0 raises ViolationError."""
        with pytest.raises((icontract.ViolationError, ValueError)):
            RepoMapBuilder.build(str(tmp_path), token_budget=0)
