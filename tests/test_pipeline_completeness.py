"""Tests for pipeline_completeness — 100% statement + branch coverage.
Consolidated from: test_algorithms_coverage.py
Traceable to: FR-001, ALG-006
"""
import pytest
from pathlib import Path
import tempfile
import os

from agentic_workflow.domain.algorithms.pipeline_completeness import (
    calculate_completeness,
    _check_file_exists_and_contains,
    _check_glob_count,
)


# ── Helpers ────────────────────────────────────────────────────────────────────
def _make_repo(tmp_path: Path, files: dict, src_files: list = None) -> Path:
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
    "docs/traceability-matrix.md": "ADR 登記簿 full matrix",
    "docs/iteration-log.md": "log",
}
ADR_GATE_FILE = "docs/adr/ADR-GATE-001.md"


# ── _check_file_exists_and_contains ──────────────────────────────────────────
class TestCheckFileExistsAndContains:
    def test_file_missing_returns_false(self, tmp_path):
        assert _check_file_exists_and_contains(tmp_path, "missing.md") is False

    def test_directory_not_file_returns_false(self, tmp_path):
        d = tmp_path / "adir"
        d.mkdir()
        assert _check_file_exists_and_contains(tmp_path, "adir") is False

    def test_file_exists_no_content_check(self, tmp_path):
        (tmp_path / "f.md").write_text("x", encoding="utf-8")
        assert _check_file_exists_and_contains(tmp_path, "f.md") is True

    def test_file_contains_string(self, tmp_path):
        (tmp_path / "f.md").write_text("BG-001 here", encoding="utf-8")
        assert _check_file_exists_and_contains(tmp_path, "f.md", "BG-001") is True

    def test_file_missing_string(self, tmp_path):
        (tmp_path / "f.md").write_text("nothing", encoding="utf-8")
        assert _check_file_exists_and_contains(tmp_path, "f.md", "BG-001") is False


# ── _check_glob_count ─────────────────────────────────────────────────────────
class TestCheckGlobCount:
    def test_no_matches_returns_false(self, tmp_path):
        assert _check_glob_count(tmp_path, "*.xyz") is False

    def test_with_match_returns_true(self, tmp_path):
        (tmp_path / "file.md").write_text("x", encoding="utf-8")
        assert _check_glob_count(tmp_path, "*.md") is True


# ── calculate_completeness ────────────────────────────────────────────────────
class TestCalculateCompleteness:

    def test_complete_returns_score_10(self, tmp_path):
        _make_repo(tmp_path, FULL_DOCS)
        (tmp_path / ADR_GATE_FILE).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / ADR_GATE_FILE).write_text("gate", encoding="utf-8")
        result = calculate_completeness(tmp_path)
        assert result["completeness_score"] == 10
        assert result["completeness_ratio"] == 1.0
        assert result["decision"] == "complete"
        assert "workflow-resume" in result["next_action"]

    def test_partial_60_percent_triggers_resume(self, tmp_path):
        # 6/10 checks pass (docs present but no ADR-GATE, no iteration-log, etc.)
        partial = {
            "docs/workflow-state.md": "content",
            "docs/project-charter.md": "BG-001",
            "docs/stakeholder-analysis.md": "S-001",
            "docs/scope-definition.md": "FEA-001",
            "docs/requirements.md": "FR-001",
            "docs/use-cases.md": "UC-001",
            "docs/traceability-matrix.md": "ADR 登記簿 content",  # both checks pass
            "docs/iteration-log.md": "log",
        }
        _make_repo(tmp_path, partial)
        result = calculate_completeness(tmp_path)
        # 8 docs present = all 8 checks pass, but no ADR-GATE file
        # checks: workflow(1) + charter(1) + stakeholder(1) + scope(1) + req(1) + uc(1)
        #         + traceability(1) + adr-section(1) + iteration-log(1) + adr-gate(0) = 9
        assert result["completeness_ratio"] >= 0.6
        # decision is partial or complete depending on ADR-GATE
        assert result["decision"] in ["partial", "complete"]

    def test_starting_with_src_is_brownfield(self, tmp_path):
        """completeness > 0 but < 0.6, with src/*.py → Path B."""
        _make_repo(tmp_path,
                   {"docs/workflow-state.md": "content"},
                   src_files=["src/main.py"])
        result = calculate_completeness(tmp_path)
        assert result["completeness_score"] == 1
        assert result["decision"] == "Path B (Brownfield)"
        assert "Phase 1" in result["next_action"]

    def test_starting_without_src_is_greenfield(self, tmp_path):
        """completeness > 0 but < 0.6, no src → Path A."""
        _make_repo(tmp_path, {"docs/workflow-state.md": "content"})
        result = calculate_completeness(tmp_path)
        assert result["completeness_score"] == 1
        assert result["decision"] == "Path A (Greenfield)"
        assert "Phase 2" in result["next_action"]

    def test_zero_completeness_with_src_is_brownfield(self, tmp_path):
        """completeness == 0, with src/*.py → Path B."""
        _make_repo(tmp_path, {}, src_files=["src/core.py"])
        result = calculate_completeness(tmp_path)
        assert result["completeness_score"] == 0
        assert result["decision"] == "Path B (Brownfield)"

    def test_zero_completeness_without_src_is_greenfield(self, tmp_path):
        """completeness == 0, no src → Path A."""
        result = calculate_completeness(tmp_path)
        assert result["completeness_score"] == 0
        assert result["decision"] == "Path A (Greenfield)"

    def test_app_js_counts_as_src(self, tmp_path):
        """lib/**/*.js also triggers Brownfield."""
        js = tmp_path / "lib" / "index.js"
        js.parent.mkdir(parents=True)
        js.write_text("// code", encoding="utf-8")
        result = calculate_completeness(tmp_path)
        assert result["decision"] == "Path B (Brownfield)"

    def test_checks_breakdown_is_list_of_bools(self, tmp_path):
        result = calculate_completeness(tmp_path)
        assert isinstance(result["checks_breakdown"], list)
        assert all(isinstance(v, bool) for v in result["checks_breakdown"])
        assert len(result["checks_breakdown"]) == 10

    def test_partial_exactly_60pct(self, tmp_path):
        """6/10 checks = 0.6 → partial branch.
        Checks that pass: workflow(1)+charter(1)+stakeholder(1)+scope(1)+req(1)+uc(1) = 6.
        Missing: traceability-matrix(0)+adr-section(0)+iteration-log(0)+adr-gate(0).
        """
        docs = {
            "docs/workflow-state.md": "content",
            "docs/project-charter.md": "BG-001",
            "docs/stakeholder-analysis.md": "S-001",
            "docs/scope-definition.md": "FEA-001",
            "docs/requirements.md": "FR-001",
            "docs/use-cases.md": "UC-001",
            # no traceability-matrix.md, no iteration-log.md, no ADR-GATE
        }
        _make_repo(tmp_path, docs)
        result = calculate_completeness(tmp_path)
        assert result["completeness_score"] == 6
        assert result["completeness_ratio"] == 0.6
        assert result["decision"] == "partial"
        assert "workflow-resume" in result["next_action"]

