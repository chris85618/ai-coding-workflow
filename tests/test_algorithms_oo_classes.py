"""Tests for OO class interfaces — verifies ALG-010 OO mandate compliance.

All algorithms must be accessible as class methods, not just module-level functions.
This file validates the class-level API while existing tests validate
backward-compat facades.

Traceable to: ALG-010 (OO mandate), FR-001..FR-030.
"""

from typing import Any

import pytest

from agentic_workflow.domain.models.enums import (
    FixedPointResult,
    Severity,
    TaskType,
)
from agentic_workflow.domain.models.model_config import ModelConfig
from agentic_workflow.domain.models.repo_map import RepoMap


# ── ConvergenceDetector ────────────────────────────────────────────────────────
class TestConvergenceDetector:
    """ALG-001 OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector

        self.cls = ConvergenceDetector

    def test_class_constants_exist(self) -> None:
        """TC-166: Convergence constants check."""
        assert self.cls.MAX_ITERATIONS == 10
        assert self.cls.DIVERGENCE_WINDOW == 3

    def test_all_yagni_returns_reached(self) -> None:
        """TC-167: All YAGNI convergence."""
        result = self.cls.check_convergence(0, [], ["YAGNI: ok", "YAGNI: fine"])
        assert result == FixedPointResult.REACHED

    def test_max_iterations_returns_max_iterations(self) -> None:
        """TC-168: Max iterations reached."""
        result = self.cls.check_convergence(10, [], ["issue"])
        assert result == FixedPointResult.MAX_ITERATIONS

    def test_diverging_detection(self) -> None:
        """TC-169: Divergence detection."""
        findings_per_iter = [["a"], ["a", "b"], ["a", "b", "c"]]
        result = self.cls.check_convergence(3, findings_per_iter, ["a", "b", "c", "d"])
        assert result == FixedPointResult.DIVERGING

    def test_not_reached_when_not_all_yagni(self) -> None:
        """TC-170: Convergence not reached."""
        result = self.cls.check_convergence(0, [], ["CRITICAL: issue"])
        assert result == FixedPointResult.NOT_REACHED

    def test_should_auto_pass_reached(self) -> None:
        """TC-171: Auto-pass on REACHED."""
        assert self.cls.should_auto_pass(FixedPointResult.REACHED) is True

    def test_should_auto_pass_diverging(self) -> None:
        """TC-172: Auto-pass on DIVERGING."""
        assert self.cls.should_auto_pass(FixedPointResult.DIVERGING) is True

    def test_should_auto_pass_max_iterations(self) -> None:
        """TC-173: Auto-pass on MAX_ITERATIONS."""
        assert self.cls.should_auto_pass(FixedPointResult.MAX_ITERATIONS) is True

    def test_should_not_pass_not_reached(self) -> None:
        """TC-174: No auto-pass on NOT_REACHED."""
        assert self.cls.should_auto_pass(FixedPointResult.NOT_REACHED) is False


# ── BlastRadiusClassifier ──────────────────────────────────────────────────────
class TestBlastRadiusClassifier:
    """ALG-003 OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        from agentic_workflow.domain.algorithms.blast_radius import (
            BlastRadiusClassifier,
        )

        self.cls = BlastRadiusClassifier

    def test_class_constants_exist(self) -> None:
        """TC-175: Blast constants check."""
        assert self.cls.CRITICAL_RADIUS == 10
        assert self.cls.HIGH_RADIUS == 5
        assert self.cls.MEDIUM_RADIUS == 2

    def test_zero_blast_radius_is_cosmetic(self) -> None:
        """TC-176: Zero blast is COSMETIC."""
        assert self.cls.classify(0, 0) == Severity.COSMETIC

    def test_critical_by_radius(self) -> None:
        """TC-177: Critical by radius."""
        assert self.cls.classify(10, 0) == Severity.CRITICAL

    def test_critical_by_stages(self) -> None:
        """TC-178: Critical by stages."""
        assert self.cls.classify(1, 3) == Severity.CRITICAL

    def test_high_by_radius(self) -> None:
        """TC-179: High by radius."""
        assert self.cls.classify(5, 0) == Severity.HIGH

    def test_high_by_stages(self) -> None:
        """TC-180: High by stages."""
        assert self.cls.classify(1, 2) == Severity.HIGH

    def test_medium(self) -> None:
        """TC-181: Medium severity."""
        assert self.cls.classify(2, 0) == Severity.MEDIUM

    def test_low(self) -> None:
        """TC-182: Low severity."""
        assert self.cls.classify(1, 0) == Severity.LOW


