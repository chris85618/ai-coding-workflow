"""Tests for the GitVersionControl frameworks gateway (FR-069, ADR-STR-029)."""

from agentic_workflow.adapters.subprocess import SubprocessExecutor, register_executor
from agentic_workflow.frameworks.git_version_control import GitVersionControl
from agentic_workflow.frameworks.subprocess_executor import OSSubprocessExecutor


class FakeExecutor(SubprocessExecutor):
    """Records commands and replays canned results for git calls."""

    def __init__(self, code: int = 0, stdout: str = "") -> None:
        """Store the canned exit code and stdout."""
        self.code = code
        self.stdout = stdout
        self.commands: list[list[str]] = []

    def run_cmd(self, cmd: str) -> tuple[int, str, str]:
        """Unused string-command variant."""
        return (self.code, self.stdout, "")

    def run_cmd_list(self, cmd: list[str], cwd: str | None = None, timeout: int = 30) -> tuple[int, str, str]:
        """Record the command and replay the canned result."""
        self.commands.append(cmd)
        return (self.code, self.stdout, "")


class TestGitVersionControl:
    """Covers the git-backed rollback gateway over the executor port."""

    def teardown_method(self) -> None:
        """Restore the OS executor so other tests keep a real registration."""
        register_executor(OSSubprocessExecutor())

    def test_current_ref_strips_stdout(self) -> None:
        """TC-V2-052: current_ref returns the trimmed rev-parse output."""
        fake = FakeExecutor(stdout="abc123\n")
        register_executor(fake)
        assert GitVersionControl().current_ref() == "abc123"
        assert fake.commands == [["git", "rev-parse", "HEAD"]]

    def test_rollback_to_reports_success(self) -> None:
        """TC-V2-053: rollback_to is True on exit code 0."""
        fake = FakeExecutor(code=0)
        register_executor(fake)
        assert GitVersionControl().rollback_to("universal-base") is True
        assert fake.commands == [["git", "reset", "--hard", "universal-base"]]

    def test_rollback_to_reports_failure(self) -> None:
        """TC-V2-054: rollback_to is False on non-zero exit code."""
        register_executor(FakeExecutor(code=1))
        assert GitVersionControl().rollback_to("missing-ref") is False

    def test_tag_universal_base_returns_tag(self) -> None:
        """TC-V2-055: Tagging returns the canonical universal-base tag name."""
        fake = FakeExecutor()
        register_executor(fake)
        assert GitVersionControl().tag_universal_base() == "universal-base"
        assert fake.commands == [["git", "tag", "-f", "universal-base"]]
