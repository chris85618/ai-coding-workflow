"""Verify path traversal protection in MarkdownDocumentIO (SEC-002)."""

import tempfile

import pytest

from agentic_workflow.adapters.persistence.markdown_writer import MarkdownDocumentIO


class TestMarkdownWriterPathTraversal:
    """Verify path traversal protection in MarkdownDocumentIO (SEC-002)."""

    def setup_method(self) -> None:
        """Set up temporary directory and IO for testing."""
        self._tmp = tempfile.mkdtemp()
        self.io = MarkdownDocumentIO(repo_root=self._tmp)

    def test_normal_path_works(self) -> None:
        """Verify normal path writing/reading works."""
        self.io.write("docs/test.md", "content")
        assert self.io.read("docs/test.md") == "content"

    def test_traversal_read_raises(self) -> None:
        """Verify path traversal in read is rejected."""
        with pytest.raises(ValueError, match="SEC-002"):
            self.io.read("../../etc/passwd")

    def test_traversal_write_raises(self) -> None:
        """Verify path traversal in write is rejected."""
        with pytest.raises(ValueError, match="SEC-002"):
            self.io.write("../../evil.txt", "malicious")

    def test_traversal_append_raises(self) -> None:
        """Verify path traversal in append is rejected."""
        with pytest.raises(ValueError, match="SEC-002"):
            self.io.append("../../evil.txt", "data")

    def test_traversal_exists_raises(self) -> None:
        """Verify path traversal in exists is rejected."""
        with pytest.raises(ValueError, match="SEC-002"):
            self.io.exists("../../etc/passwd")
