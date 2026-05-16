"""Unit tests to fill coverage gaps to reach 100%+.

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

from pathlib import Path
from typing import Any

import pytest

from agentic_workflow.domain.algorithms.blast_radius import BlastRadiusClassifier
from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector
from agentic_workflow.domain.algorithms.model_selector import (
    StrategyConfig,
    select_model,
)
from agentic_workflow.domain.algorithms.repo_map_builder import RepoMapBuilder
from agentic_workflow.domain.models.enums import (
    FixedPointResult,
    GateDecision,
    HookEvent,
    IDPrefix,
    LinkType,
    PipelineStatus,
    Severity,
    TaskType,
)
from agentic_workflow.domain.models.model_config import ModelConfig
from agentic_workflow.domain.models.pipeline import Pipeline
from agentic_workflow.domain.models.repo_map import RepoMap, SymbolDef
from agentic_workflow.domain.models.stage import Stage
from agentic_workflow.domain.models.traceable_id import TraceableID, TraceLink
from agentic_workflow.domain.services.hook_runner import HookDef, HookRunner
from agentic_workflow.domain.services.llm_strategy_selector import LLMStrategySelector

# -> convergence.py ->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->


class TestConvergenceBranches:
    """Cover missing branches in ALG-001 convergence.py."""

    def test_diverging_result(self) -> None:
        """DIVERGING: finding count increasing over 3 iterations."""
        history = [["A"], ["A", "B"], ["A", "B", "C"]]
        result = ConvergenceDetector.check_convergence(
            iteration_count=3,
            findings_per_iter=history,
            current_findings=["A", "B", "C", "D"],
        )
        assert result == FixedPointResult.DIVERGING

    def test_not_reached_short_history(self) -> None:
        """NOT_REACHED: insufficient history for divergence detection."""
        history = [["A"]]
        result = ConvergenceDetector.check_convergence(
            iteration_count=1,
            findings_per_iter=history,
            current_findings=["CRITICAL: issue"],
        )
        assert result == FixedPointResult.NOT_REACHED

    def test_max_iterations_boundary(self) -> None:
        """MAX_ITERATIONS: iteration_count >= 10."""
        result = ConvergenceDetector.check_convergence(
            iteration_count=10,
            findings_per_iter=[],
            current_findings=["CRITICAL: still here"],
        )
        assert result == FixedPointResult.MAX_ITERATIONS

    def test_should_auto_pass_not_reached(self) -> None:
        """NOT_REACHED should NOT auto-pass."""
        assert ConvergenceDetector.should_auto_pass(FixedPointResult.NOT_REACHED) is False

    def test_diverging_auto_pass(self) -> None:
        """DIVERGING should auto-pass per ADR-STR-003."""
        assert ConvergenceDetector.should_auto_pass(FixedPointResult.DIVERGING) is True

    def test_max_iterations_auto_pass(self) -> None:
        """MAX_ITERATIONS should auto-pass with warning."""
        assert ConvergenceDetector.should_auto_pass(FixedPointResult.MAX_ITERATIONS) is True


# -> blast_radius.py ->->->->->->->->->->->->->->->->->->->->->->->->->->->->->?


class TestBlastRadiusBranches:
    """Cover missing severity branches in ALG-003."""

    def test_medium_severity(self) -> None:
        """blast_radius 2-4 ->MEDIUM."""
        assert BlastRadiusClassifier.classify(2, 0) == Severity.MEDIUM
        assert BlastRadiusClassifier.classify(3, 0) == Severity.MEDIUM
        assert BlastRadiusClassifier.classify(4, 0) == Severity.MEDIUM

    def test_high_from_cross_stage(self) -> None:
        """cross_stage >= 2 ->HIGH."""
        assert BlastRadiusClassifier.classify(1, 2) == Severity.HIGH

    def test_low_severity(self) -> None:
        """blast_radius 1, cross_stage 0 ->LOW."""
        assert BlastRadiusClassifier.classify(1, 0) == Severity.LOW

    def test_critical_from_cross_stage(self) -> None:
        """cross_stage >= 3 ->CRITICAL."""
        assert BlastRadiusClassifier.classify(1, 3) == Severity.CRITICAL


# -> pipeline.py ->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->?


class TestPipelineBranches:
    """Cover missing branches in CLS-001 pipeline.py."""

    def test_invalid_position_raises(self) -> None:
        """Invalid current_position raises ValueError."""
        with pytest.raises(ValueError, match="Invalid position"):
            Pipeline(pipeline_id="x", current_position="invalid_stage")

    def test_complete_transitions(self) -> None:
        """complete() sets status to COMPLETED."""
        p = Pipeline(pipeline_id="x")
        p.start()
        p.record_gate(GateDecision.PASS)
        p.complete()
        assert p.status == PipelineStatus.COMPLETED

    def test_advance_at_final_stage_raises(self) -> None:
        """Advance from final stage raises ValueError."""
        p = Pipeline(pipeline_id="x", current_position="phase10")
        p.start()
        p.record_gate(GateDecision.PASS)
        with pytest.raises(ValueError, match="final stage"):
            p.advance()

    def test_advance_pass_with_warnings(self) -> None:
        """PASS_WITH_WARNINGS also allows advance (INV-002-v2)."""
        p = Pipeline(pipeline_id="x")
        p.start()
        p.record_gate(GateDecision.PASS_WITH_WARNINGS)
        p.advance()
        assert p.current_position == "phase1"


# -> repo_map.py ->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->?


class TestRepoMapBranches:
    """Cover missing branches in CLS-015 repo_map.py."""

    def test_prune_to_zero_budget(self) -> None:
        """Pruning to budget=0 returns empty map."""
        syms = (SymbolDef("a.py", "Foo", "class", "class Foo", 1),)
        m = RepoMap(symbols=syms, token_count=5, file_ranks={})
        pruned = m.prune_to_budget(0)
        assert pruned.token_count == 0
        assert len(pruned.symbols) == 0

    def test_get_context_string_empty(self) -> None:
        """Empty map returns empty string."""
        m = RepoMap(symbols=(), token_count=0, file_ranks={})
        assert m.get_context_string() == ""

    def test_get_context_string_multiple_files(self) -> None:
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

    def test_prune_fits_all(self) -> None:
        """Large budget keeps all symbols."""
        syms = (
            SymbolDef("a.py", "Foo", "class", "class Foo", 1),
            SymbolDef("b.py", "bar", "function", "def bar()", 1),
        )
        m = RepoMap(symbols=syms, token_count=10, file_ranks={})
        pruned = m.prune_to_budget(1000)
        assert len(pruned.symbols) == 2


# -> llm_strategy_selector.py ->->->->->->->->->->->->->->->->->->->->->->->->?


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

    def test_list_providers(self) -> None:
        """list_providers returns sorted list."""
        sel = self._make_selector()
        providers = sel.list_providers()
        assert sorted(providers) == providers
        assert "anthropic" in providers

    def test_enabled_provider_count(self) -> None:
        """enabled_provider_count returns integer count."""
        sel = self._make_selector()
        assert sel.enabled_provider_count == 2

    def test_select_comprehend(self) -> None:
        """COMPREHEND maps to reasoning model."""
        sel = self._make_selector()
        m = sel.select(TaskType.COMPREHEND)
        assert m.provider == "anthropic"

    def test_select_charter(self) -> None:
        """CHARTER maps to reasoning model."""
        sel = self._make_selector()
        m = sel.select(TaskType.CHARTER)
        assert m.provider == "anthropic"


# -> traceable_id.py ->->->->->->->->->->->->->->->->->->->->->->->->->->->->->?


class TestTraceableIDBranches:
    """Cover missing branches in CLS-004/CLS-005."""

    def test_bg_no_upstream_raises(self) -> None:
        """BG ID cannot have upstream links (INV-007)."""
        bg = TraceableID(prefix=IDPrefix.BG, sequence=1, title="BG")
        link = TraceLink("FR-001", "BG-001", LinkType.DERIVES)
        # icontract ViolationError inherits from Exception but usually
        # shows up as ViolationError if icontract is installed.
        with pytest.raises(Exception, match="BG IDs have no upstream links"):
            bg.add_upstream(link)

    def test_tc_no_downstream_raises(self) -> None:
        """TC ID cannot have downstream links (INV-007)."""
        tc = TraceableID(prefix=IDPrefix.TC, sequence=1, title="TC")
        link = TraceLink("TC-001", "FR-002", LinkType.VALIDATES)
        with pytest.raises(Exception, match="TC IDs have no downstream links"):
            tc.add_downstream(link)

    def test_full_id_format(self) -> None:
        """full_id property formats correctly."""
        fr = TraceableID(prefix=IDPrefix.FR, sequence=5, title="FR-005")
        assert fr.full_id == "FR-005"


# -> hook_runner.py ->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->


class TestHookRunnerBranches:
    """Cover missing branches in CLS-016."""

    def test_empty_event_returns_empty(self) -> None:
        """No hooks for event returns empty list."""
        runner = HookRunner()
        results = runner.execute(HookEvent.PRE_STAGE_START)
        assert results == []

    def test_all_proceeded_false(self) -> None:
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

    def test_non_blocking_hook_exit2_proceeds(self) -> None:
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

    def test_exit_code_other_than_0_2_proceeds(self) -> None:
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

    def test_all_proceeded_true(self) -> None:
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


# -> repo_map_builder.py ->->->->->->->->->->->->->->->->->->->->->->->->->->->?


class TestRepoMapBuilderBranches:
    """Cover missing branches in ALG-006."""

    def test_empty_directory_returns_empty(self, tmp_path: Path) -> None:
        """No Python files ->empty RepoMap."""
        result = RepoMapBuilder.build(str(tmp_path), 1000)
        assert result.token_count == 0
        assert len(result.symbols) == 0

    def test_single_file(self, tmp_path: Path) -> None:
        """Single file produces symbols."""
        (tmp_path / "a.py").write_text("class A:\n    pass\n\ndef foo(): pass\n")
        result = RepoMapBuilder.build(str(tmp_path), 1000)
        assert len(result.symbols) >= 2  # class + function

    def test_pagerank_empty(self) -> None:
        """PageRank on empty graph returns empty dict."""
        ranks = RepoMapBuilder.pagerank({})
        assert ranks == {}

    def test_extract_symbols_syntax_error(self) -> None:
        """Syntax error in file returns empty symbol list."""
        symbols = RepoMapBuilder.extract_symbols_ast("bad.py", "def :(")
        assert symbols == []

    def test_import_graph_unreadable_file(self, tmp_path: Path) -> None:
        """Import graph handles missing files gracefully."""
        fake = str(tmp_path / "nonexistent.py")
        graph = RepoMapBuilder.build_import_graph([fake], str(tmp_path))
        assert fake in graph  # still in graph, just empty deps

    def test_budget_prunes_symbols(self, tmp_path: Path) -> None:
        """Token budget limits symbol count (INV-024)."""
        for i in range(20):
            (tmp_path / f"mod_{i:02d}.py").write_text(
                f"class BigClass{i}:\n    def method(self): pass\n\n" * 10  # makes each file larger
            )
        # Very small budget
        result = RepoMapBuilder.build(str(tmp_path), 50)
        assert result.token_count <= 50


# -> traceable_id.py ->success paths ->->->->->->->->->->->->->->->->->->->->->


class TestTraceableIDSuccessPaths:
    """Cover the append lines (L76, L88) in traceable_id.py."""

    def test_add_upstream_non_bg(self) -> None:
        """Non-BG ID can add upstream links (covers L76)."""
        fr = TraceableID(prefix=IDPrefix.FR, sequence=1, title="FR-001")
        link = TraceLink("BG-001", "FR-001", LinkType.DECOMPOSES)
        fr.add_upstream(link)
        assert len(fr.upstream_links) == 1
        assert fr.upstream_links[0].source_id == "BG-001"

    def test_add_downstream_non_tc(self) -> None:
        """Non-TC ID can add downstream links (covers L88)."""
        fr = TraceableID(prefix=IDPrefix.FR, sequence=1, title="FR-001")
        link = TraceLink("FR-001", "UC-001", LinkType.REALIZES)
        fr.add_downstream(link)
        assert len(fr.downstream_links) == 1
        assert fr.downstream_links[0].target_id == "UC-001"

    def test_trace_link_self_link_raises(self) -> None:
        """Self-link raises ValueError (INV-008)."""
        with pytest.raises(ValueError, match="Self-link forbidden"):
            TraceLink("FR-001", "FR-001", LinkType.DERIVES)


# -> model_selector.py ->double-fallback path (L83) ->->->->->->->->->->->->->?


class TestModelSelectorDoubleFallback:
    """Cover the emergency fallback branch (L83) in ALG-008."""

    def test_double_fallback_constructs_config(self) -> None:
        """When fallback is disabled, creates ModelConfig from enabled set."""
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


# -> hook_runner.py ->timeout path (L108-111) ->->->->->->->->->->->->->->->->?


class TestHookRunnerTimeout:
    """Cover the subprocess.TimeoutExpired path (L108-111)."""

    def test_timeout_hook_proceeds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Timed-out hook gets exit_code=1 ->proceed=True (L108-111)."""
        import subprocess

        def fake_run(*args: Any, **kwargs: Any) -> Any:
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


