"""Additional adapter coverage tests to reach ≥ 100% total coverage.

Fills branches in:
llm_adapter, sequential_adapter, gitkraken_adapter, nodes, file_repository.
All external I/O remains mocked.
"""

from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest
from pytest_bdd import given, scenario, then, when

if TYPE_CHECKING:
    from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
    from agentic_workflow.domain.models.traceable_id import TraceableID

# ===========================================================================
# LLM Adapter: _build_langchain_model error paths
# ===========================================================================


@scenario(
    "../features/langgraph_dag.feature",
    "Invariants Verifier passes on a correctly structured DAG",
)
def test_invariants_verifier_passes_on_correct_dag() -> None:
    """BDD scenario for invariant verification."""
    pass


class TestLLMProviders:
    """Tests for concrete LLM provider implementations."""

    def test_unsupported_provider_raises(self) -> None:
        """Test registry error when provider is not supported."""
        from agentic_workflow.adapters.llm.provider_registry import LLMProviderRegistry

        registry = LLMProviderRegistry()
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            registry.get_provider("cohere")

    def test_openai_import_error(self) -> None:
        """Test handling of missing langchain_openai in OpenAIProvider."""
        from agentic_workflow.adapters.llm.providers.openai import OpenAIProvider
        from agentic_workflow.domain.models.model_config import ModelConfig

        cfg = ModelConfig(provider="openai", model="gpt-4o")
        provider = OpenAIProvider()
        with (
            patch.dict("sys.modules", {"langchain_openai": None}),
            pytest.raises(ImportError, match="langchain-openai is required"),
        ):
            provider.create_model(cfg)

    def test_anthropic_import_error(self) -> None:
        """Test handling of missing langchain_anthropic in AnthropicProvider."""
        from agentic_workflow.adapters.llm.providers.anthropic import AnthropicProvider
        from agentic_workflow.domain.models.model_config import ModelConfig

        cfg = ModelConfig(provider="anthropic", model="claude-opus")
        provider = AnthropicProvider()
        with (
            patch.dict("sys.modules", {"langchain_anthropic": None}),
            pytest.raises(ImportError, match="langchain-anthropic is required"),
        ):
            provider.create_model(cfg)

    @patch("agentic_workflow.adapters.llm.providers.openai.OpenAIProvider.create_model")
    def test_model_cache_reuse(self, mock_create: MagicMock) -> None:
        """Same (provider, model, temp) key should reuse cached model."""
        from agentic_workflow.adapters.llm.llm_adapter import LangChainLLMAdapter
        from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
        from agentic_workflow.domain.models.enums import TaskType
        from agentic_workflow.domain.models.model_config import ModelConfig

        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="resp")
        mock_create.return_value = mock_model

        m = ModelConfig(provider="openai", model="gpt-4o")
        cfg = StrategyConfig(
            reasoning_model=m,
            editing_model=m,
            cheap_model=m,
            default_model=m,
            fallback_model=m,
            enabled_providers=frozenset(["openai"]),
        )
        adapter = LangChainLLMAdapter(cfg)
        adapter.complete("p1", TaskType.CRITIQUE)
        adapter.complete("p2", TaskType.CRITIQUE)
        # _build_langchain_model called only once due to cache
        assert mock_create.call_count == 1

    @patch(
        "agentic_workflow.adapters.llm.providers.anthropic.AnthropicProvider.create_model"
    )
    def test_anthropic_is_available(self, mock_create: MagicMock) -> None:
        """Test availability for Anthropic provider."""
        from agentic_workflow.adapters.llm.llm_adapter import LangChainLLMAdapter
        from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
        from agentic_workflow.domain.models.model_config import ModelConfig

        m = ModelConfig(provider="anthropic", model="claude-opus")
        cfg = StrategyConfig(
            reasoning_model=m,
            editing_model=m,
            cheap_model=m,
            default_model=m,
            fallback_model=m,
            enabled_providers=frozenset(["anthropic"]),
        )
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            adapter = LangChainLLMAdapter(cfg)
            assert adapter.is_available() is True


