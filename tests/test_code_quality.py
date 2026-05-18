"""Tests for codebase quality using Ruff and Mypy.

Traceable to: FR-QUALITY-001, FR-QUALITY-002
"""

import ast
import pathlib
import subprocess
import sys
import typing

# Load tomllib (Python 3.11+) or tomli for compatibility
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


def _load_target_paths() -> list[str]:
    """Load target paths from pyproject.toml configuration and resolve them to absolute paths."""
    pyproject_path = (pathlib.Path(__file__).parent.parent / "pyproject.toml").resolve()
    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            config = tomllib.load(f)
            # Try to load target paths from [tool.ruff] src definition
            ruff_src = config.get("tool", {}).get("ruff", {}).get("src")
            if isinstance(ruff_src, list):
                root_dir = pyproject_path.parent
                return [str((root_dir / p).resolve()) for p in ruff_src]
    # Fallback default if config parsing fails
    root_dir = pathlib.Path(__file__).parent.parent.resolve()
    return [str((root_dir / "src").resolve()), str((root_dir / "tests").resolve())]


def test_ruff_linting() -> None:
    """TC-QUALITY-001: Verify Ruff check reports zero warnings and passes successfully."""
    paths = _load_target_paths()
    root_dir = pathlib.Path(__file__).parent.parent.resolve()
    cmd = [sys.executable, "-m", "ruff", "check"] + paths
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=False, cwd=root_dir)

    # Assert on both exit code and success indicator in stdout
    assert result.returncode == 0, (
        f"Ruff check failed with exit code {result.returncode}.\n"
        f"Command executed: {' '.join(cmd)}\n"
        f"Target paths: {paths}\n"
        f"Stdout:\n{result.stdout}\n"
        f"Stderr:\n{result.stderr}"
    )
    assert "All checks passed!" in result.stdout or not result.stdout, (
        f"Ruff linting found violations.\n"
        f"Command executed: {' '.join(cmd)}\n"
        f"Target paths: {paths}\n"
        f"Stdout:\n{result.stdout}"
    )


def test_mypy_type_safety() -> None:
    """TC-QUALITY-002: Verify Mypy type-checking reports zero issues and passes strictly by config."""
    paths = _load_target_paths()
    root_dir = pathlib.Path(__file__).parent.parent.resolve()
    cmd = [sys.executable, "-m", "mypy"] + paths
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=False, cwd=root_dir)

    # Assert on exit code 0 to ensure strict checking passes completely
    assert result.returncode == 0, (
        f"Mypy check failed with exit code {result.returncode}.\n"
        f"Command executed: {' '.join(cmd)}\n"
        f"Target paths: {paths}\n"
        f"Stdout:\n{result.stdout}\n"
        f"Stderr:\n{result.stderr}"
    )

    # Assert that mypy actually scanned files and reported success without violations
    import re

    match = re.search(r"Success: no issues found in (\d+) source files", result.stdout)
    assert match is not None, (
        f"Mypy output did not report strict success format or found violations.\n"
        f"Command executed: {' '.join(cmd)}\n"
        f"Target paths: {paths}\n"
        f"Stdout:\n{result.stdout}\n"
        f"Stderr:\n{result.stderr}"
    )
    num_files = int(match.group(1))
    assert num_files > 0, (
        f"Mypy did not check any files (0 files checked)!\n"
        f"Command executed: {' '.join(cmd)}\n"
        f"Target paths: {paths}\n"
        f"Stdout:\n{result.stdout}"
    )


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


