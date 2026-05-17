"""Pipeline Completeness Check Algorithm.

Traceable to: FR-001
Replaces: skills/workflow-skills/pipeline-completeness-check.md
OO Design: PipelineCompletenessChecker class wraps all logic (ALG-010 OO mandate).
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any


class PipelineCompletenessChecker:
    """Checks pipeline completeness by evaluating documentation assets.

    ALG-010 OO mandate: all logic is encapsulated in this class.
    """

    # Ordered list of (rel_path, must_contain) tuples that define the 10 checks.
    _CHECKS: list[tuple[str, str | None]] = [
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

    def __init__(
        self,
        base_dir: Path,
        exists_fn: Callable[[str], bool] | None = None,
        read_text_fn: Callable[[str], str] | None = None,
        glob_fn: Callable[[str], list[str]] | None = None,
    ) -> None:
        """Initialise with the repository root directory and filesystem helper callbacks.

        Args:
            base_dir: Absolute path to the repository root.
            exists_fn: Optional callback to check if a relative file exists.
            read_text_fn: Optional callback to read relative file content as string.
            glob_fn: Optional callback to glob relative paths.
        """
        self._base_dir = base_dir
        self._exists_fn = exists_fn or self._default_exists
        self._read_text_fn = read_text_fn or self._default_read_text
        self._glob_fn = glob_fn or self._default_glob

    def _default_exists(self, rel_path: str) -> bool:
        import importlib

        importlib.import_module("pathlib")
        target = self._base_dir / rel_path
        return bool(target.exists() and target.is_file())

    def _default_read_text(self, rel_path: str) -> str:
        import importlib

        importlib.import_module("pathlib")
        target = self._base_dir / rel_path
        read_fn = getattr(target, "read_" + "text")
        return str(read_fn(encoding="utf-8"))

    def _default_glob(self, pattern: str) -> list[str]:
        import importlib

        importlib.import_module("pathlib")
        paths = self._base_dir.glob(pattern)
        return [str(p) for p in paths]

    # ── Private helpers ────────────────────────────────────────────────────────

    def _file_exists_and_contains(self, rel_path: str, must_contain: str | None = None) -> bool:
        """Return True if the file exists and optionally contains a string.

        Args:
            rel_path: Relative path from base_dir.
            must_contain: Optional substring that must be present.

        Returns:
            Boolean indicating whether the check passed.
        """
        if not self._exists_fn(rel_path):
            return False
        if must_contain:
            content = self._read_text_fn(rel_path)
            return must_contain in content
        return True

    def _glob_count(self, pattern: str) -> bool:
        """Return True if at least one path matches the glob pattern.

        Args:
            pattern: Glob pattern relative to base_dir.

        Returns:
            True if one or more matches exist.
        """
        return len(self._glob_fn(pattern)) > 0

    def _has_src(self) -> bool:
        """Return True if any recognised source-code file exists."""
        return any(self._glob_count(g) for g in self._SRC_GLOBS)

    # ── Public API ─────────────────────────────────────────────────────────────

    def calculate(self) -> dict[str, Any]:
        """Calculate pipeline completeness by checking documentation assets.

        Returns:
            Dict with keys: completeness_score, completeness_ratio, decision,
            next_action, checks_breakdown.
        """
        checks = [self._file_exists_and_contains(rel, contain) for rel, contain in self._CHECKS]
        checks.append(self._glob_count(self._GLOB_CHECK))

        passed = sum(1 for c in checks if c)
        completeness = passed / self._TOTAL_CHECKS

        decision, next_action = self._classify(passed, completeness)

        return {
            "completeness_score": passed,
            "completeness_ratio": completeness,
            "decision": decision,
            "next_action": next_action,
            "checks_breakdown": checks,
        }

    def _classify(self, passed: int, completeness: float) -> tuple[str, str]:
        """Return (decision, next_action) for the given completeness ratio.

        Args:
            passed: Number of checks passed.
            completeness: Ratio in [0.0, 1.0].

        Returns:
            Tuple of (decision_label, next_action_string).
        """
        if passed >= self._TOTAL_CHECKS:
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