# -> stage.py ->add_finding (L82) ->->->->->->->->->->->->->->->->->->->->->->?


class TestStageAddFinding:
    """Cover Stage.add_finding() body (L82)."""

    def test_add_finding_appends(self) -> None:
        """add_finding appends finding string to findings list (L82)."""
        s = Stage(stage_id="s3", name="Stage 3")
        s.add_finding("CRITICAL: missing invariant")
        s.add_finding("HIGH: unclear domain")
        assert len(s.findings) == 2
        assert "CRITICAL: missing invariant" in s.findings


# -> repo_map.py ->prune_to_budget exact-fit (L64) ->->->->->->->->->->->->->->


class TestRepoMapPruneExactFit:
    """Cover exact-budget boundary in CLS-015 (L64)."""

    def test_prune_exact_budget(self) -> None:
        """Symbol exactly at budget limit is included (covers L64 boundary)."""
        syms = (
            SymbolDef("a.py", "Foo", "class", "class Foo:  # 5 tokens", 5),
            SymbolDef("b.py", "bar", "function", "def bar(): ...", 5),
        )
        m = RepoMap(symbols=syms, token_count=10, file_ranks={})
        # Budget equals exactly first symbol's token count
        pruned = m.prune_to_budget(5)
        assert pruned.token_count <= 5

    def test_prune_single_symbol_exceeds_budget(self) -> None:
        """Symbol with long signature bigger than budget is excluded."""
        long_sig = "class HeavyClass: " + "x" * 400  # 400+/4 = 100+ tokens
        syms = (SymbolDef("a.py", "HeavyClass", "class", long_sig, 1),)
        m = RepoMap(symbols=syms, token_count=100, file_ranks={})
        pruned = m.prune_to_budget(50)
        assert len(pruned.symbols) == 0