# ── RiceScorer ─────────────────────────────────────────────────────────────────
class TestRiceScorer:
    """ALG-004 OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        from agentic_workflow.domain.algorithms.rice_scoring import RiceScorer

        self.cls = RiceScorer

    def test_class_constants_exist(self) -> None:
        """TC-183: RICE constants check."""
        assert 0.5 in self.cls.VALID_IMPACT_VALUES
        assert self.cls.REACH_MIN == 1
        assert self.cls.REACH_MAX == 100

    def test_score_formula(self) -> None:
        """TC-184: RICE formula check."""
        result = self.cls.score(10, 2.0, 1.0, 5.0)
        assert abs(result - 4.0) < 1e-9

    def test_score_half_impact(self) -> None:
        """TC-185: Half impact RICE score."""
        result = self.cls.score(100, 0.5, 0.5, 1.0)
        assert abs(result - 25.0) < 1e-9

    def test_invalid_effort_raises(self) -> None:
        """TC-186: Invalid effort detection."""
        import icontract

        with pytest.raises(icontract.ViolationError):
            self.cls.score(10, 2.0, 1.0, 0)

    def test_invalid_reach_raises(self) -> None:
        """TC-187: Invalid reach detection."""
        import icontract

        with pytest.raises(icontract.ViolationError):
            self.cls.score(0, 2.0, 1.0, 1.0)

    def test_invalid_impact_raises(self) -> None:
        """TC-188: Invalid impact detection."""
        import icontract

        with pytest.raises(icontract.ViolationError):
            self.cls.score(10, 1.5, 1.0, 1.0)

    def test_invalid_confidence_raises(self) -> None:
        """TC-189: Invalid confidence detection."""
        import icontract

        with pytest.raises(icontract.ViolationError):
            self.cls.score(10, 2.0, 0.1, 1.0)


# ── ContextBudgetAllocator ─────────────────────────────────────────────────────
class TestContextBudgetAllocator:
    """ALG-007 OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        from agentic_workflow.domain.algorithms.context_budget import (
            ContextBudgetAllocator,
        )

        self.cls = ContextBudgetAllocator

    def test_class_constants_exist(self) -> None:
        """TC-190: Budget constants check."""
        assert self.cls.CHARS_PER_TOKEN == 4
        assert self.cls.TASK_BUDGET_FRACTION == 0.5
        assert self.cls.FILES_BUDGET_FRACTION == 0.7

    def test_estimate_tokens_minimum_one(self) -> None:
        """TC-191: Minimum token estimation."""
        assert self.cls.estimate_tokens("") == 1

    def test_estimate_tokens_calculation(self) -> None:
        """TC-192: Token calculation logic."""
        text = "a" * 400
        assert self.cls.estimate_tokens(text) == 100

    def test_allocate_respects_budget(self) -> None:
        """TC-193: Budget allocation logic."""
        from agentic_workflow.domain.models.repo_map import RepoMap

        repo_map = RepoMap(symbols=(), token_count=0, file_ranks={})
        result = self.cls.allocate(1000, repo_map, [], "hello world task context")
        assert result.total_tokens <= 1000

    def test_allocate_invalid_budget_raises(self) -> None:
        """TC-194: Zero budget detection."""
        import icontract

        from agentic_workflow.domain.models.repo_map import RepoMap

        with pytest.raises(icontract.ViolationError):
            self.cls.allocate(
                0, RepoMap(symbols=(), token_count=0, file_ranks={}), [], "task"
            )


