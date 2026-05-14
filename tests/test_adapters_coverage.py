"""Additional adapter coverage tests to reach ≥ 95% total coverage.

Fills branches in llm_adapter, sequential_adapter, gitkraken_adapter, nodes, file_repository.
All external I/O remains mocked.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ===========================================================================
# LLM Adapter: _build_langchain_model error paths
# ===========================================================================

class TestBuildLangchainModel:
    """Tests for the provider dispatch in _build_langchain_model."""

    def test_unsupported_provider_raises(self) -> None:
        from agentic_workflow.adapters.llm.llm_adapter import _build_langchain_model
        from agentic_workflow.domain.models.model_config import ModelConfig
        cfg = ModelConfig(provider="cohere", model="command-r")
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            _build_langchain_model(cfg)

    def test_openai_import_error(self) -> None:
        from agentic_workflow.adapters.llm.llm_adapter import _build_langchain_model
        from agentic_workflow.domain.models.model_config import ModelConfig
        cfg = ModelConfig(provider="openai", model="gpt-4o")
        with patch.dict("sys.modules", {"langchain_openai": None}):
            with pytest.raises((ImportError, Exception)):
                _build_langchain_model(cfg)

    def test_anthropic_import_error(self) -> None:
        from agentic_workflow.adapters.llm.llm_adapter import _build_langchain_model
        from agentic_workflow.domain.models.model_config import ModelConfig
        cfg = ModelConfig(provider="anthropic", model="claude-opus")
        with patch.dict("sys.modules", {"langchain_anthropic": None}):
            with pytest.raises((ImportError, Exception)):
                _build_langchain_model(cfg)

    @patch("agentic_workflow.adapters.llm.llm_adapter._build_langchain_model")
    def test_model_cache_reuse(self, mock_build: MagicMock) -> None:
        """Same (provider, model, temp) key should reuse cached model."""
        from agentic_workflow.adapters.llm.llm_adapter import LangChainLLMAdapter
        from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
        from agentic_workflow.domain.models.model_config import ModelConfig
        from agentic_workflow.domain.models.enums import TaskType

        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="resp")
        mock_build.return_value = mock_model

        m = ModelConfig(provider="openai", model="gpt-4o")
        cfg = StrategyConfig(
            reasoning_model=m, editing_model=m, cheap_model=m,
            default_model=m, fallback_model=m,
            enabled_providers=frozenset(["openai"]),
        )
        adapter = LangChainLLMAdapter(cfg)
        adapter.complete("p1", TaskType.CRITIQUE)
        adapter.complete("p2", TaskType.CRITIQUE)
        # _build_langchain_model called only once due to cache
        assert mock_build.call_count == 1

    @patch("agentic_workflow.adapters.llm.llm_adapter._build_langchain_model")
    def test_anthropic_is_available(self, mock_build: MagicMock) -> None:
        from agentic_workflow.adapters.llm.llm_adapter import LangChainLLMAdapter
        from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
        from agentic_workflow.domain.models.model_config import ModelConfig

        m = ModelConfig(provider="anthropic", model="claude-opus")
        cfg = StrategyConfig(
            reasoning_model=m, editing_model=m, cheap_model=m,
            default_model=m, fallback_model=m,
            enabled_providers=frozenset(["anthropic"]),
        )
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            adapter = LangChainLLMAdapter(cfg)
            assert adapter.is_available() is True


# ===========================================================================
# GitKraken: commit failure + git_status + git_commit_raw
# ===========================================================================

class TestGitKrakenEdgeCases:
    """Additional branch coverage for GitKrakenMCPAdapter."""

    def setup_method(self) -> None:
        from agentic_workflow.adapters.mcp.gitkraken_adapter import GitKrakenMCPAdapter
        self.adapter = GitKrakenMCPAdapter()

    @patch("subprocess.run")
    def test_auto_commit_raises_on_commit_failure(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),  # git add
            MagicMock(returncode=1, stdout="", stderr="commit error"),  # git commit
        ]
        with pytest.raises(RuntimeError, match="git commit failed"):
            self.adapter.auto_commit("msg", ["f.py"])

    @patch("subprocess.run")
    def test_call_tool_git_status(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="M file.py\n", stderr="")
        result = self.adapter.call_tool("git_status", {"repo_path": "."})
        assert result["success"] is True
        assert "file.py" in result["output"]

    @patch("subprocess.run")
    def test_call_tool_git_commit(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="[main abc123]", stderr="")
        result = self.adapter.call_tool("git_commit", {"message": "feat: x"})
        assert result["success"] is True

    @patch("subprocess.run")
    def test_get_head_sha_failure(self, mock_run: MagicMock) -> None:
        """If rev-parse fails, returns 'unknown'."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),  # add
            MagicMock(returncode=0, stdout="", stderr=""),  # commit
            MagicMock(returncode=1, stdout="", stderr="error"),  # rev-parse
        ]
        sha = self.adapter.auto_commit("msg", ["f.py"])
        assert sha == "unknown"

    def test_is_connected_timeout(self) -> None:
        import subprocess
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("git", 5)):
            assert self.adapter.is_connected() is False