def _walk_within_scope(node: ast.AST) -> list[ast.AST]:
    """Helper to walk the AST within the current function/method scope only, ignoring nested definitions."""
    result = []
    queue = [node]
    while queue:
        curr = queue.pop(0)
        result.append(curr)
        if isinstance(curr, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and curr is not node:
            continue
        for child in ast.iter_child_nodes(curr):
            queue.append(child)
    return result


def _get_cyclomatic_complexity(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Helper to calculate the cyclomatic complexity of a function/method node."""
    complexity = 1
    for child in _walk_within_scope(node):
        if child is node:
            continue
        if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            complexity += 1
    return complexity


def _get_function_nloc(node: ast.FunctionDef | ast.AsyncFunctionDef, file_lines: list[str]) -> int:
    """Helper to calculate the NLOC (excluding blank lines, comments, and docstrings) of a function/method."""
    body_nodes = node.body
    # Exclude docstring if present at the start of the body
    if body_nodes:
        first_stmt = body_nodes[0]
        if isinstance(first_stmt, ast.Expr) and (
            isinstance(first_stmt.value, ast.Constant)
            and isinstance(first_stmt.value.value, str)
            or (hasattr(ast, "Str") and isinstance(first_stmt.value, ast.Str))
        ):
            body_nodes = body_nodes[1:]
    if not body_nodes:
        return 0
    start_line = min(n.lineno for n in body_nodes)
    end_linenos = [n.end_lineno for n in body_nodes if getattr(n, "end_lineno", None) is not None]
    if not end_linenos:
        return 0
    valid_ends = [val for val in end_linenos if val is not None]
    if not valid_ends:
        return 0
    end_line = max(valid_ends)
    sliced_lines = file_lines[start_line - 1 : end_line]
    nloc = 0
    for line in sliced_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            nloc += 1
    return nloc


def _get_max_nesting_depth(nodes: typing.Sequence[ast.AST], current_depth: int = 0) -> int:
    """Helper to recursively calculate the maximum nesting depth of control structures."""
    max_depth = current_depth
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
            next_depth = current_depth + 1
            if isinstance(node, ast.If):
                body_depth = _get_max_nesting_depth(node.body, next_depth)
                max_depth = max(max_depth, body_depth)
                # Keep elif chains at the same conceptual depth as the parent If
                if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                    orelse_depth = _get_max_nesting_depth(node.orelse, current_depth)
                else:
                    orelse_depth = _get_max_nesting_depth(node.orelse, next_depth)
                max_depth = max(max_depth, orelse_depth)
            elif isinstance(node, (ast.For, ast.While)):
                body_depth = _get_max_nesting_depth(node.body, next_depth)
                orelse_depth = _get_max_nesting_depth(node.orelse, next_depth)
                max_depth = max(max_depth, body_depth, orelse_depth)
            elif isinstance(node, ast.Try):
                body_depth = _get_max_nesting_depth(node.body, next_depth)
                max_depth = max(max_depth, body_depth)
                for handler in node.handlers:
                    handler_depth = _get_max_nesting_depth([handler], current_depth)
                    max_depth = max(max_depth, handler_depth)
                orelse_depth = _get_max_nesting_depth(node.orelse, next_depth)
                final_depth = _get_max_nesting_depth(node.finalbody, next_depth)
                max_depth = max(max_depth, orelse_depth, final_depth)
            elif isinstance(node, ast.ExceptHandler):
                body_depth = _get_max_nesting_depth(node.body, next_depth)
                max_depth = max(max_depth, body_depth)
        else:
            children = [
                c
                for c in ast.iter_child_nodes(node)
                if not isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            ]
            child_depth = _get_max_nesting_depth(children, current_depth)
            max_depth = max(max_depth, child_depth)
    return max_depth


def _get_branch_count(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Helper to count total branch nodes (If, For, While, ExceptHandler) in the function scope."""
    count = 0
    for child in _walk_within_scope(node):
        if child is node:
            continue
        if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
            count += 1
    return count


def _get_return_count(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Helper to count total ast.Return nodes in the function scope."""
    count = 0
    for child in _walk_within_scope(node):
        if child is node:
            continue
        if isinstance(child, ast.Return):
            count += 1
    return count


def _get_inner_layer_imported_names(tree: ast.AST) -> set[str]:
    """Helper to extract names imported from inner layers (Domain, Application, Adapters)."""
    inner_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                if name.name.startswith(
                    ("agentic_workflow.domain", "agentic_workflow.application", "agentic_workflow.adapters")
                ):
                    asname = name.asname or name.name.split(".")[-1]
                    inner_names.add(asname)
        elif (
            isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.startswith(
                ("agentic_workflow.domain", "agentic_workflow.application", "agentic_workflow.adapters")
            )
        ):
            for name in node.names:
                asname = name.asname or name.name
                inner_names.add(asname)
    return inner_names


def _resolve_base_name(base_node: ast.AST) -> str | None:
    """Helper to resolve a base class name to a root identifier name."""
    if isinstance(base_node, ast.Name):
        return base_node.id
    if isinstance(base_node, ast.Attribute) and isinstance(base_node.value, ast.Name):
        return base_node.value.id
    return None


def _is_exempt_from_inheritance(class_name: str, file_path: pathlib.Path) -> bool:
    """Check if a frameworks class is exempt from direct inner abstraction inheritance checks."""
    if class_name == "DependencyContainer":
        return True
    if class_name.endswith(("Config", "ConfigLoader", "Loader", "Builder", "Registry", "Mapper")):
        return True
    return "config" in file_path.parts or "graph" in file_path.parts


def _find_framework_python_files() -> list[pathlib.Path]:
    """Find all python source files in the frameworks layer."""
    root_dir = pathlib.Path(__file__).parent.parent.resolve()
    framework_dir = root_dir / "src" / "agentic_workflow" / "frameworks"
    if not framework_dir.exists():
        return []
    return [
        p
        for p in framework_dir.rglob("*.py")
        if p.name not in ("__init__.py", "main.py") and "validation" not in p.parts
    ]


def test_framework_cyclomatic_complexity() -> None:
    """TC-QUALITY-004: Ensure any framework code function/method has a Cyclomatic Complexity <= 2."""
    violations = []
    for file_path in _find_framework_python_files():
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    cc = _get_cyclomatic_complexity(node)
                    if cc > 2:
                        violations.append(
                            f"{file_path}:{node.lineno}: Function '{node.name}' "
                            f"has Cyclomatic Complexity of {cc} (violates CC <= 2)."
                        )
        except Exception as exc:
            violations.append(f"Failed to parse {file_path}: {exc}")

    assert not violations, "Complexity violations in frameworks layer:\n" + "\n".join(violations)


def test_framework_function_nloc() -> None:
    """TC-QUALITY-005: Ensure any framework code function/method NLOC (excluding blanks/comments/docstrings) is <= 6."""
    violations = []
    for file_path in _find_framework_python_files():
        try:
            content = file_path.read_text(encoding="utf-8")
            file_lines = content.splitlines()
            tree = ast.parse(content, filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    nloc = _get_function_nloc(node, file_lines)
                    if nloc > 6:
                        violations.append(
                            f"{file_path}:{node.lineno}: Function '{node.name}' "
                            f"has NLOC of {nloc} (violates NLOC <= 6)."
                        )
        except Exception as exc:
            violations.append(f"Failed to parse {file_path}: {exc}")

    assert not violations, "NLOC violations in frameworks layer:\n" + "\n".join(violations)


def test_framework_nesting_depth() -> None:
    """TC-QUALITY-006: Ensure any framework code nesting depth is <= 1."""
    violations = []
    for file_path in _find_framework_python_files():
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    depth = _get_max_nesting_depth(node.body)
                    if depth > 1:
                        violations.append(
                            f"{file_path}:{node.lineno}: Function '{node.name}' "
                            f"has nesting depth of {depth} (violates depth <= 1)."
                        )
        except Exception as exc:
            violations.append(f"Failed to parse {file_path}: {exc}")

    assert not violations, "Nesting depth violations in frameworks layer:\n" + "\n".join(violations)


def test_framework_branch_count() -> None:
    """TC-QUALITY-007: Ensure any framework code branch count is <= 1."""
    violations = []
    for file_path in _find_framework_python_files():
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    branches = _get_branch_count(node)
                    if branches > 1:
                        violations.append(
                            f"{file_path}:{node.lineno}: Function '{node.name}' "
                            f"has branch count of {branches} (violates branch <= 1)."
                        )
        except Exception as exc:
            violations.append(f"Failed to parse {file_path}: {exc}")

    assert not violations, "Branch count violations in frameworks layer:\n" + "\n".join(violations)


def test_framework_return_count() -> None:
    """TC-QUALITY-008: Ensure any framework code ast.Return node count is <= 1."""
    violations = []
    for file_path in _find_framework_python_files():
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    returns = _get_return_count(node)
                    if returns > 1:
                        violations.append(
                            f"{file_path}:{node.lineno}: Function '{node.name}' "
                            f"has return count of {returns} (violates return <= 1)."
                        )
        except Exception as exc:
            violations.append(f"Failed to parse {file_path}: {exc}")

    assert not violations, "Return count violations in frameworks layer:\n" + "\n".join(violations)


def test_frameworks_inheritance_abstraction() -> None:
    """TC-QUALITY-009: Ensure framework code functional class inherits from inner layer abstraction."""
    violations = []
    for file_path in _find_framework_python_files():
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            inner_names = _get_inner_layer_imported_names(tree)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if _is_exempt_from_inheritance(node.name, file_path):
                        continue
                    # Check base classes
                    implements_inner = False
                    for base in node.bases:
                        resolved = _resolve_base_name(base)
                        if resolved and resolved in inner_names:
                            implements_inner = True
                            break
                    if not implements_inner:
                        violations.append(
                            f"{file_path}:{node.lineno}: Class '{node.name}' "
                            f"does not inherit from any inner layer (Domain, Application, Adapters) abstraction."
                        )
        except Exception as exc:
            violations.append(f"Failed to parse {file_path}: {exc}")

    assert not violations, "Inheritance violations in frameworks layer:\n" + "\n".join(violations)


def test_frameworks_methods_override_inner_abstraction() -> None:
    """TC-QUALITY-010: Ensure every frameworks class method overrides a method declared in its inner abstraction."""
    import importlib

    violations = []

    for file_path in _find_framework_python_files():
        # Get absolute dot path for importing the module
        parts = list(file_path.parts)
        if "agentic_workflow" not in parts:
            continue
        idx = parts.index("agentic_workflow")
        mod_parts = parts[idx:]
        module_name = ".".join(mod_parts)
        if module_name.endswith(".py"):
            module_name = module_name[:-3]

        try:
            mod = importlib.import_module(module_name)
        except Exception as exc:
            violations.append(f"Failed to import {module_name}: {exc}")
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if _is_exempt_from_inheritance(node.name, file_path):
                        continue

                    cls_obj = getattr(mod, node.name, None)
                    if cls_obj is None:
                        continue

                    # Find all inner layer abstraction base classes
                    inner_bases = []
                    for base in cls_obj.__mro__:
                        if base is cls_obj or base is object:
                            continue
                        base_mod = base.__module__
                        if base_mod.startswith(
                            ("agentic_workflow.domain", "agentic_workflow.application", "agentic_workflow.adapters")
                        ):
                            inner_bases.append(base)

                    if not inner_bases:
                        continue

                    # Get all methods defined in the ClassDef of the AST
                    defined_methods = [
                        child for child in node.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ]

                    for m_node in defined_methods:
                        m_name = m_node.name
                        if m_name.startswith("__") and m_name.endswith("__"):
                            continue

                        # Verify if the method is declared in any base class
                        declared_in_base = False
                        for base in inner_bases:
                            if m_name in dir(base):
                                declared_in_base = True
                                break

                        if not declared_in_base:
                            base_names = [b.__name__ for b in inner_bases]
                            violations.append(
                                f"{file_path}:{m_node.lineno}: Method '{m_name}' in class '{node.name}' "
                                f"is not declared in any of its inner abstraction base classes ({base_names})."
                            )
        except Exception as exc:
            violations.append(f"Failed to parse {file_path}: {exc}")

    assert not violations, "Methods override violations in frameworks layer:\n" + "\n".join(violations)


def test_frameworks_no_module_level_functions() -> None:
    """TC-QUALITY-011: Ensure no module-level (outside class) functions or async functions exist in framework files."""
    violations = []

    class ModuleLevelFunctionVisitor(ast.NodeVisitor):
        def __init__(self, filepath: pathlib.Path):
            self.filepath = filepath
            self.in_class = False

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            old_in_class = self.in_class
            self.in_class = True
            self.generic_visit(node)
            self.in_class = old_in_class

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            if not self.in_class:
                violations.append(
                    f"{self.filepath}:{node.lineno}: Function '{node.name}' "
                    f"is defined outside a class in frameworks layer (TC-QUALITY-011)."
                )
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            if not self.in_class:
                violations.append(
                    f"{self.filepath}:{node.lineno}: Async function '{node.name}' "
                    f"is defined outside a class in frameworks layer (TC-QUALITY-011)."
                )
            self.generic_visit(node)

    for file_path in _find_framework_python_files():
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            visitor = ModuleLevelFunctionVisitor(file_path)
            visitor.visit(tree)
        except Exception as exc:
            violations.append(f"Failed to parse {file_path}: {exc}")

    assert not violations, "Module-level function violations in frameworks layer:\n" + "\n".join(violations)
