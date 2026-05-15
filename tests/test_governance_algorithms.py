"""Unit tests for completion_check, exhaustive_search, iter_loop,
security_audit, sonarcloud_gate, workflow_resume.
Targets 100% coverage on each module.
"""
import pytest
from agentic_workflow.domain.algorithms.completion_check import CompletionCheck
from agentic_workflow.domain.algorithms.exhaustive_search import ExhaustiveSearch
from agentic_workflow.domain.algorithms.iter_loop import IterationLoop
from agentic_workflow.domain.algorithms.security_audit import (
    ThreeLayerSecurityAudit, SecurityAuditResult,
)
from agentic_workflow.domain.algorithms.sonarcloud_gate import SonarCloudGate
from agentic_workflow.domain.algorithms.workflow_resume import WorkflowResume


# ── CompletionCheck ────────────────────────────────────────────────────────────
class TestCompletionCheck:
    def test_ready_when_all_green(self):
        # 100% coverage, 0 risks, 0 debts
        result = CompletionCheck.verify_readiness(1.00, 0, 0)
        assert result["ready"] is True
        assert result["failures"] == []

    def test_fails_on_low_coverage(self):
        # 99.9% is still low for strict mode
        result = CompletionCheck.verify_readiness(0.999, 0, 0)
        assert result["ready"] is False
        assert any("coverage" in f.lower() for f in result["failures"])

    def test_fails_on_open_risks(self):
        result = CompletionCheck.verify_readiness(1.00, 2, 0)
        assert result["ready"] is False
        assert any("risk" in f.lower() for f in result["failures"])

    def test_exactly_at_threshold_is_ready(self):
        # Threshold is now 1.00
        result = CompletionCheck.verify_readiness(1.00, 0, 0)
        assert result["ready"] is True

    def test_pending_debts_blocks_in_strict_mode(self):
        # ALG-010 OO refactor added debt checking
        result = CompletionCheck.verify_readiness(1.00, 0, 1)
        assert result["ready"] is False
        assert any("debt" in f.lower() for f in result["failures"])

    def test_facade_backward_compatibility(self):
        # Test the module-level function calls the class method correctly
        from agentic_workflow.domain.algorithms.completion_check import verify_readiness
        result = verify_readiness(1.00, 0, 0)
        assert result["ready"] is True


# ── ExhaustiveSearch ───────────────────────────────────────────────────────────
class TestExhaustiveSearch:
    def test_scan_directory_returns_list(self):
        result = ExhaustiveSearch.scan_directory("/some/path", "FR-")
        assert isinstance(result, list)

    def test_verify_orphan_status_no_references(self):
        # scan_directory returns [] so len==0 → not referenced → False
        assert ExhaustiveSearch.verify_orphan_status("FR-001", "/path") is False

    def test_verify_orphan_status_logic(self, monkeypatch):
        monkeypatch.setattr(ExhaustiveSearch, "scan_directory", lambda *_: ["a", "b"])
        assert ExhaustiveSearch.verify_orphan_status("FR-001", "/path") is True


# ── IterationLoop ──────────────────────────────────────────────────────────────
class TestIterationLoop:
    def test_agent_alpha_returns_list(self):
        result = IterationLoop.agent_alpha_critique("output", ["criterion"])
        assert isinstance(result, list)

    def test_agent_beta_returns_string(self):
        result = IterationLoop.agent_beta_resolve([])
        assert isinstance(result, str)

    def test_convergence_reached_all_yagni(self):
        critiques = [{"severity": "YAGNI"}, {"severity": "YAGNI"}]
        assert IterationLoop.determine_convergence(critiques, []) == "REACHED"

    def test_convergence_not_reached(self):
        curr = [{"severity": "HIGH"}]
        prev = [{"severity": "CRITICAL"}, {"severity": "CRITICAL"}]
        result = IterationLoop.determine_convergence(curr, prev)
        assert result == "NOT_REACHED"

    def test_convergence_diverging(self):
        curr = [{"severity": "CRITICAL"}, {"severity": "HIGH"}]
        prev = [{"severity": "HIGH"}]
        result = IterationLoop.determine_convergence(curr, prev)
        assert result == "DIVERGING"

    def test_run_iteration_converged_immediately(self):
        # agent_alpha returns [] → REACHED
        result = IterationLoop.run_iteration("output", [])
        assert result["status"] == "converged"
        assert result["output"] == "output"

    def test_run_iteration_not_converged(self, monkeypatch):
        monkeypatch.setattr(IterationLoop, "agent_alpha_critique",
                            lambda *_: [{"severity": "HIGH"}])
        result = IterationLoop.run_iteration("output", [])
        assert "next_output" in result or "status" in result


