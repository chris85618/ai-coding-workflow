"""Clean Architecture Boundary Scanner Script.

Scans the production codebase (src/) for any Clean Architecture boundary violations
or unauthorized dependency injection attempts. Exits with non-zero code on violation.
"""

import sys
from pathlib import Path

from agentic_workflow.frameworks.validation.clean_architecture_scanner import (
    CleanArchitectureBoundaryScanner,
)


def run_scan() -> int:
    """Scan src/ directory and report violations in a clean tabular format."""
    print("=" * 80)
    print("  CLEAN ARCHITECTURE BOUNDARY COMPLIANCE SCANNER  ")
    print("=" * 80)

    project_root = Path(__file__).resolve().parent.parent
    src_dir = project_root / "src"

    if not src_dir.exists():
        print(f"Error: Source directory not found at: {src_dir}")
        return 1

    print(f"Scanning codebase: {src_dir.resolve()} ...")
    scanner = CleanArchitectureBoundaryScanner(project_root=str(project_root))
    violations = scanner.scan_directory(str(src_dir))

    if not violations:
        print("\n[SUCCESS] Compliance verification passed! 0 architectural violations found.\n")
        return 0

    print(f"\n[FAILURE] Found {len(violations)} architectural boundary violation(s):\n")

    # Format output in a beautiful CLI Table
    print(f"{'Line:Col':<10} | {'Category':<20} | {'File Path (Relative to Root)':<50}")
    separator = f"{'-' * 10}-+-{'-' * 20}-+-{'-' * 50}"
    print(separator)
    for v in violations:
        try:
            rel_file = Path(v.file_path).relative_to(project_root)
        except ValueError:
            rel_file = Path(v.file_path)
        loc_str = f"{v.line}:{v.column}"
        print(f"{loc_str:<10} | {v.category:<20} | {str(rel_file):<50}")
        print(f"  └─ Message: {v.message}\n")

    print("=" * 80)
    print("Violation(s) detected. Clean Architecture compliance check failed!")
    print("=" * 80)
    return 1


if __name__ == "__main__":
    sys.exit(run_scan())
