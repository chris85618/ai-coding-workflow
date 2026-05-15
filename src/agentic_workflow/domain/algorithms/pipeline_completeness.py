"""Pipeline Completeness Check Algorithm.

Traceable to: FR-001
Replaces: skills/workflow-skills/pipeline-completeness-check.md
OO Design: PipelineCompletenessChecker class wraps all logic (ALG-010 OO mandate).
"""

from pathlib import Path
from typing import Dict, Any, List


class PipelineCompletenessChecker:
    """Checks pipeline completeness by evaluating documentation assets.

    ALG-010 OO mandate: all logic is encapsulated in this class.
    Module-level facade functions below delegate to this class for backward
    compatibility with existing tests and callers.
    """

    # Ordered list of (rel_path, must_contain) tuples that define the 10 checks.
    _CHECKS: List[tuple] = [
        ("docs/workflow-state.md", None),
        ("docs/project-charter.md", "BG-"),
        ("docs/stakeholder-analysis.md", "S-"),
        ("docs/scope-definition.md", "FEA-"),
        ("docs/requirements.md", "FR-"),
        ("docs/use-cases.md", "UC-"),
        ("docs/traceability-matrix.md", None),
        ("docs/traceability-matrix.md", "ADR 登記簿"),
        ("docs/iteration-log.md", None),
    ]
    _GLOB_CHECK = "docs/adr/ADR-GATE-*.md"
    _SRC_GLOBS = ["src/**/*.py", "app/**/*.py", "lib/**/*.js"]
    _TOTAL_CHECKS = 10

    def __init__(self, base_dir: Path) -> None:
        """Initialise with the repository root directory.

        Args:
            base_dir: Absolute path to the repository root.
        """
        self._base_dir = base_dir

    # ── Private helpers ────────────────────────────────────────────────────────

    def _file_exists_and_contains(
        self, rel_path: str, must_contain: str | None = None
    ) -> bool:
        """Return True if the file exists and optionally contains a string.

        Args:
            rel_path: Relative path from base_dir.
            must_contain: Optional substring that must be present.

        Returns:
            Boolean indicating whether the check passed.
        """
        target = self._base_dir / rel_path
        if not target.exists() or not target.is_file():
            return False
        if must_contain:
            content = target.read_text(encoding="utf-8")
            return must_contain in content
        return True

    def _glob_count(self, pattern: str) -> bool:
        """Return True if at least one path matches the glob pattern.

        Args:
            pattern: Glob pattern relative to base_dir.

        Returns:
            True if one or more matches exist.
        """
        return len(list(self._base_dir.glob(pattern))) > 0

    def _has_src(self) -> bool:
        """Return True if any recognised source-code file exists."""
        return any(self._glob_count(g) for g in self._SRC_GLOBS)

    # ── Public API ─────────────────────────────────────────────────────────────

    def calculate(self) -> Dict[str, Any]:
        """Calculate pipeline completeness by checking documentation assets.

        Returns:
            Dict with keys: completeness_score, completeness_ratio, decision,
            next_action, checks_breakdown.
        """
        checks = [
            self._file_exists_and_contains(rel, contain)
            for rel, contain in self._CHECKS
        ]
        checks.append(self._glob_count(self._GLOB_CHECK))

        passed = sum(1 for c in checks if c)
        completeness = passed / self._TOTAL_CHECKS

        decision, next_action = self._classify(completeness)

        return {
            "completeness_score": passed,
            "completeness_ratio": completeness,
            "decision": decision,
            "next_action": next_action,
            "checks_breakdown": checks,
        }

    def _classify(self, completeness: float) -> tuple[str, str]:
        """Return (decision, next_action) for the given completeness ratio.

        Args:
            completeness: Ratio in [0.0, 1.0].

        Returns:
            Tuple of (decision_label, next_action_string).
        """
        if completeness == 1.0:
            return (
                "complete",
                "Check workflow-state.md position. Trigger workflow-resume.md if pending work exists.",
            )
        if completeness >= 0.6:
            return (
                "partial",
                "Trigger workflow-resume.md to continue from Gate Status break point.",
            )
        # < 0.6 (including 0)
        if self._has_src():
            return (
                "Path B (Brownfield)",
                "Trigger Phase 1 (Understanding) to process existing code.",
            )
        return (
            "Path A (Greenfield)",
            "Trigger Phase 2 (Project Analysis) to start planning.",
        )


# ── Module-level facade (backward compatibility) ───────────────────────────────
# Tests and existing callers import these directly; they delegate to the class.


def _check_file_exists_and_contains(
    base_dir: Path, rel_path: str, must_contain: str | None = None
) -> bool:
    """Backward-compat facade — delegates to PipelineCompletenessChecker."""
    checker = PipelineCompletenessChecker(base_dir)
    return checker._file_exists_and_contains(rel_path, must_contain)


def _check_glob_count(base_dir: Path, pattern: str) -> bool:
    """Backward-compat facade — delegates to PipelineCompletenessChecker."""
    checker = PipelineCompletenessChecker(base_dir)
    return checker._glob_count(pattern)


def calculate_completeness(base_dir: Path) -> Dict[str, Any]:
    """Backward-compat facade — delegates to PipelineCompletenessChecker."""
    return PipelineCompletenessChecker(base_dir).calculate()