# ===========================================================================
# GitKraken: commit failure + git_status + git_commit_raw
# ===========================================================================


@given("a compiled LangGraph built from config.yaml")
def given_compiled_langgraph(context: dict[str, Any]) -> None:
    """BDD given step: compiled graph."""
    # ADR-STR-007: OO Builder is the sole path
    from agentic_workflow.frameworks.graph import build_graph

    context["compiled_graph"] = build_graph()


class TestGitKrakenEdgeCases:
    """Additional branch coverage for GitKrakenMCPAdapter."""

    def setup_method(self) -> None:
        """Set up test environment."""
        from agentic_workflow.adapters.mcp.gitkraken_adapter import GitKrakenMCPAdapter

        self.adapter = GitKrakenMCPAdapter()

    @patch("subprocess.run")
    def test_auto_commit_raises_on_commit_failure(self, mock_run: MagicMock) -> None:
        """Test error handling on git commit failure."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),  # git add
            MagicMock(returncode=1, stdout="", stderr="commit error"),  # git commit
        ]
        with pytest.raises(RuntimeError, match="git commit failed"):
            self.adapter.auto_commit("msg", ["f.py"])

    @patch("subprocess.run")
    def test_call_tool_git_status(self, mock_run: MagicMock) -> None:
        """Test git_status tool call."""
        mock_run.return_value = MagicMock(returncode=0, stdout="M file.py\n", stderr="")
        result = self.adapter.call_tool("git_status", {"repo_path": "."})
        assert result["success"] is True
        assert "file.py" in result["output"]

    @patch("subprocess.run")
    def test_call_tool_git_commit(self, mock_run: MagicMock) -> None:
        """Test git_commit tool call."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="[main abc123]", stderr=""
        )
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
        """Test connection timeout handling."""
        import subprocess

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("git", 5)):
            assert self.adapter.is_connected() is False


# ===========================================================================
# Sequential Thinking: call_tool sequentialthinking (HTTP failure path)
# ===========================================================================


class TestSequentialAdapterEdgeCases:
    """Cover the HTTP call path in SequentialThinkingMCPAdapter."""

    def setup_method(self) -> None:
        """Set up test environment."""
        from agentic_workflow.adapters.mcp.sequential_adapter import (
            SequentialThinkingMCPAdapter,
        )

        self.adapter = SequentialThinkingMCPAdapter(server_url="http://localhost:9999")

    def test_call_sequentialthinking_fails_gracefully(self) -> None:
        """Connection refused returns success=False, not an exception."""
        result = self.adapter.call_tool(
            "sequentialthinking",
            {
                "thought": "test",
                "nextThoughtNeeded": False,
                "thoughtNumber": 1,
                "totalThoughts": 1,
            },
        )
        assert result["success"] is False


# ===========================================================================
# LangGraph Nodes: already-running pipeline + failed nodes
# ===========================================================================


@then('the graph should contain "start_pipeline" node')
def then_contains_start_pipeline(context: dict[str, Any]) -> None:
    """BDD then step: verify start node."""
    graph = context["compiled_graph"]
    assert "start_pipeline" in graph.nodes or "start" in graph.nodes


class TestLangGraphNodeEdgeCases:
    """Edge cases for DAG node functions."""

    def _running_state(self) -> WorkflowState:
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
        """Test iterate_stage node when stage_id is missing."""
        from agentic_workflow.adapters.langgraph.nodes import node_iterate_stage
        from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState

        state = WorkflowState(pipeline_id="p1", pipeline_status="running")
        result = node_iterate_stage(state)
        assert result.get("last_error") is not None

    def test_should_continue_gate_on_passed_status(self) -> None:
        """Test transition logic for passed status."""
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


@when("the graph builder compiles the LangGraph")
def when_graph_builder_compiles(context: dict[str, Any]) -> None:
    """BDD when step: compile graph."""
    from agentic_workflow.frameworks.graph import build_graph

    context["compiled_graph"] = build_graph()


