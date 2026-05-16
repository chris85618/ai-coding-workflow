"""BDD step definitions for atomic_git_commits.feature (SC-015)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when


@dataclass
class CommitResult:
    """Result of a git commit operation."""

    committed: bool
    message: str
    files: list[str]


@dataclass
class FakeMCPGateway:
    """Test double for MCPGateway, recording commit calls."""

    commits: list[CommitResult] = field(default_factory=list)
    _staged_files: list[str] = field(default_factory=list)

    def stage_changes(self, files: list[str]) -> None:
        """Stage files for commit."""
        self._staged_files = list(files)

    def auto_commit(self, directory: str, message: str, files: list[str]) -> CommitResult:
        """Simulate atomic git commit. Returns CommitResult."""
        if not files:
            return CommitResult(committed=False, message="", files=[])
        result = CommitResult(committed=True, message=message, files=list(files))
        self.commits.append(result)
        return result


class TestAtomicGitCommitsScenarios:
    """BDD scenarios for atomic git commits."""

    @staticmethod
    @scenario("features/atomic_git_commits.feature", "Stage completion triggers atomic git commit")
    def test_stage_completion_commits() -> None:
        """SC-015: Stage completion auto-commits."""

    @staticmethod
    @scenario("features/atomic_git_commits.feature", "No changes means no commit")
    def test_no_changes_no_commit() -> None:
        """SC-015: No changes → no commit."""

    @staticmethod
    @scenario("features/atomic_git_commits.feature", "Commit includes all stage files atomically")
    def test_all_files_in_one_commit() -> None:
        """SC-015: All stage files in single commit."""


@pytest.fixture
def ctx() -> dict[str, Any]:
    """Shared step context."""
    return {"gateway": FakeMCPGateway()}


@given(parsers.parse("Stage {n:d} has completed with updated artifacts in docs/"))
def given_stage_completed(ctx: dict[str, Any], n: int) -> None:
    """Simulate stage N completing with artifact files."""
    ctx["stage"] = n
    ctx["files"] = [f"docs/stage{n}-output.md", "docs/traceability-matrix.md"]
    ctx["directory"] = "."


@given("a stage produces no artifact changes")
def given_no_changes(ctx: dict[str, Any]) -> None:
    """Simulate a stage with no changed files."""
    ctx["stage"] = 4
    ctx["files"] = []
    ctx["directory"] = "."


@given(parsers.parse("Stage {n:d} updated ooad-design.md and domain-model.md"))
def given_two_files(ctx: dict[str, Any], n: int) -> None:
    """Simulate Stage N with exactly 2 artifact files."""
    ctx["stage"] = n
    ctx["files"] = ["docs/ooad-design.md", "docs/domain-model.md"]
    ctx["directory"] = "."


@when("auto_commit executes via GitKraken MCP")
def when_auto_commit(ctx: dict[str, Any]) -> None:
    """Execute the auto_commit call."""
    n = ctx.get("stage", 0)
    files = ctx.get("files", [])
    message = f"[Stage {n}] Auto-commit: stage artifacts updated"
    ctx["result"] = ctx["gateway"].auto_commit(ctx["directory"], message, files)


@when("auto_commit checks for changes")
def when_check_changes(ctx: dict[str, Any]) -> None:
    """Execute auto_commit with empty file list."""
    ctx["result"] = ctx["gateway"].auto_commit(ctx["directory"], "empty", ctx["files"])


@when("auto_commit executes")
def when_execute_commit(ctx: dict[str, Any]) -> None:
    """Execute auto_commit for multi-file scenario."""
    n = ctx.get("stage", 0)
    message = f"[Stage {n}] Auto-commit: stage artifacts updated"
    ctx["result"] = ctx["gateway"].auto_commit(ctx["directory"], message, ctx["files"])


@then("a git commit is created")
def then_commit_created(ctx: dict[str, Any]) -> None:
    """Assert committed is True."""
    assert ctx["result"].committed is True


@then(parsers.parse('commit message starts with "[Stage {n:d}]"'))
def then_message_starts(ctx: dict[str, Any], n: int) -> None:
    """Assert commit message starts with [Stage N]."""
    assert ctx["result"].message.startswith(f"[Stage {n}]")


@then("all changed stage artifacts are included")
def then_all_files_included(ctx: dict[str, Any]) -> None:
    """Assert all expected files are in the commit."""
    for f in ctx["files"]:
        assert f in ctx["result"].files


@then("no git commit is created")
def then_no_commit(ctx: dict[str, Any]) -> None:
    """Assert committed is False when no files."""
    assert ctx["result"].committed is False


@then("no error is raised")
def then_no_error(ctx: dict[str, Any]) -> None:
    """Assert result exists without exception."""
    assert ctx["result"] is not None


@then("both files are in the same single commit")
def then_both_files_single_commit(ctx: dict[str, Any]) -> None:
    """Assert exactly one commit with both files."""
    assert ctx["result"].committed is True
    assert len(ctx["result"].files) == 2
    assert len(ctx["gateway"].commits) == 1
