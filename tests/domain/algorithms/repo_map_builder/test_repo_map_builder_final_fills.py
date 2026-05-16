"""Cover final edge cases in RepoMapBuilder."""

from pathlib import Path
from typing import Any
from unittest.mock import patch

from agentic_workflow.domain.algorithms.repo_map_builder import RepoMapBuilder


class TestRepoMapBuilderFinalFills:
    """Cover final edge cases in RepoMapBuilder."""

    def test_import_graph_none_module_group(self, tmp_path: Path) -> None:
        """Import an external module (not in path_map) to exercise module falsy paths."""
        a = tmp_path / "alpha.py"
        a.write_text("import os\nimport sys\nfrom pathlib import Path\n")
        result = RepoMapBuilder.build_import_graph([str(a)], str(tmp_path))
        assert result[str(a)] == []

    def test_repo_map_build_oserror_on_second_read(self, tmp_path: Path) -> None:
        """OSError during symbol-extraction read ->file is skipped."""
        good_file = tmp_path / "good.py"
        bad_file = tmp_path / "bad.py"
        good_file.write_text("def good_func(): pass\n")
        bad_file.write_text("class BadClass: pass\n")

        call_registry: dict[str, int] = {}
        original_read_text = Path.read_text

        def patched_read(self: Path, *args: Any, **kwargs: Any) -> str:
            name = self.name
            call_registry[name] = call_registry.get(name, 0) + 1
            if name == "bad.py" and call_registry[name] == 1:
                raise OSError("forced OSError for L183-184 coverage")
            return original_read_text(self, *args, **kwargs)

        with patch.object(Path, "read_text", patched_read):
            result = RepoMapBuilder.build(str(tmp_path), token_budget=1000)

        good_syms = [s for s in result.symbols if "good" in s.file_path]
        bad_syms = [s for s in result.symbols if "bad" in s.file_path]
        assert len(good_syms) >= 1
        assert bad_syms == []
        assert call_registry.get("bad.py", 0) >= 1
