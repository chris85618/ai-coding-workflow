"""Pipeline Completeness Check Algorithm.

Traceable to: FR-001
Replaces: skills/workflow-skills/pipeline-completeness-check.md
"""

from pathlib import Path
from typing import Dict, Any, List

def _check_file_exists_and_contains(base_dir: Path, rel_path: str, must_contain: str | None = None) -> bool:
    target = base_dir / rel_path
    if not target.exists() or not target.is_file():
        return False
    if must_contain:
        content = target.read_text(encoding="utf-8")
        return must_contain in content
    return True

def _check_glob_count(base_dir: Path, pattern: str) -> bool:
    matches = list(base_dir.glob(pattern))
    return len(matches) > 0

def calculate_completeness(base_dir: Path) -> Dict[str, Any]:
    """Calculates pipeline completeness by checking documentation assets.
    
    Returns a dictionary with score, passed count, decision path, and next action.
    """
    checks = [
        _check_file_exists_and_contains(base_dir, "docs/workflow-state.md"),
        _check_file_exists_and_contains(base_dir, "docs/project-charter.md", "BG-"),
        _check_file_exists_and_contains(base_dir, "docs/stakeholder-analysis.md", "S-"),
        _check_file_exists_and_contains(base_dir, "docs/scope-definition.md", "FEA-"),
        _check_file_exists_and_contains(base_dir, "docs/requirements.md", "FR-"),
        _check_file_exists_and_contains(base_dir, "docs/use-cases.md", "UC-"),
        _check_file_exists_and_contains(base_dir, "docs/traceability-matrix.md"),
        _check_file_exists_and_contains(base_dir, "docs/traceability-matrix.md", "ADR 登記簿"),
        _check_file_exists_and_contains(base_dir, "docs/iteration-log.md"),
        _check_glob_count(base_dir, "docs/adr/ADR-GATE-*.md")
    ]
    
    passed = sum(1 for c in checks if c)
    completeness = passed / 10.0
    
    decision = ""
    next_action = ""
    
    if completeness == 1.0:
        decision = "complete"
        next_action = "Check workflow-state.md position. Trigger workflow-resume.md if pending work exists."
    elif completeness >= 0.6:
        decision = "partial"
        next_action = "Trigger workflow-resume.md to continue from Gate Status break point."
    elif completeness > 0:
        decision = "starting"
        has_src = _check_glob_count(base_dir, "src/**/*.py") or _check_glob_count(base_dir, "app/**/*.py") or _check_glob_count(base_dir, "lib/**/*.js")
        if has_src:
            decision = "Path B (Brownfield)"
            next_action = "Trigger Phase 1 (Understanding) to process existing code."
        else:
            decision = "Path A (Greenfield)"
            next_action = "Trigger Phase 2 (Project Analysis) to start planning."
    else:
        decision = "new"
        has_src = _check_glob_count(base_dir, "src/**/*.py") or _check_glob_count(base_dir, "app/**/*.py") or _check_glob_count(base_dir, "lib/**/*.js")
        if has_src:
            decision = "Path B (Brownfield)"
            next_action = "Trigger Phase 1 (Understanding) to process existing code."
        else:
            decision = "Path A (Greenfield)"
            next_action = "Trigger Phase 2 (Project Analysis) to start planning."
            
    return {
        "completeness_score": passed,
        "completeness_ratio": completeness,
        "decision": decision,
        "next_action": next_action,
        "checks_breakdown": checks
    }