# ── PipelineCompletenessChecker ────────────────────────────────────────────────
class TestPipelineCompletenessChecker:
    """Pipeline completeness OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        from agentic_workflow.domain.algorithms.pipeline_completeness import (
            PipelineCompletenessChecker,
        )

        self.cls = PipelineCompletenessChecker

    def test_empty_dir_returns_zero_score(self, tmp_path: Any) -> None:
        """TC-195: Empty directory score check."""
        checker = self.cls(tmp_path)
        result = checker.calculate()
        assert result["completeness_score"] == 0
        assert result["completeness_ratio"] == 0.0

    def test_greenfield_path_with_no_src(self, tmp_path: Any) -> None:
        """TC-196: Path A detection."""
        checker = self.cls(tmp_path)
        result = checker.calculate()
        assert result["decision"] == "Path A (Greenfield)"

    def test_brownfield_path_with_src(self, tmp_path: Any) -> None:
        """TC-197: Path B detection."""
        src = tmp_path / "src" / "main.py"
        src.parent.mkdir(parents=True)
        src.write_text("# code")
        checker = self.cls(tmp_path)
        result = checker.calculate()
        assert result["decision"] == "Path B (Brownfield)"

    def test_checks_breakdown_length(self, tmp_path: Any) -> None:
        """TC-198: Checks breakdown count."""
        checker = self.cls(tmp_path)
        result = checker.calculate()
        assert len(result["checks_breakdown"]) == 10

    def test_file_exists_and_contains_method(self, tmp_path: Any) -> None:
        """TC-199: File content check helper."""
        f = tmp_path / "test.md"
        f.write_text("BG-001 content")
        checker = self.cls(tmp_path)
        assert checker._file_exists_and_contains("test.md", "BG-001") is True
        assert checker._file_exists_and_contains("test.md", "FR-001") is False

    def test_glob_count_method(self, tmp_path: Any) -> None:
        """TC-200: Glob count helper."""
        checker = self.cls(tmp_path)
        assert checker._glob_count("*.md") is False
        (tmp_path / "file.md").write_text("x")
        assert checker._glob_count("*.md") is True


# ── ModelSelector ──────────────────────────────────────────────────────────────
class TestModelSelector:
    """ALG-008 OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        from agentic_workflow.domain.algorithms.model_selector import (
            ModelSelector,
            StrategyConfig,
        )

        self.cls = ModelSelector
        self.reasoning = ModelConfig(provider="anthropic", model="claude-opus")
        self.editing = ModelConfig(provider="anthropic", model="claude-haiku")
        self.cheap = ModelConfig(provider="openai", model="gpt-3.5")
        self.default = ModelConfig(provider="anthropic", model="claude-sonnet")
        self.fallback = ModelConfig(provider="openai", model="gpt-4o")
        self.config = StrategyConfig(
            reasoning_model=self.reasoning,
            editing_model=self.editing,
            cheap_model=self.cheap,
            default_model=self.default,
            fallback_model=self.fallback,
            enabled_providers=frozenset(["anthropic", "openai"]),
        )

    def test_critique_maps_to_reasoning(self) -> None:
        """TC-201: CRITIQUE task mapping."""
        result = self.cls.select(TaskType.CRITIQUE, self.config)
        assert result == self.reasoning

    def test_resolve_maps_to_editing(self) -> None:
        """TC-202: RESOLVE task mapping."""
        result = self.cls.select(TaskType.RESOLVE, self.config)
        assert result == self.editing

    def test_format_maps_to_cheap(self) -> None:
        """TC-203: FORMAT task mapping."""
        result = self.cls.select(TaskType.FORMAT, self.config)
        assert result == self.cheap

    def test_falls_back_when_provider_disabled(self) -> None:
        """TC-204: Fallback for disabled provider."""
        from agentic_workflow.domain.algorithms.model_selector import StrategyConfig

        config = StrategyConfig(
            reasoning_model=ModelConfig(provider="disabled_provider", model="x"),
            editing_model=self.editing,
            cheap_model=self.cheap,
            default_model=self.default,
            fallback_model=self.fallback,
            enabled_providers=frozenset(["openai"]),
        )
        result = self.cls.select(TaskType.CRITIQUE, config)
        assert result.provider == "openai"

    def test_no_providers_raises(self) -> None:
        """TC-205: No enabled providers raises error."""
        import icontract

        from agentic_workflow.domain.algorithms.model_selector import StrategyConfig

        config = StrategyConfig(
            reasoning_model=self.reasoning,
            editing_model=self.editing,
            cheap_model=self.cheap,
            default_model=self.default,
            fallback_model=self.fallback,
            enabled_providers=frozenset(),
        )
        with pytest.raises(icontract.ViolationError):
            self.cls.select(TaskType.CRITIQUE, config)