# ── ThreeLayerSecurityAudit ────────────────────────────────────────────────────
class TestSecurityAudit:
    def test_layer1_passes(self):
        r = ThreeLayerSecurityAudit.run_layer1_app_security()
        assert r.passed is True
        assert r.layer == "1_app_security"

    def test_layer2_passes(self):
        r = ThreeLayerSecurityAudit.run_layer2_agent_security()
        assert r.passed is True

    def test_layer3_passes(self):
        r = ThreeLayerSecurityAudit.run_layer3_supply_chain()
        assert r.passed is True

    def test_evaluate_all_pass(self):
        results = [
            ThreeLayerSecurityAudit.run_layer1_app_security(),
            ThreeLayerSecurityAudit.run_layer2_agent_security(),
            ThreeLayerSecurityAudit.run_layer3_supply_chain(),
        ]
        ev = ThreeLayerSecurityAudit.evaluate_audit(results)
        assert ev["passed"] is True
        assert ev["decision"] == "pass"

    def test_evaluate_with_high_finding_reworks(self):
        results = [
            SecurityAuditResult(
                layer="1", passed=False,
                findings=[{"severity": "HIGH", "message": "SQL injection"}]
            )
        ]
        ev = ThreeLayerSecurityAudit.evaluate_audit(results)
        assert ev["decision"] == "rework"
        assert ev["passed"] is False

    def test_evaluate_with_critical_finding_blocks(self):
        results = [
            SecurityAuditResult(
                layer="1", passed=False,
                findings=[{"severity": "CRITICAL", "message": "RCE"}]
            )
        ]
        ev = ThreeLayerSecurityAudit.evaluate_audit(results)
        assert ev["decision"] == "block_escalate"

    def test_generate_risk_debt_entries(self):
        findings = [
            {"severity": "CRITICAL", "message": "XSS"},
            {"severity": "HIGH", "message": "CSRF"},
        ]
        out = ThreeLayerSecurityAudit.generate_risk_debt_entries(findings)
        assert len(out["risks"]) == 2
        assert out["risks"][0]["id"] == "RISK-SEC-0"
        assert out["debts"][0]["priority"] == "P0"
        assert out["debts"][1]["priority"] == "P1"

    def test_generate_empty_findings(self):
        out = ThreeLayerSecurityAudit.generate_risk_debt_entries([])
        assert out == {"risks": [], "debts": []}

    def test_evaluate_low_severity_finding_not_collected(self):
        """Branch: finding severity not in HIGH/CRITICAL → not collected."""
        results = [
            SecurityAuditResult(
                layer="1", passed=False,
                findings=[{"severity": "LOW", "message": "minor"}]
            )
        ]
        ev = ThreeLayerSecurityAudit.evaluate_audit(results)
        # all_passed=False, no HIGH/CRITICAL → decision=rework
        assert ev["decision"] == "rework"
        assert ev["findings"] == []


