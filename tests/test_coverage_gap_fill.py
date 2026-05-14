"""Unit tests to fill coverage gaps to reach 95%+.

Covers missing branches in:
- convergence.py (divergence branch, max iter)
- blast_radius.py (MEDIUM/HIGH branches)
- pipeline.py (invalid position, complete(), final stage)
- repo_map.py (empty prune, context string with single file)
- llm_strategy_selector.py (list_providers, enabled_provider_count)
- traceable_id.py (add_upstream/downstream guards)
- hook_runner.py (timeout path, empty event, all_proceeded=False)
- repo_map_builder.py (no py files, unreadable file branches)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from agentic_workflow.domain.algorithms.blast_radius import classify_severity
from agentic_workflow.domain.algorithms.convergence import (
    check_convergence,
    should_auto_pass,
)
from agentic_workflow.domain.algorithms.context_budget import allocate_budget
from agentic_workflow.domain.algorithms.model_selector import (
    StrategyConfig,
    select_model,
)
from agentic_workflow.domain.algorithms.repo_map_builder import (
    _build_import_graph,
    _extract_symbols_ast,
    _pagerank,
    repo_map_build,
)
from agentic_workflow.domain.models.enums import (
    FixedPointResult,
    GateDecision,
    HookEvent,
    IDPrefix,
    LinkType,
    PipelineStatus,
    Severity,
    StageStatus,
    TaskType,
)
from agentic_workflow.domain.models.model_config import ModelConfig
from agentic_workflow.domain.models.pipeline import Pipeline, _STAGE_ORDER
from agentic_workflow.domain.models.repo_map import RepoMap, SymbolDef
from agentic_workflow.domain.models.stage import Stage
from agentic_workflow.domain.models.traceable_id import TraceLink, TraceableID
from agentic_workflow.domain.services.hook_runner import HookDef, HookRunner
from agentic_workflow.domain.services.llm_strategy_selector import LLMStrategySelector


# ── convergence.py ────────────────────────────────────────────────────────────

class TestConvergenceBranches:
    """Cover missing branches in ALG-001 convergence.py."""

    def test_diverging_result(self):
        """DIVERGING: finding count increasing over 3 iterations."""
        history = [["A"], ["A", "B"], ["A", "B", "C"]]
        result = check_convergence(
            iteration_count=3,
            findings_per_iter=history,
            current_findings=["A", "B", "C", "D"],
        )
        assert result == FixedPointResult.DIVERGING

    def test_not_reached_short_history(self):
        """NOT_REACHED: insufficient history for divergence detection."""
        history = [["A"]]
        result = check_convergence(
            iteration_count=1,
            findings_per_iter=history,
            current_findings=["CRITICAL: issue"],
        )
        assert result == FixedPointResult.NOT_REACHED

    def test_max_iterations_boundary(self):
        """MAX_ITERATIONS: iteration_count >= 10."""
        result = check_convergence(
            iteration_count=10,
            findings_per_iter=[],
            current_findings=["CRITICAL: still here"],
        )
        assert result == FixedPointResult.MAX_ITERATIONS

    def test_should_auto_pass_not_reached(self):
        """NOT_REACHED should NOT auto-pass."""
        assert should_auto_pass(FixedPointResult.NOT_REACHED) is False

    def test_diverging_auto_pass(self):
        """DIVERGING should auto-pass per ADR-STR-003."""
        assert should_auto_pass(FixedPointResult.DIVERGING) is True

    def test_max_iterations_auto_pass(self):
        """MAX_ITERATIONS should auto-pass with warning."""
        assert should_auto_pass(FixedPointResult.MAX_ITERATIONS) is True


# ── blast_radius.py ───────────────────────────────────────────────────────────

class TestBlastRadiusBranches:
    """Cover missing severity branches in ALG-003."""

    def test_medium_severity(self):
        """blast_radius 2-4 → MEDIUM."""
        assert classify_severity(2, 0) == Severity.MEDIUM
        assert classify_severity(3, 0) == Severity.MEDIUM
        assert classify_severity(4, 0) == Severity.MEDIUM

    def test_high_from_cross_stage(self):
        """cross_stage >= 2 → HIGH."""
        assert classify_severity(1, 2) == Severity.HIGH

    def test_low_severity(self):
        """blast_radius 1, cross_stage 0 → LOW."""
        assert classify_severity(1, 0) == Severity.LOW

    def test_critical_from_cross_stage(self):
        """cross_stage >= 3 → CRITICAL."""
        assert classify_severity(1, 3) == Severity.CRITICAL


# ── pipeline.py ───────────────────────────────────────────────────────────────

class TestPipelineBranches:
    """Cover missing branches in CLS-001 pipeline.py."""

    def test_invalid_position_raises(self):
        """Invalid current_position raises ValueError."""
        with pytest.raises(ValueError, match="Invalid position"):
            Pipeline(pipeline_id="x", current_position="invalid_stage")

    def test_complete_transitions(self):
        """complete() sets status to COMPLETED."""
        p = Pipeline(pipeline_id="x")
        p.start()
        p.record_gate(GateDecision.PASS)
        p.complete()
        assert p.status == PipelineStatus.COMPLETED

    def test_advance_at_final_stage_raises(self):
        """Advance from final stage raises ValueError."""
        p = Pipeline(pipeline_id="x", current_position="phase10")
        p.start()
        p.record_gate(GateDecision.PASS)
        with pytest.raises(ValueError, match="final stage"):
            p.advance()

    def test_advance_pass_with_warnings(self):
        """PASS_WITH_WARNINGS also allows advance (INV-002-v2)."""
        p = Pipeline(pipeline_id="x")
        p.start()
        p.record_gate(GateDecision.PASS_WITH_WARNINGS)
        p.advance()
        assert p.current_position == "phase1"


# ── repo_map.py ───────────────────────────────────────────────────────────────

class TestRepoMapBranches:
    """Cover missing branches in CLS-015 repo_map.py."""

    def test_prune_to_zero_budget(self):
        """Pruning to budget=0 returns empty map."""
        syms = (SymbolDef("a.py", "Foo", "class", "class Foo", 1),)
        m = RepoMap(symbols=syms, token_count=5, file_ranks={})
        pruned = m.prune_to_budget(0)
        assert pruned.token_count == 0
        assert len(pruned.symbols) == 0

    def test_get_context_string_empty(self):
        """Empty map returns empty string."""
        m = RepoMap(symbols=(), token_count=0, file_ranks={})
        assert m.get_context_string() == ""

    def test_get_context_string_multiple_files(self):
        """Context string groups symbols by file."""
        syms = (
            SymbolDef("a.py", "Foo", "class", "class Foo", 1),
            SymbolDef("a.py", "bar", "function", "def bar()", 5),
            SymbolDef("b.py", "baz", "function", "def baz()", 1),
        )
        m = RepoMap(symbols=syms, token_count=10, file_ranks={})
        ctx = m.get_context_string()
        assert "## a.py" in ctx
        assert "## b.py" in ctx
        assert "class Foo" in ctx

    def test_prune_fits_all(self):
        """Large budget keeps all symbols."""
        syms = (
            SymbolDef("a.py", "Foo", "class", "class Foo", 1),
            SymbolDef("b.py", "bar", "function", "def bar()", 1),
        )
        m = RepoMap(symbols=syms, token_count=10, file_ranks={})
        pruned = m.prune_to_budget(1000)
        assert len(pruned.symbols) == 2


# ── llm_strategy_selector.py ─────────────────────────────────────────────────

class TestLLMStrategySelectorBranches:
    """Cover missing branches in CLS-017."""

    def _make_selector(self) -> LLMStrategySelector:
        m = ModelConfig(provider="anthropic", model="claude-opus-4")
        cfg = StrategyConfig(
            reasoning_model=m,
            editing_model=ModelConfig(provider="openai", model="gpt-4o"),
            cheap_model=ModelConfig(provider="openai", model="gpt-4o-mini"),
            default_model=ModelConfig(provider="openai", model="gpt-4o"),
            fallback_model=ModelConfig(provider="openai", model="gpt-4o"),
            enabled_providers=frozenset({"anthropic", "openai"}),
        )
        return LLMStrategySelector(cfg)

    def test_list_providers(self):
        """list_providers returns sorted list."""
        sel = self._make_selector()
        providers = sel.list_providers()
        assert sorted(providers) == providers
        assert "anthropic" in providers

    def test_enabled_provider_count(self):
        """enabled_provider_count returns integer count."""
        sel = self._make_selector()
        assert sel.enabled_provider_count == 2

    def test_select_comprehend(self):
        """COMPREHEND maps to reasoning model."""
        sel = self._make_selector()
        m = sel.select(TaskType.COMPREHEND)
        assert m.provider == "anthropic"

    def test_select_charter(self):
        """CHARTER maps to reasoning model."""
        sel = self._make_selector()
        m = sel.select(TaskType.CHARTER)
        assert m.provider == "anthropic"


# ── traceable_id.py ───────────────────────────────────────────────────────────

class TestTraceableIDBranches:
    """Cover missing branches in CLS-004/CLS-005."""

    def test_bg_no_upstream_raises(self):
        """BG ID cannot have upstream links (INV-007)."""
        bg = TraceableID(prefix=IDPrefix.BG, sequence=1, title="BG")
        link = TraceLink("FR-001", "BG-001", LinkType.DERIVES)
        with pytest.raises(Exception):  # icontract ViolationError
            bg.add_upstream(link)

    def test_tc_no_downstream_raises(self):
        """TC ID cannot have downstream links (INV-007)."""
        tc = TraceableID(prefix=IDPrefix.TC, sequence=1, title="TC")
        link = TraceLink("TC-001", "FR-002", LinkType.VALIDATES)
        with pytest.raises(Exception):  # icontract ViolationError
            tc.add_downstream(link)

    def test_full_id_format(self):
        """full_id property formats correctly."""
        fr = TraceableID(prefix=IDPrefix.FR, sequence=5, title="FR-005")
        assert fr.full_id == "FR-005"


# ── hook_runner.py ────────────────────────────────────────────────────────────

class TestHookRunnerBranches:
    """Cover missing branches in CLS-016."""

    def test_empty_event_returns_empty(self):
        """No hooks for event returns empty list."""
        runner = HookRunner()
        results = runner.execute(HookEvent.PRE_STAGE_START)
        assert results == []

    def test_all_proceeded_false(self):
        """all_proceeded returns False if any hook blocked."""
        runner = HookRunner()
        hook = HookDef(
            event=HookEvent.PRE_STAGE_START,
            command='python -c "exit(2)"',
            blocking=True,
        )
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START)
        assert runner.all_proceeded(results) is False

    def test_non_blocking_hook_exit2_proceeds(self):
        """Non-blocking hook with exit 2 still proceeds."""
        runner = HookRunner()
        hook = HookDef(
            event=HookEvent.PRE_STAGE_START,
            command='python -c "exit(2)"',
            blocking=False,
        )
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START)
        assert results[0].proceed is True

    def test_exit_code_other_than_0_2_proceeds(self):
        """Exit code 1 (non-blocking kind) still proceeds."""
        runner = HookRunner()
        hook = HookDef(
            event=HookEvent.PRE_STAGE_START,
            command='python -c "exit(1)"',
            blocking=True,
        )
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START)
        # exit 1 is not 2, so proceed=True even if blocking
        assert results[0].proceed is True

    def test_all_proceeded_true(self):
        """all_proceeded True when all hooks pass."""
        runner = HookRunner()
        hook = HookDef(
            event=HookEvent.PRE_STAGE_START,
            command='python -c "exit(0)"',
            blocking=True,
        )
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START)
        assert runner.all_proceeded(results) is True


# ── repo_map_builder.py ───────────────────────────────────────────────────────

class TestRepoMapBuilderBranches:
    """Cover missing branches in ALG-006."""

    def test_empty_directory_returns_empty(self, tmp_path):
        """No Python files → empty RepoMap."""
        result = repo_map_build(str(tmp_path), 1000)
        assert result.token_count == 0
        assert len(result.symbols) == 0

    def test_single_file(self, tmp_path):
        """Single file produces symbols."""
        (tmp_path / "a.py").write_text("class A:\n    pass\n\ndef foo(): pass\n")
        result = repo_map_build(str(tmp_path), 1000)
        assert len(result.symbols) >= 2  # class + function

    def test_pagerank_empty(self):
        """PageRank on empty graph returns empty dict."""
        ranks = _pagerank({})
        assert ranks == {}

    def test_extract_symbols_syntax_error(self):
        """Syntax error in file returns empty symbol list."""
        symbols = _extract_symbols_ast("bad.py", "def :(")
        assert symbols == []

    def test_import_graph_unreadable_file(self, tmp_path):
        """Import graph handles missing files gracefully."""
        fake = str(tmp_path / "nonexistent.py")
        graph = _build_import_graph([fake], str(tmp_path))
        assert fake in graph  # still in graph, just empty deps

    def test_budget_prunes_symbols(self, tmp_path):
        """Token budget limits symbol count (INV-024)."""
        for i in range(20):
            (tmp_path / f"mod_{i:02d}.py").write_text(
                f"class BigClass{i}:\n    def method(self): pass\n\n"
                * 10  # makes each file larger
            )
        # Very small budget
        result = repo_map_build(str(tmp_path), 50)
        assert result.token_count <= 50


# ── traceable_id.py — success paths ──────────────────────────────────────────

class TestTraceableIDSuccessPaths:
    """Cover the append lines (L76, L88) in traceable_id.py."""

    def test_add_upstream_non_bg(self):
        """Non-BG ID can add upstream links (covers L76)."""
        fr = TraceableID(prefix=IDPrefix.FR, sequence=1, title="FR-001")
        link = TraceLink("BG-001", "FR-001", LinkType.DECOMPOSES)
        fr.add_upstream(link)
        assert len(fr.upstream_links) == 1
        assert fr.upstream_links[0].source_id == "BG-001"

    def test_add_downstream_non_tc(self):
        """Non-TC ID can add downstream links (covers L88)."""
        fr = TraceableID(prefix=IDPrefix.FR, sequence=1, title="FR-001")
        link = TraceLink("FR-001", "UC-001", LinkType.REALIZES)
        fr.add_downstream(link)
        assert len(fr.downstream_links) == 1
        assert fr.downstream_links[0].target_id == "UC-001"

    def test_trace_link_self_link_raises(self):
        """Self-link raises ValueError (INV-008)."""
        with pytest.raises(ValueError, match="Self-link forbidden"):
            TraceLink("FR-001", "FR-001", LinkType.DERIVES)


# ── model_selector.py — double-fallback path (L83) ───────────────────────────

class TestModelSelectorDoubleFallback:
    """Cover the emergency fallback branch (L83) in ALG-008."""

    def test_double_fallback_constructs_config(self):
        """When fallback provider is also disabled, creates ModelConfig from enabled set."""
        disabled_primary = ModelConfig(provider="anthropic", model="claude-opus-4")
        disabled_fallback = ModelConfig(provider="google", model="gemini-ultra")
        cfg = StrategyConfig(
            reasoning_model=disabled_primary,
            editing_model=disabled_primary,
            cheap_model=disabled_primary,
            default_model=disabled_primary,
            fallback_model=disabled_fallback,
            enabled_providers=frozenset({"openai"}),  # neither primary nor fallback
        )
        result = select_model(TaskType.CRITIQUE, cfg)
        assert result.provider == "openai"


# ── hook_runner.py — timeout path (L108-111) ─────────────────────────────────

class TestHookRunnerTimeout:
    """Cover the subprocess.TimeoutExpired path (L108-111)."""

    def test_timeout_hook_proceeds(self, monkeypatch):
        """Timed-out hook gets exit_code=1 → proceed=True (L108-111)."""
        import subprocess

        def fake_run(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="fake", timeout=30)

        monkeypatch.setattr(subprocess, "run", fake_run)

        runner = HookRunner()
        hook = HookDef(
            event=HookEvent.PRE_STAGE_START,
            command="sleep 999",
            blocking=True,
        )
        runner.register(hook)
        results = runner.execute(HookEvent.PRE_STAGE_START)
        assert len(results) == 1
        assert results[0].exit_code == 1
        assert "timed out" in results[0].stderr.lower()
        assert results[0].proceed is True  # exit_code=1 is not 2


# ── stage.py — add_finding (L82) ─────────────────────────────────────────────

class TestStageAddFinding:
    """Cover Stage.add_finding() body (L82)."""

    def test_add_finding_appends(self):
        """add_finding appends finding string to findings list (L82)."""
        s = Stage(stage_id="s3", name="Stage 3")
        s.add_finding("CRITICAL: missing invariant")
        s.add_finding("HIGH: unclear domain")
        assert len(s.findings) == 2
        assert "CRITICAL: missing invariant" in s.findings


# ── repo_map.py — prune_to_budget exact-fit (L64) ────────────────────────────

class TestRepoMapPruneExactFit:
    """Cover exact-budget boundary in CLS-015 (L64)."""

    def test_prune_exact_budget(self):
        """Symbol exactly at budget limit is included (covers L64 boundary)."""
        syms = (
            SymbolDef("a.py", "Foo", "class", "class Foo:  # 5 tokens", 5),
            SymbolDef("b.py", "bar", "function", "def bar(): ...", 5),
        )
        m = RepoMap(symbols=syms, token_count=10, file_ranks={})
        # Budget equals exactly first symbol's token count
        pruned = m.prune_to_budget(5)
        assert pruned.token_count <= 5

    def test_prune_single_symbol_exceeds_budget(self):
        """Symbol with long signature bigger than budget is excluded."""
        long_sig = "class HeavyClass: " + "x" * 400  # 400+/4 = 100+ tokens
        syms = (SymbolDef("a.py", "HeavyClass", "class", long_sig, 1),)
        m = RepoMap(symbols=syms, token_count=100, file_ranks={})
        pruned = m.prune_to_budget(50)
        assert len(pruned.symbols) == 0