# ── RepoMapBuilder ─────────────────────────────────────────────────────────────
class TestRepoMapBuilder:
    """ALG-006 OO class interface."""

    def setup_method(self) -> None:
        """Initialize class reference."""
        from agentic_workflow.domain.algorithms.repo_map_builder import RepoMapBuilder

        self.cls = RepoMapBuilder

    def test_class_constants_exist(self) -> None:
        """TC-206: RepoMap constants check."""
        assert self.cls.CHARS_PER_TOKEN == 4
        assert self.cls.PAGERANK_DAMPING == 0.85
        assert self.cls.PAGERANK_ITERATIONS == 20

    def test_extract_symbols_ast_class(self) -> None:
        """TC-207: AST class extraction."""
        source = "class Foo:\n    pass\n"
        symbols = self.cls.extract_symbols_ast("test.py", source)
        assert any(s.name == "Foo" and s.kind == "class" for s in symbols)

    def test_extract_symbols_ast_function(self) -> None:
        """TC-208: AST function extraction."""
        source = "def bar(x, y):\n    pass\n"
        symbols = self.cls.extract_symbols_ast("test.py", source)
        assert any(s.name == "bar" and s.kind == "function" for s in symbols)

    def test_extract_symbols_ast_syntax_error_returns_empty(self) -> None:
        """TC-209: AST syntax error handling."""
        symbols = self.cls.extract_symbols_ast("bad.py", "def (broken:")
        assert symbols == []

    def test_build_import_graph_empty(self) -> None:
        """TC-210: Empty import graph."""
        graph = self.cls.build_import_graph([], "/tmp")
        assert graph == {}

    def test_pagerank_empty_graph(self) -> None:
        """TC-211: PageRank on empty graph."""
        result = self.cls.pagerank({})
        assert result == {}

    def test_pagerank_single_node(self) -> None:
        """TC-212: PageRank single node."""
        result = self.cls.pagerank({"a": []})
        assert "a" in result

    def test_build_returns_repo_map(self, tmp_path: Any) -> None:
        """TC-213: Build RepoMap from directory."""
        (tmp_path / "mod.py").write_text("def foo(): pass\n")
        result = self.cls.build(str(tmp_path), 500)
        assert isinstance(result, RepoMap)
        assert result.token_count <= 500

    def test_build_empty_dir_returns_empty_map(self, tmp_path: Any) -> None:
        """TC-214: Build RepoMap from empty directory."""
        result = self.cls.build(str(tmp_path), 500)
        assert result.token_count == 0
        assert result.symbols == ()


# ── Graph Builder Classes ──────────────────────────────────────────────────────
class TestGraphBuilderClasses:
    """Frameworks OO graph builder class interface."""

    def test_micro_validation_graph_builder_returns_compiled(self) -> None:
        """TC-215: MicroValidationGraphBuilder static method."""
        from agentic_workflow.frameworks.graph import MicroValidationGraphBuilder

        graph = MicroValidationGraphBuilder.build()
        assert graph is not None

    def test_iteration_graph_builder_returns_compiled(self) -> None:
        """TC-216: IterationGraphBuilder static method."""
        from agentic_workflow.frameworks.graph import IterationGraphBuilder

        graph = IterationGraphBuilder.build()
        assert graph is not None

    def test_master_graph_builder_returns_compiled(self) -> None:
        """TC-217: MasterGraphBuilder static method."""
        from agentic_workflow.frameworks.graph import MasterGraphBuilder

        graph = MasterGraphBuilder.build()
        assert graph is not None
