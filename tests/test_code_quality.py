"""Tests for codebase quality using Ruff and Mypy.

Traceable to: FR-QUALITY-001, FR-QUALITY-002
"""

import pathlib
import subprocess
import sys

# Load tomllib (Python 3.11+) or tomli for compatibility
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


def _load_target_paths() -> list[str]:
    """Load target paths from pyproject.toml configuration."""
    pyproject_path = pathlib.Path(__file__).parent.parent / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            config = tomllib.load(f)
            # Try to load target paths from [tool.ruff] src definition
            ruff_src = config.get("tool", {}).get("ruff", {}).get("src")
            if isinstance(ruff_src, list):
                return [str(p) for p in ruff_src]
    # Fallback default if config parsing fails
    return ["src", "tests"]


def test_ruff_linting() -> None:
    """TC-QUALITY-001: Verify Ruff check reports zero warnings and passes successfully."""
    paths = _load_target_paths()
    cmd = [sys.executable, "-m", "ruff", "check"] + paths
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=False)

    # Assert on both exit code and success indicator in stdout
    assert result.returncode == 0, (
        f"Ruff check failed with exit code {result.returncode}.\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
    )
    assert "All checks passed!" in result.stdout or not result.stdout, (
        f"Ruff linting found violations:\n{result.stdout}"
    )


def test_mypy_type_safety() -> None:
    """TC-QUALITY-002: Verify Mypy type-checking reports zero issues and passes successfully."""
    paths = _load_target_paths()
    cmd = [sys.executable, "-m", "mypy", "--ignore-missing-imports"] + paths
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=False)

    # Assert on both exit code and success indicator in stdout
    assert result.returncode == 0, (
        f"Mypy check failed with exit code {result.returncode}.\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
    )

    assert "Success: no issues found" in result.stdout, f"Mypy found type safety violations:\n{result.stdout}"


def test_debt_009_ellipsis_in_concrete_code() -> None:
    """TC-QUALITY-003: Verify that ellipsis (...) is only used in Protocols or abstract methods (DEBT-009)."""
    import ast

    paths = _load_target_paths()
    violations = []

    class EllipsisVisitor(ast.NodeVisitor):
        def __init__(self, filepath: pathlib.Path):
            self.filepath = filepath
            self.class_stack: list[tuple[str, bool]] = []  # (class_name, is_abstract)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            is_abstract = False
            for base in node.bases:
                if (
                    isinstance(base, ast.Name)
                    and base.id in ("Protocol", "ABC")
                    or isinstance(base, ast.Attribute)
                    and base.attr in ("Protocol", "ABC")
                ):
                    is_abstract = True
            self.class_stack.append((node.name, is_abstract))
            self.generic_visit(node)
            self.class_stack.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._check_body(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._check_body(node)
            self.generic_visit(node)

        def _check_body(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            if len(node.body) == 1:
                stmt = node.body[0]
                is_ellipsis = False
                if isinstance(stmt, ast.Expr) and (
                    isinstance(stmt.value, ast.Constant)
                    and stmt.value.value is Ellipsis
                    or isinstance(stmt.value, ast.Ellipsis)
                ):
                    is_ellipsis = True

                if is_ellipsis:
                    # Check context
                    in_abstract_class = False
                    if self.class_stack:
                        _, in_abstract_class = self.class_stack[-1]

                    is_abstract_method = False
                    for dec in node.decorator_list:
                        if (
                            isinstance(dec, ast.Name)
                            and dec.id == "abstractmethod"
                            or isinstance(dec, ast.Attribute)
                            and dec.attr == "abstractmethod"
                        ):
                            is_abstract_method = True

                    if not (in_abstract_class or is_abstract_method):
                        violations.append(
                            f"{self.filepath}:{node.lineno}: Method/Function '{node.name}' "
                            "uses ellipsis '...' in concrete context. Use 'pass' instead (DEBT-009)."
                        )

    for p in paths:
        path = pathlib.Path(p)
        files = [path] if path.is_file() else list(path.rglob("*.py"))

        for file in files:
            try:
                content = file.read_text(encoding="utf-8")
                tree = ast.parse(content, filename=str(file))
                visitor = EllipsisVisitor(file)
                visitor.visit(tree)
            except Exception:
                pass

    assert not violations, "DEBT-009 Violations found (ellipsis used in concrete dry-run contexts):\n" + "\n".join(
        violations
    )
