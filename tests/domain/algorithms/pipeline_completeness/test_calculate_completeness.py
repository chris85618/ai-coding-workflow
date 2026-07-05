"""Test calculate core logic for pipeline completeness."""

from pathlib import Path

from agentic_workflow.domain.algorithms.pipeline_completeness import PipelineCompletenessChecker


def _make_repo(tmp_path: Path, files: dict[str, str], src_files: list[str] | None = None) -> Path:
    """Creates a minimal repo structure in tmp_path."""
    for rel, content in files.items():
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    if src_files:
        for sf in src_files:
            p = tmp_path / sf
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# code", encoding="utf-8")
    return tmp_path


FULL_DOCS = {
    "docs/workflow-state.md": "content",
    "docs/project-charter.md": "BG-001 project",
    "docs/stakeholder-analysis.md": "S-001 stakeholder",
    "docs/scope-definition.md": "FEA-001 scope",
    "docs/requirements.md": "FR-001 requirement",
    "docs/use-cases.md": "UC-001 use case",
    "docs/traceability-matrix.md": "ADR \u767b\u8a18\u7c3f full matrix",
    "docs/iteration-log.md": "log",
}
ADR_GATE_FILE = "docs/adr/ADR-GATE-001.md"


class TestCalculateCompleteness:
    """Test calculate core logic."""

    def test_complete_returns_score_10(self, tmp_path: Path) -> None:
        """Verify 100% completeness logic."""
        full_docs = FULL_DOCS
        adr_gate_file = ADR_GATE_FILE
        _make_repo(tmp_path, full_docs)
        (tmp_path / adr_gate_file).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / adr_gate_file).write_text("gate", encoding="utf-8")
        result = PipelineCompletenessChecker(tmp_path).calculate()
        assert result["completeness_score"] == 10
        assert result["completeness_ratio"] == 1.0
        assert result["decision"] == "complete"
        assert "workflow-resume" in result["next_action"]

    def test_partial_60_percent_triggers_resume(self, tmp_path: Path) -> None:
        """Verify 60% partial completeness."""
        partial = {
            "docs/workflow-state.md": "content",
            "docs/project-charter.md": "BG-001",
            "docs/stakeholder-analysis.md": "S-001",
            "docs/scope-definition.md": "FEA-001",
            "docs/requirements.md": "FR-001",
            "docs/use-cases.md": "UC-001",
            "docs/traceability-matrix.md": "ADR \u767b\u8a18\u7c3f content",
            "docs/iteration-log.md": "log",
        }
        _make_repo(tmp_path, partial)
        result = PipelineCompletenessChecker(tmp_path).calculate()
        assert result["completeness_ratio"] >= 0.6
        assert result["decision"] in ["partial", "complete"]

    def test_starting_with_src_is_brownfield(self, tmp_path: Path) -> None:
        """Verify Path B detection."""
        _make_repo(tmp_path, {"docs/workflow-state.md": "content"}, src_files=["src/main.py"])
        result = PipelineCompletenessChecker(tmp_path).calculate()
        assert result["completeness_score"] == 1
        assert result["decision"] == "Path B (Brownfield)"
        assert "Phase 1" in result["next_action"]

    def test_starting_without_src_is_greenfield(self, tmp_path: Path) -> None:
        """Verify Path A detection."""
        _make_repo(tmp_path, {"docs/workflow-state.md": "content"})
        result = PipelineCompletenessChecker(tmp_path).calculate()
        assert result["completeness_score"] == 1
        assert result["decision"] == "Path A (Greenfield)"
        assert "Phase 2" in result["next_action"]

    def test_zero_completeness_with_src_is_brownfield(self, tmp_path: Path) -> None:
        """Verify Brownfield with zero docs."""
        _make_repo(tmp_path, {}, src_files=["src/core.py"])
        result = PipelineCompletenessChecker(tmp_path).calculate()
        assert result["completeness_score"] == 0
        assert result["decision"] == "Path B (Brownfield)"

    def test_zero_completeness_without_src_is_greenfield(self, tmp_path: Path) -> None:
        """Verify Greenfield with zero docs."""
        result = PipelineCompletenessChecker(tmp_path).calculate()
        assert result["completeness_score"] == 0
        assert result["decision"] == "Path A (Greenfield)"

    def test_app_js_counts_as_src(self, tmp_path: Path) -> None:
        """Verify JS files trigger Path B."""
        js = tmp_path / "lib" / "index.js"
        js.parent.mkdir(parents=True)
        js.write_text("// code", encoding="utf-8")
        result = PipelineCompletenessChecker(tmp_path).calculate()
        assert result["decision"] == "Path B (Brownfield)"

    def test_checks_breakdown_is_list_of_bools(self, tmp_path: Path) -> None:
        """Verify output structure of checks breakdown."""
        result = PipelineCompletenessChecker(tmp_path).calculate()
        assert isinstance(result["checks_breakdown"], list)
        assert all(isinstance(v, bool) for v in result["checks_breakdown"])
        assert len(result["checks_breakdown"]) == 10

    def test_partial_exactly_60pct(self, tmp_path: Path) -> None:
        """Verify boundary condition for partial decision."""
        docs = {
            "docs/workflow-state.md": "content",
            "docs/project-charter.md": "BG-001",
            "docs/stakeholder-analysis.md": "S-001",
            "docs/scope-definition.md": "FEA-001",
            "docs/requirements.md": "FR-001",
            "docs/use-cases.md": "UC-001",
        }
        _make_repo(tmp_path, docs)
        result = PipelineCompletenessChecker(tmp_path).calculate()
        assert result["completeness_score"] == 6
        assert result["completeness_ratio"] == 0.6
        assert result["decision"] == "partial"
        assert "workflow-resume" in result["next_action"]