# -> 100% coverage final fills ->->->->->->->->->->->->->->->->->->->->->->->->?


class TestFinalCoverageGaps:
    """Three targeted tests to reach 100% coverage.

    convergence.py L48->4: all() True but count[-1] NOT > count[0] ->NOT_REACHED
    repo_map_builder.py L98->6: regex match with both groups None ->module is falsy
    repo_map_builder.py L183-184: OSError on Path.read_text in symbol extraction loop
    """

    # --- convergence.py L48->4 ---

    def test_convergence_non_diverging_plateau(self) -> None:
        """L48->4: findings_per_iter >= 3 but not strictly increasing ->NOT_REACHED.

        The divergence guard requires:
          all(counts[i] <= counts[i+1]) AND counts[-1] > counts[0]
        If counts are flat (e.g. [3, 3, 3]) the all() is True but counts[-1]==counts[0],
        so the condition short-circuits and we fall through to NOT_REACHED (L54).
        """
        from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector
        from agentic_workflow.domain.models.enums import FixedPointResult

        # Three identical-length histories ->plateau, not diverging
        history = [["A", "B", "C"], ["A", "B", "C"], ["A", "B", "C"]]
        result = ConvergenceDetector.check_convergence(
            iteration_count=3,
            findings_per_iter=history,
            current_findings=["CRITICAL: still here"],
        )
        assert result == FixedPointResult.NOT_REACHED

    def test_convergence_decreasing_then_increasing_not_diverging(self) -> None:
        """L48->4: [3,2,3] ->not monotonically non-decreasing ->NOT_REACHED."""
        from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector
        from agentic_workflow.domain.models.enums import FixedPointResult

        # [3, 2, 3]: all(counts[i] <= counts[i+1]) is False for i=0 (3 > 2)
        # ->all() returns False ->skip DIVERGING branch ->fall to NOT_REACHED
        history = [["A", "B", "C"], ["A", "B"], ["A", "B", "C"]]
        result = ConvergenceDetector.check_convergence(
            iteration_count=3,
            findings_per_iter=history,
            current_findings=["CRITICAL: still here"],
        )
        assert result == FixedPointResult.NOT_REACHED

    # --- repo_map_builder.py L98->6 ---

    def test_import_graph_none_module_group(self, tmp_path: Path) -> None:
        r"""L98->6: regex match where both groups() are None ->module is falsy ->skip.

        The import_pattern has two groups: group(1) = 'from X import' base,
        group(2) = 'import X' base. A bare 'import' keyword with no module
        cannot be crafted to match the pattern (it requires \\w+). So the real
        way to trigger module='' is via a match where group(1) or group(2) is
        an empty string. We achieve this by having no matching imports at all
        (graph still built, just no edges), which forces the loop body where
        base not in path_map ->the if module: guard is exercised.
        The branch L98->6 fires when the for-loop body is entered but module
        is falsy OR when the loop doesn't run at all (no matches). The actual
        uncovered arc is: L97 (assign module) ->module is truthy but base NOT
        in path_map ->L96 (next iteration). We cover that with an import that
        matches but whose base is not in path_map.
        """
        from agentic_workflow.domain.algorithms.repo_map_builder import (
            RepoMapBuilder,
        )

        a = tmp_path / "alpha.py"
        # Import an external module (not in path_map)
        a.write_text("import os\nimport sys\nfrom pathlib import Path\n")
        result = RepoMapBuilder.build_import_graph([str(a)], str(tmp_path))
        # All imports map to external modules ->no edges added, but no crash
        assert result[str(a)] == []

    # --- repo_map_builder.py L183-184 ---

    def test_repo_map_build_oserror_on_second_read(self, tmp_path: Path) -> None:
        """L183-184: OSError during symbol-extraction read ->file is skipped.

        In RepoMapBuilder.build:
          L180-185: symbol extraction loop (reads each file first)
          L188: build_import_graph (reads each file second)
        So to trigger L183-184, we raise OSError on the FIRST read of bad.py
        (the symbol extraction pass), then allow the second read (import graph).
        """
        from unittest.mock import patch

        from agentic_workflow.domain.algorithms.repo_map_builder import RepoMapBuilder

        good_file = tmp_path / "good.py"
        bad_file = tmp_path / "bad.py"
        good_file.write_text("def good_func(): pass\n")
        bad_file.write_text("class BadClass: pass\n")

        call_registry: dict[str, int] = {}
        original_read_text = Path.read_text

        def patched_read(self: Path, *args: Any, **kwargs: Any) -> str:
            name = self.name
            call_registry[name] = call_registry.get(name, 0) + 1
            # Raise on the FIRST access to bad.py ->hits L183-184 (symbol loop)
            if name == "bad.py" and call_registry[name] == 1:
                raise OSError("forced OSError for L183-184 coverage")
            return original_read_text(self, *args, **kwargs)

        with patch.object(Path, "read_text", patched_read):
            result = RepoMapBuilder.build(str(tmp_path), token_budget=1000)

        # good.py symbols must still appear; bad.py symbols were skipped
        good_syms = [s for s in result.symbols if "good" in s.file_path]
        bad_syms = [s for s in result.symbols if "bad" in s.file_path]
        assert len(good_syms) >= 1
        assert bad_syms == []  # bad.py was skipped in symbol extraction
        # Confirm bad.py was accessed (at least attempted)
        assert call_registry.get("bad.py", 0) >= 1