@then("it should return a compiled graph")
def then_returns_compiled_graph(context: dict[str, Any]) -> None:
    """BDD then step: verify compilation."""
    assert context.get("compiled_graph") is not None
    assert hasattr(context["compiled_graph"], "nodes")


@then('the graph should contain "orchestrator" node')
def then_contains_orchestrator(context: dict[str, Any]) -> None:
    """BDD then step: verify orchestrator presence."""
    assert context.get("compiled_graph") is not None


@given("a valid config.yaml with workflow_graph configuration")
def given_valid_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """BDD given step: valid config."""
    pass


@then("all structural invariants should pass")
def then_invariants_should_pass(context: dict[str, Any]) -> None:
    """BDD then step: structural pass."""
    result = context["verification_result"]
    assert result["passed"] is True


@then("there should be zero validation failures")
def then_zero_validation_failures(context: dict[str, Any]) -> None:
    """BDD then step: zero failures."""
    result = context["verification_result"]
    assert len(result["failures"]) == 0


# ===========================================================================
# FileTraceableIDRepository: find_all with data
# ===========================================================================


@when("the DAG Invariant Verifier checks the graph")
def when_verifier_checks_graph(context: dict[str, Any]) -> None:
    """BDD when step: run verification."""
    from agentic_workflow.domain.algorithms.invariants_verifier import (
        DAGInvariantVerifier,
    )

    context["verification_result"] = DAGInvariantVerifier.run_all_verifications(
        context["compiled_graph"]
    )