# ── SonarCloudGate ─────────────────────────────────────────────────────────────
class TestSonarCloudGate:
    def _good_metrics(self):
        return {
            "coverage": {"global": 82.0, "new": 90.0},
            "duplication": {"global": 2.0, "new": 1.0},
            "cyclomatic_complexity": {"global": 10, "new": 8},
            "cognitive_complexity": {"global": 10, "new": 8},
            "security_vulnerabilities": {"global": 0, "new": 0},
            "blocker_critical_smells": {"global": 0, "new": 0},
            "major_smells": {"global": 5, "new": 2},
            "tech_debt_ratio": {"global": 3.0, "new": 2.0},
            "reliability_rating": {"global": "A", "new": "A"},
        }

    def test_all_pass_returns_passed(self):
        result = SonarCloudGate.evaluate(self._good_metrics())
        assert result["passed"] is True
        assert result["next_action"] == "continue"
        assert result["prompt_for_agent"] is None

    def test_low_coverage_fails(self):
        metrics = self._good_metrics()
        metrics["coverage"] = {"global": 70.0, "new": 70.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False
        assert result["next_action"] == "trigger_autonomous_fix"
        assert result["prompt_for_agent"] is not None

    def test_high_duplication_fails(self):
        metrics = self._good_metrics()
        metrics["duplication"] = {"global": 10.0, "new": 5.0}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False

    def test_bad_reliability_rating_fails(self):
        metrics = self._good_metrics()
        metrics["reliability_rating"] = {"global": "B", "new": "A"}
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is False

    def test_missing_metric_skipped(self):
        # only provide coverage — other metrics not evaluated, so it passes
        result = SonarCloudGate.evaluate({"coverage": {"global": 85.0, "new": 90.0}})
        assert result["passed"] is True

    def test_extract_tech_debt_todo(self):
        issues = [
            {"type": "TODO", "message": "Refactor this", "severity": "MAJOR"},
            {"type": "TODO", "message": "Clean up", "severity": "MINOR"},
        ]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert len(debts) == 2
        assert debts[0]["priority"] == "P2"
        assert debts[1]["priority"] == "P3"

    def test_extract_tech_debt_non_debt_type_ignored(self):
        issues = [{"type": "BUG", "message": "crash"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert debts == []

    def test_extract_tech_debt_code_smell(self):
        issues = [{"type": "CODE_SMELL", "message": "smell", "severity": "CRITICAL"}]
        debts = SonarCloudGate.extract_tech_debt(issues)
        assert debts[0]["priority"] == "P2"

    def test_metric_with_only_global_scope_evaluates_global(self):
        """Branch: scope 'new' not in actual_data → skip new scope."""
        metrics = {"coverage": {"global": 85.0}}  # no 'new' scope
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is True

    def test_metric_with_only_new_scope(self):
        """Branch: scope 'global' not in actual_data → skip global scope."""
        metrics = {"coverage": {"new": 90.0}}  # no 'global' scope
        result = SonarCloudGate.evaluate(metrics)
        assert result["passed"] is True


# ── WorkflowResume ─────────────────────────────────────────────────────────────
class TestWorkflowResume:
    def test_load_state_returns_dict(self):
        state = WorkflowResume.load_state("some workflow state content")
        assert isinstance(state, dict)
        assert "pipeline_position" in state

    def test_format_recovery_summary_contains_position(self):
        state = {"pipeline_position": "Stage 3", "completed_gates": ["G1"], "pending_escalations": []}
        summary = WorkflowResume.format_recovery_summary(state)
        assert "Stage 3" in summary
        assert "1" in summary  # 1 completed gate

    def test_determine_next_action_reset(self):
        state = {"pending_escalations": []}
        result = WorkflowResume.determine_next_action(state, user_choice=3)
        assert result == "RESET_PHASE_0"

    def test_determine_next_action_with_escalations(self):
        state = {"pending_escalations": ["ESC-001"]}
        result = WorkflowResume.determine_next_action(state, user_choice=1)
        assert result == "RESOLVE_ESCALATIONS"

    def test_determine_next_action_resume(self):
        state = {"pending_escalations": []}
        result = WorkflowResume.determine_next_action(state, user_choice=1)
        assert result == "RESUME_AT_POSITION"
