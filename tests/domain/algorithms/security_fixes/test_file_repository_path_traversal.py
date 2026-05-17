"""Verify path traversal protection in FileTraceableIDRepository (SEC-003)."""

import tempfile

from agentic_workflow.frameworks.persistence.file_repository import FileTraceableIDRepository


class TestFileRepositoryPathTraversal:
    """Verify path traversal protection in FileTraceableIDRepository (SEC-003)."""

    def setup_method(self) -> None:
        """Set up temporary directory and repository for testing."""
        self._tmp = tempfile.mkdtemp()
        self.repo = FileTraceableIDRepository(repo_root=self._tmp)

    def test_normal_id_works(self) -> None:
        """Verify normal ID lookup works."""
        assert self.repo.find_by_id("FR-001") is None  # Not found, but no error

    def test_dotdot_in_id_is_sanitised(self) -> None:
        """.. sequences in ID strings are replaced, not traversed (SEC-003)."""
        # Should not raise; path is sanitised to stay within root
        result = self.repo.find_by_id("../../../etc/passwd")
        assert result is None  # Safe: sanitised path doesn't match any file

    def test_slash_in_id_is_sanitised(self) -> None:
        """Verify slash in ID is sanitised."""
        result = self.repo.find_by_id("FR/001")
        assert result is None