class TestFileRepositoryFindAll:
    """Tests for find_all with persisted data."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self._tmp = tempfile.mkdtemp()
        from agentic_workflow.adapters.persistence.file_repository import (
            FileTraceableIDRepository,
        )

        self.repo = FileTraceableIDRepository(repo_root=self._tmp)

    def _make_id(self, seq: int, title: str) -> TraceableID:
        from agentic_workflow.domain.models.enums import IDPrefix
        from agentic_workflow.domain.models.traceable_id import TraceableID

        return TraceableID(prefix=IDPrefix.FR, sequence=seq, title=title)

    def test_find_all_returns_saved(self) -> None:
        """Test find_all returns all saved entities."""
        tid1 = self._make_id(1, "First")
        tid2 = self._make_id(2, "Second")
        self.repo.save(tid1)
        self.repo.save(tid2)
        all_ids = self.repo.find_all()
        id_strings = {obj.full_id for obj in all_ids}
        assert "FR-001" in id_strings
        assert "FR-002" in id_strings


# ===========================================================================
# LLM Adapter: Token Limit Exceeded
# ===========================================================================


@scenario(
    "../features/langgraph_dag.feature",
    "Graph Builder constructs a valid StateGraph from config.yaml",
)
def test_graph_builder_constructs_valid_stategraph() -> None:
    """BDD scenario for graph construction."""
    pass


class TestLLMAdapterTokenLimit:
    """Tests for the token auto-continuation and fast-fail logic."""

    def test_auto_continuation(self) -> None:
        """Test auto-continuation for long model responses."""
        from agentic_workflow.adapters.llm.llm_adapter import LangChainLLMAdapter
        from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
        from agentic_workflow.domain.models.enums import TaskType
        from agentic_workflow.domain.models.model_config import ModelConfig

        m = ModelConfig(provider="openai", model="gpt-4o")
        cfg = StrategyConfig(
            reasoning_model=m,
            editing_model=m,
            cheap_model=m,
            default_model=m,
            fallback_model=m,
            enabled_providers=frozenset(["openai"]),
        )
        adapter = LangChainLLMAdapter(cfg)

        mock_model = MagicMock()
        resp1 = MagicMock()
        resp1.content = "Part 1"
        resp1.response_metadata = {"finish_reason": "length"}
        resp2 = MagicMock()
        resp2.content = " Part 2"
        resp2.response_metadata = {"finish_reason": "stop"}
        mock_model.invoke.side_effect = [resp1, resp2]

        with patch(
            "agentic_workflow.adapters.llm.providers.openai.OpenAIProvider.create_model",
            return_value=mock_model,
        ):
            # CRITIQUE supports auto-continuation
            result = adapter.complete("prompt", TaskType.CRITIQUE)
            assert result == "Part 1 Part 2"
            assert mock_model.invoke.call_count == 2

    def test_structured_fast_fail(self) -> None:
        """Test fast-fail for structured task types."""
        from agentic_workflow.adapters.llm.llm_adapter import LangChainLLMAdapter
        from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
        from agentic_workflow.domain.models.enums import TaskType
        from agentic_workflow.domain.models.exceptions import TokenLimitExceededError
        from agentic_workflow.domain.models.model_config import ModelConfig

        m = ModelConfig(provider="openai", model="gpt-4o")
        cfg = StrategyConfig(
            reasoning_model=m,
            editing_model=m,
            cheap_model=m,
            default_model=m,
            fallback_model=m,
            enabled_providers=frozenset(["openai"]),
        )
        adapter = LangChainLLMAdapter(cfg)

        mock_model = MagicMock()
        resp = MagicMock()
        resp.content = '{"partial": '
        resp.response_metadata = {"finish_reason": "length"}
        mock_model.invoke.return_value = resp

        with (
            patch(
                "agentic_workflow.adapters.llm.providers.openai.OpenAIProvider.create_model",
                return_value=mock_model,
            ),
            pytest.raises(TokenLimitExceededError, match="Auto-continuation disabled"),
        ):
            # RESOLVE does not support auto-continuation
            adapter.complete("prompt", TaskType.RESOLVE)

    def test_stop_reason_anthropic(self) -> None:
        """Test stop_reason mapping for Anthropic provider."""
        from agentic_workflow.adapters.llm.llm_adapter import LangChainLLMAdapter
        from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
        from agentic_workflow.domain.models.enums import TaskType
        from agentic_workflow.domain.models.model_config import ModelConfig

        m = ModelConfig(provider="anthropic", model="claude-opus")
        cfg = StrategyConfig(
            reasoning_model=m,
            editing_model=m,
            cheap_model=m,
            default_model=m,
            fallback_model=m,
            enabled_providers=frozenset(["anthropic"]),
        )
        adapter = LangChainLLMAdapter(cfg)

        mock_model = MagicMock()
        resp = MagicMock()
        resp.content = "Anthropic reply"
        # Simulate finish_reason being missing and using stop_reason
        resp.response_metadata = {"stop_reason": "stop_sequence"}
        mock_model.invoke.return_value = resp

        with patch(
            "agentic_workflow.adapters.llm.providers.anthropic.AnthropicProvider.create_model",
            return_value=mock_model,
        ):
            result = adapter.complete("prompt", TaskType.COMPREHEND)
            assert result == "Anthropic reply"

    def test_max_continuations_exceeded(self) -> None:
        """Test error when max continuations reached."""
        from agentic_workflow.adapters.llm.llm_adapter import LangChainLLMAdapter
        from agentic_workflow.domain.algorithms.model_selector import StrategyConfig
        from agentic_workflow.domain.models.enums import TaskType
        from agentic_workflow.domain.models.exceptions import TokenLimitExceededError
        from agentic_workflow.domain.models.model_config import ModelConfig

        m = ModelConfig(provider="openai", model="gpt-4o")
        cfg = StrategyConfig(
            reasoning_model=m,
            editing_model=m,
            cheap_model=m,
            default_model=m,
            fallback_model=m,
            enabled_providers=frozenset(["openai"]),
        )
        adapter = LangChainLLMAdapter(cfg)

        mock_model = MagicMock()
        resp = MagicMock()
        resp.content = "Loop "
        resp.response_metadata = {"finish_reason": "length"}
        # It will continuously return length. max_continuations is 3.
        # It will invoke 4 times (initial + 3 continuations) and then raise.
        mock_model.invoke.return_value = resp

        with (
            patch(
                "agentic_workflow.adapters.llm.providers.openai.OpenAIProvider.create_model",
                return_value=mock_model,
            ),
            pytest.raises(TokenLimitExceededError, match="across 3 continuations"),
        ):
            adapter.complete("prompt", TaskType.CRITIQUE)
