"""Tests for Adapter Layer — DEBT-002 implementation.

Traceable to: FR-001, FR-015, FR-018, FR-026~030
Tests all 4 adapter sub-packages without requiring external services.
All external dependencies (LLM APIs, MCP servers, git) are mocked.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ===========================================================================
# Port interface smoke tests (ABC compliance)
# ===========================================================================

class TestPortInterfaces:
    """Verify all ABC ports can be subclassed and satisfy their contracts."""

    def test_traceable_id_repository_is_abc(self) -> None:
        from agentic_workflow.application.ports.repositories import TraceableIDRepository
        with pytest.raises(TypeError):
            TraceableIDRepository()  # type: ignore[abstract]

    def test_checkpoint_repository_is_abc(self) -> None:
        from agentic_workflow.application.ports.repositories import CheckpointRepository
        with pytest.raises(TypeError):
            CheckpointRepository()  # type: ignore[abstract]

    def test_llm_gateway_is_abc(self) -> None:
        from agentic_workflow.application.ports.gateways import LLMGateway
        with pytest.raises(TypeError):
            LLMGateway()  # type: ignore[abstract]

    def test_mcp_gateway_is_abc(self) -> None:
        from agentic_workflow.application.ports.gateways import MCPGateway
        with pytest.raises(TypeError):
            MCPGateway()  # type: ignore[abstract]

    def test_document_io_is_abc(self) -> None:
        from agentic_workflow.application.ports.doc_io import DocumentIOGateway
        with pytest.raises(TypeError):
            DocumentIOGateway()  # type: ignore[abstract]

    def test_event_bus_is_abc(self) -> None:
        from agentic_workflow.application.ports.doc_io import DomainEventBus
        with pytest.raises(TypeError):
            DomainEventBus()  # type: ignore[abstract]


# ===========================================================================
# Persistence: FileTraceableIDRepository
# ===========================================================================

class TestFileTraceableIDRepository:
    """Tests for filesystem-backed TraceableID repository."""

    def setup_method(self) -> None:
        self._tmp = tempfile.mkdtemp()
        from agentic_workflow.adapters.persistence.file_repository import (
            FileTraceableIDRepository,
        )
        self.repo = FileTraceableIDRepository(repo_root=self._tmp)

    def _make_id(self) -> object:
        from agentic_workflow.domain.models.traceable_id import TraceableID
        from agentic_workflow.domain.models.enums import IDPrefix
        return TraceableID(prefix=IDPrefix.FR, sequence=1, title="Test FR")

    def test_save_and_find_by_id(self) -> None:
        tid = self._make_id()
        self.repo.save(tid)  # type: ignore[arg-type]
        result = self.repo.find_by_id("FR-001")
        assert result is not None
        assert result.full_id == "FR-001"

    def test_find_by_id_missing_returns_none(self) -> None:
        assert self.repo.find_by_id("XX-999") is None

    def test_find_all_empty(self) -> None:
        assert self.repo.find_all() == []

    def test_delete_existing(self) -> None:
        tid = self._make_id()
        self.repo.save(tid)  # type: ignore[arg-type]
        assert self.repo.delete("FR-001") is True
        assert self.repo.find_by_id("FR-001") is None

    def test_delete_missing(self) -> None:
        assert self.repo.delete("FR-999") is False


# ===========================================================================
# Persistence: FileCheckpointRepository
# ===========================================================================

class TestFileCheckpointRepository:
    """Tests for filesystem-backed checkpoint repository."""

    def setup_method(self) -> None:
        self._tmp = tempfile.mkdtemp()
        from agentic_workflow.adapters.persistence.checkpoint_repository import (
            FileCheckpointRepository,
        )
        self.repo = FileCheckpointRepository(repo_root=self._tmp)

    def test_save_and_load_latest(self) -> None:
        state = {"pipeline_id": "p1", "position": "phase0"}
        cid = self.repo.save_checkpoint("p1", state)
        assert isinstance(cid, str)
        loaded = self.repo.load_latest("p1")
        assert loaded == state

    def test_load_latest_empty_returns_none(self) -> None:
        assert self.repo.load_latest("nonexistent") is None

    def test_list_checkpoints(self) -> None:
        self.repo.save_checkpoint("p1", {"a": 1})
        self.repo.save_checkpoint("p1", {"b": 2})
        cids = self.repo.list_checkpoints("p1")
        assert len(cids) == 2
        # Newest first
        assert cids[0] > cids[1]

    def test_delete_checkpoint(self) -> None:
        cid = self.repo.save_checkpoint("p1", {"x": 1})
        assert self.repo.delete_checkpoint("p1", cid) is True
        assert self.repo.load_latest("p1") is None

    def test_delete_missing_checkpoint(self) -> None:
        assert self.repo.delete_checkpoint("p1", "nonexistent") is False


# ===========================================================================
# Persistence: MarkdownDocumentIO
# ===========================================================================

class TestMarkdownDocumentIO:
    """Tests for filesystem Markdown document I/O adapter."""

    def setup_method(self) -> None:
        self._tmp = tempfile.mkdtemp()
        from agentic_workflow.adapters.persistence.markdown_writer import (
            MarkdownDocumentIO,
        )
        self.io = MarkdownDocumentIO(repo_root=self._tmp)

    def test_write_and_read(self) -> None:
        self.io.write("docs/test.md", "# Hello")
        assert self.io.read("docs/test.md") == "# Hello"

    def test_exists_false_before_write(self) -> None:
        assert not self.io.exists("docs/missing.md")

    def test_exists_true_after_write(self) -> None:
        self.io.write("docs/exist.md", "content")
        assert self.io.exists("docs/exist.md")

    def test_append(self) -> None:
        self.io.write("docs/a.md", "line1\n")
        self.io.append("docs/a.md", "line2\n")
        content = self.io.read("docs/a.md")
        assert "line1" in content
        assert "line2" in content

    def test_read_missing_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            self.io.read("docs/missing.md")

    def test_write_creates_parent_dirs(self) -> None:
        self.io.write("deep/nested/dir/file.md", "content")
        assert self.io.exists("deep/nested/dir/file.md")


# ===========================================================================
# Persistence: HookConfigLoader
# ===========================================================================

class TestHookConfigLoader:
    """Tests for JSON hook configuration loader."""

    def setup_method(self) -> None:
        self._tmp = tempfile.mkdtemp()

    def test_load_from_file(self) -> None:
        config = {
            "hooks": [
                {
                    "event": "pre_stage_start",
                    "command": "echo hello",
                    "blocking": True,
                    "matcher": "",
                }
            ]
        }
        cfg_path = Path(self._tmp) / "hooks.json"
        cfg_path.write_text(json.dumps(config), encoding="utf-8")

        from agentic_workflow.adapters.persistence.hook_config_loader import (
            HookConfigLoader,
        )
        from agentic_workflow.domain.models.enums import HookEvent

        loader = HookConfigLoader(str(cfg_path))
        hooks = loader.load()
        assert len(hooks) == 1
        assert hooks[0].event == HookEvent.PRE_STAGE_START
        assert hooks[0].command == "echo hello"
        assert hooks[0].blocking is True

    def test_from_dict(self) -> None:
        from agentic_workflow.adapters.persistence.hook_config_loader import (
            HookConfigLoader,
        )
        from agentic_workflow.domain.models.enums import HookEvent

        config = {
            "hooks": [
                {"event": "post_doc_write", "command": "git add .", "blocking": False}
            ]
        }
        hooks = HookConfigLoader.from_dict(config)
        assert len(hooks) == 1
        assert hooks[0].event == HookEvent.POST_DOC_WRITE
        assert hooks[0].blocking is False

    def test_from_dict_empty(self) -> None:
        from agentic_workflow.adapters.persistence.hook_config_loader import (
            HookConfigLoader,
        )
        hooks = HookConfigLoader.from_dict({})
        assert hooks == []


# ===========================================================================
# Events: InMemoryEventBus
# ===========================================================================

class TestInMemoryEventBus:
    """Tests for the in-memory domain event bus."""

    def setup_method(self) -> None:
        from agentic_workflow.adapters.events.in_memory_bus import InMemoryEventBus
        self.bus = InMemoryEventBus()

    def test_publish_and_get_events(self) -> None:
        self.bus.publish("ModelSelected", {"provider": "openai"})
        events = self.bus.get_published_events()
        assert len(events) == 1
        assert events[0]["type"] == "ModelSelected"
        assert events[0]["payload"]["provider"] == "openai"

    def test_subscribe_and_receive(self) -> None:
        received = []
        self.bus.subscribe("GitCommitCreated", lambda t, p: received.append(p))
        self.bus.publish("GitCommitCreated", {"sha": "abc123"})
        assert received == [{"sha": "abc123"}]

    def test_clear(self) -> None:
        self.bus.publish("Evt", {"x": 1})
        self.bus.clear()
        assert self.bus.get_published_events() == []

    def test_multiple_subscribers(self) -> None:
        calls: list[str] = []
        self.bus.subscribe("Evt", lambda t, p: calls.append("A"))
        self.bus.subscribe("Evt", lambda t, p: calls.append("B"))
        self.bus.publish("Evt", {})
        assert calls == ["A", "B"]


# ===========================================================================
# MCP: GitKrakenMCPAdapter
# ===========================================================================

class TestGitKrakenMCPAdapter:
    """Tests for GitKraken MCP adapter (git operations mocked)."""

    def setup_method(self) -> None:
        from agentic_workflow.adapters.mcp.gitkraken_adapter import GitKrakenMCPAdapter
        from agentic_workflow.adapters.events.in_memory_bus import InMemoryEventBus
        self.bus = InMemoryEventBus()
        self.adapter = GitKrakenMCPAdapter(event_bus=self.bus)

    def test_call_tool_unknown(self) -> None:
        result = self.adapter.call_tool("unknown_tool", {})
        assert result["success"] is False

    def test_call_tool_git_add_no_files(self) -> None:
        result = self.adapter.call_tool("git_add", {"files": [], "repo_path": "."})
        assert result["success"] is True

    @patch("subprocess.run")
    def test_auto_commit_emits_event(self, mock_run: MagicMock) -> None:
        # add succeeds, commit succeeds, rev-parse returns SHA
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),   # git add
            MagicMock(returncode=0, stdout="", stderr=""),   # git commit
            MagicMock(returncode=0, stdout="deadbeef\n", stderr=""),  # rev-parse
        ]
        sha = self.adapter.auto_commit("test: commit", ["file.py"], repo_path=".")
        assert sha == "deadbeef"
        events = self.bus.get_published_events()
        assert any(e["type"] == "GitCommitCreated" for e in events)

    @patch("subprocess.run")
    def test_auto_commit_raises_on_add_failure(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        with pytest.raises(RuntimeError, match="git add failed"):
            self.adapter.auto_commit("msg", ["f.py"])

    @patch("subprocess.run")
    def test_is_connected_true(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0)
        assert self.adapter.is_connected() is True

    @patch("subprocess.run")
    def test_is_connected_false(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1)
        assert self.adapter.is_connected() is False

    def test_is_connected_file_not_found(self) -> None:
        """is_connected returns False when git binary not found."""
        from agentic_workflow.adapters.mcp.gitkraken_adapter import GitKrakenMCPAdapter
        adapter = GitKrakenMCPAdapter(git_binary="/nonexistent/git")
        assert adapter.is_connected() is False


# ===========================================================================
# MCP: SequentialThinkingMCPAdapter
# ===========================================================================

class TestSequentialThinkingMCPAdapter:
    """Tests for Sequential Thinking MCP adapter."""

    def setup_method(self) -> None:
        from agentic_workflow.adapters.mcp.sequential_adapter import (
            SequentialThinkingMCPAdapter,
        )
        self.adapter = SequentialThinkingMCPAdapter(server_url="http://localhost:9999")

    def test_auto_commit_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            self.adapter.auto_commit("msg", [])

    def test_call_tool_unknown(self) -> None:
        result = self.adapter.call_tool("unknown", {})
        assert result["success"] is False

    def test_is_connected_false_when_server_down(self) -> None:
        # Port 9999 is not listening
        assert self.adapter.is_connected() is False


# ===========================================================================
# LangGraph: StateMapper
# ===========================================================================

class TestStateMapper:
    """Tests for bidirectional WorkflowState <-> Pipeline/Stage mapping."""

    def test_pipeline_roundtrip(self) -> None:
        from agentic_workflow.adapters.langgraph.state_mapper import StateMapper
        from agentic_workflow.domain.models.pipeline import Pipeline
        from agentic_workflow.domain.models.enums import PipelineStatus

        pipeline = Pipeline(pipeline_id="test-pipe")
        pipeline.start()
        state = StateMapper.pipeline_to_state(pipeline)
        restored = StateMapper.state_to_pipeline(state)
        assert restored.pipeline_id == "test-pipe"
        assert restored.status == PipelineStatus.RUNNING

    def test_stage_roundtrip(self) -> None:
        from agentic_workflow.adapters.langgraph.state_mapper import StateMapper
        from agentic_workflow.domain.models.stage import Stage
        from agentic_workflow.domain.models.enums import StageStatus

        stage = Stage(stage_id="stage3", name="Technical Planning")
        state = StateMapper.stage_to_state(stage)
        restored = StateMapper.state_to_stage(state)
        assert restored is not None
        assert restored.stage_id == "stage3"
        assert restored.status == StageStatus.PENDING

    def test_state_to_stage_none_when_no_stage_id(self) -> None:
        from agentic_workflow.adapters.langgraph.state_mapper import StateMapper, WorkflowState
        state = WorkflowState(pipeline_id="p1")
        assert StateMapper.state_to_stage(state) is None

    def test_pipeline_with_gate(self) -> None:
        from agentic_workflow.adapters.langgraph.state_mapper import StateMapper
        from agentic_workflow.domain.models.pipeline import Pipeline
        from agentic_workflow.domain.models.enums import GateDecision

        pipeline = Pipeline(pipeline_id="g-test")
        pipeline.start()
        pipeline.record_gate(GateDecision.PASS)
        state = StateMapper.pipeline_to_state(pipeline)
        assert state["last_gate_decision"] == "pass"


# ===========================================================================
# LangGraph: DAG Node Functions
# ===========================================================================

class TestLangGraphNodes:
    """Tests for LangGraph DAG node functions."""

    def _base_state(self) -> dict:
        from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
        return WorkflowState(
            pipeline_id="pipe-test",
            pipeline_status="not_started",
            current_position="phase0",
        )

    def test_node_start_pipeline(self) -> None:
        from agentic_workflow.adapters.langgraph.nodes import node_start_pipeline
        state = self._base_state()
        result = node_start_pipeline(state)
        assert result["pipeline_status"] == "running"

    def test_node_auto_gate_default_pass(self) -> None:
        from agentic_workflow.adapters.langgraph.nodes import node_auto_gate
        state = self._base_state()
        state["pipeline_status"] = "running"
        result = node_auto_gate(state)
        assert result["last_gate_decision"] == "pass"

    def test_node_auto_gate_pass_with_warnings(self) -> None:
        from agentic_workflow.adapters.langgraph.nodes import node_auto_gate
        state = self._base_state()
        state["pipeline_status"] = "running"
        state["metadata"] = {"gate_override": "pass_with_warnings"}
        result = node_auto_gate(state)
        assert result["last_gate_decision"] == "pass_with_warnings"

    def test_node_advance_stage(self) -> None:
        from agentic_workflow.adapters.langgraph.nodes import node_advance_stage
        from agentic_workflow.domain.models.enums import GateDecision
        state = self._base_state()
        state["pipeline_status"] = "running"
        state["last_gate_decision"] = GateDecision.PASS.value
        result = node_advance_stage(state)
        assert result["current_position"] == "phase1"

    def test_node_iterate_stage(self) -> None:
        from agentic_workflow.adapters.langgraph.nodes import node_iterate_stage
        state = self._base_state()
        state["current_stage_id"] = "stage3"
        state["stage_status"] = "pending"
        state["iteration_count"] = 0
        state["metadata"] = {"stage_name": "Technical Planning"}
        result = node_iterate_stage(state)
        assert result["iteration_count"] == 1
        assert result["stage_status"] == "iterating"

    def test_node_complete_pipeline(self) -> None:
        from agentic_workflow.adapters.langgraph.nodes import node_complete_pipeline
        state = self._base_state()
        state["pipeline_status"] = "running"
        result = node_complete_pipeline(state)
        assert result["pipeline_status"] == "completed"

    def test_should_continue_iterating_no_stage(self) -> None:
        from agentic_workflow.adapters.langgraph.nodes import should_continue_iterating
        state = self._base_state()
        assert should_continue_iterating(state) == "gate"

    def test_should_continue_iterating_iterate(self) -> None:
        from agentic_workflow.adapters.langgraph.nodes import should_continue_iterating
        state = self._base_state()
        state["current_stage_id"] = "stage3"
        state["stage_status"] = "iterating"
        state["iteration_count"] = 2
        state["metadata"] = {"stage_name": "s"}
        assert should_continue_iterating(state) == "iterate"

    def test_should_continue_iterating_gate_on_max(self) -> None:
        from agentic_workflow.adapters.langgraph.nodes import should_continue_iterating
        from agentic_workflow.domain.models.stage import MAX_ITERATIONS
        state = self._base_state()
        state["current_stage_id"] = "stage3"
        state["stage_status"] = "iterating"
        state["iteration_count"] = MAX_ITERATIONS
        state["metadata"] = {"stage_name": "s"}
        assert should_continue_iterating(state) == "gate"


# ===========================================================================
# LLM: LangChainLLMAdapter (mocked provider)
# ===========================================================================

class TestLangChainLLMAdapter:
    """Tests for LLM adapter with mocked LangChain models."""

    def _make_config(self) -> object:
        from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
        from agentic_workflow.domain.models.model_config import ModelConfig

        model = ModelConfig(provider="openai", model="gpt-4o", temperature=0.0)
        return StrategyConfig(
            reasoning_model=model,
            editing_model=model,
            cheap_model=model,
            default_model=model,
            fallback_model=model,
            enabled_providers=frozenset(["openai"]),
        )

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"})
    def test_is_available_with_api_key(self) -> None:
        from agentic_workflow.adapters.llm.llm_adapter import LangChainLLMAdapter
        adapter = LangChainLLMAdapter(self._make_config())  # type: ignore[arg-type]
        assert adapter.is_available() is True

    def test_is_available_without_api_key(self) -> None:
        from agentic_workflow.adapters.llm.llm_adapter import LangChainLLMAdapter
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            adapter = LangChainLLMAdapter(self._make_config())  # type: ignore[arg-type]
            assert adapter.is_available() is False

    def test_get_model_config(self) -> None:
        from agentic_workflow.adapters.llm.llm_adapter import LangChainLLMAdapter
        from agentic_workflow.domain.models.enums import TaskType
        adapter = LangChainLLMAdapter(self._make_config())  # type: ignore[arg-type]
        cfg = adapter.get_model_config(TaskType.CRITIQUE)
        assert cfg.provider == "openai"

    @patch("agentic_workflow.adapters.llm.llm_adapter._build_langchain_model")
    def test_complete_calls_model(self, mock_build: MagicMock) -> None:
        from agentic_workflow.adapters.llm.llm_adapter import LangChainLLMAdapter
        from agentic_workflow.domain.models.enums import TaskType
        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="test response")
        mock_build.return_value = mock_model

        adapter = LangChainLLMAdapter(self._make_config())  # type: ignore[arg-type]
        result = adapter.complete("Hello", TaskType.RESOLVE)
        assert result == "test response"
        mock_model.invoke.assert_called_once()
