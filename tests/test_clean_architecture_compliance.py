"""Clean Architecture Compliance Gate — Production Codebase Full Scan.

This module is the MANDATORY architectural enforcement test.
It calls CleanArchitectureBoundaryScanner on the real production src/ directory
and asserts ZERO violations across ALL categories.

Violation categories enforced:
  - pragma_no_cover_abuse : # pragma: * in any layer outside if __name__ == '__main__'
  - type_ignore_abuse     : # type: * in inner layers (domain/application/adapters)
  - static_import         : inner layer importing outer layer module
  - dynamic_import        : dynamic importlib/importlib in inner layers
  - exec_eval             : exec()/eval() in inner layers
  - sys_modules           : sys.modules lookup in inner layers
  - di_container_abuse    : DependencyContainer/ServiceLocator in inner layers
  - env_access            : os.environ/os.getenv in inner layers
  - file_io               : open()/Path.read_text() in domain layer
  - external_dependency_violation: non-whitelisted third-party imports in inner layers
  - illegal_instantiation : outer-layer class instantiation in inner layers

ADR: ADR-STR-027 v2
Policy: ZERO TOLERANCE — no exceptions.
"""

import pathlib
from collections import defaultdict

import pytest

from agentic_workflow.frameworks.validation.clean_architecture_scanner import (
    BoundaryViolation,
    CleanArchitectureBoundaryScanner,
)

# ── Fixture ───────────────────────────────────────────────────────────────────

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"


@pytest.fixture(scope="module")
def all_violations() -> list[BoundaryViolation]:
    """Scan entire production src/ directory and return all violations."""
    scanner = CleanArchitectureBoundaryScanner(project_root=str(PROJECT_ROOT))
    return scanner.scan_directory(str(SRC_DIR))


# ── Helper ────────────────────────────────────────────────────────────────────


def _format_violation_report(violations: list[BoundaryViolation]) -> str:
    """Format violations into a readable grouped report for pytest failure output."""
    by_category: defaultdict[str, list[BoundaryViolation]] = defaultdict(list)
    for v in violations:
        by_category[v.category].append(v)

    lines = [
        f"\n{'=' * 80}",
        f"  CLEAN ARCHITECTURE COMPLIANCE FAILURE — {len(violations)} violation(s)",
        f"{'=' * 80}",
    ]
    for category, vs in sorted(by_category.items()):
        lines.append(f"\n[{category}] — {len(vs)} violation(s):")
        for v in vs:
            try:
                rel = pathlib.Path(v.file_path).relative_to(PROJECT_ROOT)
            except ValueError:
                rel = pathlib.Path(v.file_path)

            lines.append(f"  {rel}:{v.line}:{v.column}")
            lines.append(f"    └─ {v.message}")
    lines.append(f"\n{'=' * 80}")
    return "\n".join(lines)


# ── Compliance Tests ──────────────────────────────────────────────────────────


def test_no_pragma_violations(all_violations: list[BoundaryViolation]) -> None:
    """ADR-STR-027 v2: Zero # pragma comments allowed anywhere outside entry point.

    Enforces: ALL layers (domain/application/adapters/frameworks).
    Category: pragma_no_cover_abuse.
    """
    pragma_violations = [v for v in all_violations if v.category == "pragma_no_cover_abuse"]
    assert pragma_violations == [], _format_violation_report(pragma_violations)


def test_no_type_comment_violations(all_violations: list[BoundaryViolation]) -> None:
    """ADR-STR-027 v2: Zero # type comments allowed in inner layers.

    Enforces: domain/application/adapters layers (rank <= 3).
    Category: type_ignore_abuse.
    """
    type_violations = [v for v in all_violations if v.category == "type_ignore_abuse"]
    assert type_violations == [], _format_violation_report(type_violations)


def test_no_static_import_violations(all_violations: list[BoundaryViolation]) -> None:
    """Clean Architecture: inner layers must not statically import outer layers.

    Category: static_import.
    """
    import_violations = [v for v in all_violations if v.category == "static_import"]
    assert import_violations == [], _format_violation_report(import_violations)


def test_no_dynamic_import_violations(all_violations: list[BoundaryViolation]) -> None:
    """Clean Architecture: dynamic imports (importlib) banned in inner layers.

    Category: dynamic_import.
    """
    violations = [v for v in all_violations if v.category == "dynamic_import"]
    assert violations == [], _format_violation_report(violations)


def test_no_exec_eval_violations(all_violations: list[BoundaryViolation]) -> None:
    """Clean Architecture: exec()/eval() banned in inner layers.

    Category: exec_eval.
    """
    violations = [v for v in all_violations if v.category == "exec_eval"]
    assert violations == [], _format_violation_report(violations)


def test_no_sys_modules_violations(all_violations: list[BoundaryViolation]) -> None:
    """Clean Architecture: sys.modules lookup banned in inner layers.

    Category: sys_modules.
    """
    violations = [v for v in all_violations if v.category == "sys_modules"]
    assert violations == [], _format_violation_report(violations)


def test_no_di_container_abuse(all_violations: list[BoundaryViolation]) -> None:
    """Clean Architecture: DI container/locator banned in inner layers (rank < 3).

    Category: di_container_abuse.
    """
    violations = [v for v in all_violations if v.category == "di_container_abuse"]
    assert violations == [], _format_violation_report(violations)


def test_no_env_access_violations(all_violations: list[BoundaryViolation]) -> None:
    """Clean Architecture: os.environ/os.getenv banned in inner layers.

    Category: env_access.
    """
    violations = [v for v in all_violations if v.category == "env_access"]
    assert violations == [], _format_violation_report(violations)


def test_no_file_io_violations(all_violations: list[BoundaryViolation]) -> None:
    """Clean Architecture: open()/Path.read_text() banned in domain layer.

    Category: file_io.
    """
    violations = [v for v in all_violations if v.category == "file_io"]
    assert violations == [], _format_violation_report(violations)


def test_no_external_dependency_violations(all_violations: list[BoundaryViolation]) -> None:
    """Clean Architecture: non-whitelisted third-party imports banned in inner layers.

    Category: external_dependency_violation.
    """
    violations = [v for v in all_violations if v.category == "external_dependency_violation"]
    assert violations == [], _format_violation_report(violations)


def test_no_illegal_instantiation_violations(all_violations: list[BoundaryViolation]) -> None:
    """Clean Architecture: outer-layer class instantiation banned in inner layers.

    Category: illegal_instantiation.
    """
    violations = [v for v in all_violations if v.category == "illegal_instantiation"]
    assert violations == [], _format_violation_report(violations)


def test_zero_total_violations(all_violations: list[BoundaryViolation]) -> None:
    """Master gate: total violation count across ALL categories must be exactly zero.

    This is the single summary assertion that combines all individual checks.
    A failure here means at least one category-specific test above also fails.
    """
    assert all_violations == [], _format_violation_report(all_violations)