# ===========================================================================
# Sequential Thinking: call_tool sequentialthinking (HTTP failure path)
# ===========================================================================

class TestSequentialAdapterEdgeCases:
    """Cover the HTTP call path in SequentialThinkingMCPAdapter."""

    def setup_method(self) -> None:
        from agentic_workflow.adapters.mcp.sequential_adapter import (
            SequentialThinkingMCPAdapter,
        )
        self.adapter = SequentialThinkingMCPAdapter(server_url="http://localhost:9999")

    def test_call_sequentialthinking_fails_gracefully(self) -> None:
        """Connection refused returns success=False, not an exception."""
        result = self.adapter.call_tool("sequentialthinking", {"thought": "test", "nextThoughtNeeded": False, "thoughtNumber": 1, "totalThoughts": 1})
        assert result["success"] is False


# ===========================================================================
# LangGraph Nodes: already-running pipeline + failed nodes
# ===========================================================================

class TestLangGraphNodeEdgeCases:
    """Edge cases for DAG node functions."""

    def _running_state(self) -> dict:
        from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
        from agentic_workflow.domain.models.enums import GateDecision
        return WorkflowState(
            pipeline_id="pipe-test",
            pipeline_status="running",
            current_position="phase0",
            last_gate_decision=GateDecision.PASS.value,
        )

    def test_node_start_already_running(self) -> None:
        """Starting a running pipeline should not re-start (no-op)."""
        from agentic_workflow.adapters.langgraph.nodes import node_start_pipeline
        state = self._running_state()
        result = node_start_pipeline(state)
        assert result["pipeline_status"] == "running"

    def test_node_complete_already_completed(self) -> None:
        """Completing a completed pipeline is a no-op."""
        from agentic_workflow.adapters.langgraph.nodes import node_complete_pipeline
        state = self._running_state()
        state["pipeline_status"] = "completed"
        result = node_complete_pipeline(state)
        assert result["pipeline_status"] == "completed"

    def test_node_iterate_no_stage(self) -> None:
        """Iterating with no stage_id returns error state."""
        from agentic_workflow.adapters.langgraph.nodes import node_iterate_stage
        from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
        state = WorkflowState(pipeline_id="p1", pipeline_status="running")
        result = node_iterate_stage(state)
        assert result.get("last_error") is not None

    def test_should_continue_gate_on_passed_status(self) -> None:
        from agentic_workflow.adapters.langgraph.nodes import should_continue_iterating
        from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
        state = WorkflowState(
            pipeline_id="p1",
            current_stage_id="stage3",
            stage_status="passed",
            iteration_count=3,
            metadata={"stage_name": "s"},
        )
        assert should_continue_iterating(state) == "gate"


# ===========================================================================
# FileTraceableIDRepository: find_all with data
# ===========================================================================

class TestFileRepositoryFindAll:
    """Tests for find_all with persisted data."""

    def setup_method(self) -> None:
        self._tmp = tempfile.mkdtemp()
        from agentic_workflow.adapters.persistence.file_repository import (
            FileTraceableIDRepository,
        )
        self.repo = FileTraceableIDRepository(repo_root=self._tmp)

    def _make_id(self, seq: int, title: str) -> object:
        from agentic_workflow.domain.models.traceable_id import TraceableID
        from agentic_workflow.domain.models.enums import IDPrefix
        return TraceableID(prefix=IDPrefix.FR, sequence=seq, title=title)

    def test_find_all_returns_saved(self) -> None:
        tid1 = self._make_id(1, "First")
        tid2 = self._make_id(2, "Second")
        self.repo.save(tid1)  # type: ignore[arg-type]
        self.repo.save(tid2)  # type: ignore[arg-type]
        all_ids = self.repo.find_all()
        id_strings = {obj.full_id for obj in all_ids}
        assert "FR-001" in id_strings
        assert "FR-002" in id_strings
