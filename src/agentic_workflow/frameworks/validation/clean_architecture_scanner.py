"""Clean Architecture Boundary Violations Scanner.

Scans Python source files to ensure inner layers do not access outer layers.
Checks for static imports, dynamic imports, exec/eval, sys.modules lookup,
DI container abuse, string type annotations, direct environment variable access,
and direct file I/O within prohibited layers.
"""

import ast
import io
import os
import re
import tokenize
from pathlib import Path
from typing import NamedTuple

# Match comment starting with '#' followed by optional whitespace, then 'pragma', then a word boundary
PRAGMA_REGEX = re.compile(r"^#\s*pragma\b", re.IGNORECASE)
# Match comment starting with '#' followed by optional whitespace, then 'type', then a word boundary
TYPE_REGEX = re.compile(r"^#\s*type\b", re.IGNORECASE)


class BoundaryViolation(NamedTuple):
    """Represents a single Clean Architecture boundary violation."""

    file_path: str
    line: int
    column: int
    category: str
    message: str


class CleanArchitectureBoundaryScanner:
    """Scanner for enforcing Clean Architecture boundaries and blocking illegal injections."""

    LAYERS = ["domain", "application", "adapters", "frameworks"]
    LAYER_RANKS = {"domain": 1, "application": 2, "adapters": 3, "frameworks": 4}

    # Blocked classes/symbols in inner layers to prevent DI container/locator abuse
    BLOCKED_LOCATORS = {"DependencyContainer", "Container", "ServiceLocator"}

    # Whitelist of allowed base module/package names in inner layers (domain, application, adapters)
    ALLOWED_INNER_DEPENDENCIES = {
        "typing",
        "dataclasses",
        "re",
        "enum",
        "abc",
        "collections",
        "math",
        "random",
        "warnings",
        "traceback",
        "types",
        "icontract",
    }

    def __init__(self, project_root: str | None = None) -> None:
        """Initialize the scanner with an optional project root."""
        self.project_root = Path(project_root).resolve() if project_root else Path.cwd().resolve()

    def get_layer_from_path(self, path: Path) -> str | None:
        """Determine the Clean Architecture layer of a given file path."""
        try:
            rel_parts = path.resolve().relative_to(self.project_root).parts
        except ValueError:
            rel_parts = path.parts

        for part in rel_parts:
            if part in self.LAYER_RANKS:
                return part
        return None

    def get_layer_from_module(self, module_name: str) -> str | None:
        """Determine the layer of an imported module by scanning its segments."""
        parts = module_name.split(".")
        for part in parts:
            if part in self.LAYER_RANKS:
                return part
        return None

    def resolve_module_path(self, file_path: Path) -> str:
        """Map a physical file path to its absolute python module dot path."""
        try:
            rel = file_path.resolve().relative_to(self.project_root)
        except ValueError:
            rel = file_path

        parts = list(rel.parts)
        if parts and parts[0] == "src":
            parts = parts[1:]

        if parts and parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]
            if parts[-1] == "__init__":
                parts = parts[:-1]

        return ".".join(parts)

    def resolve_relative_import(self, current_module: str, relative_module: str | None, level: int) -> str:
        """Resolve a relative import (e.g. from ..entities import X) to absolute module path."""
        parts = current_module.split(".")
        base = "" if level > len(parts) else ".".join(parts[: len(parts) - level])

        if relative_module:
            return f"{base}.{relative_module}" if base else relative_module
        return base

    def _read_file_content(self, path: Path) -> tuple[str, list[BoundaryViolation]]:
        """Read text from file, returning content and read errors if any."""
        try:
            return path.read_text(encoding="utf-8"), []
        except Exception as e:
            return "", [
                BoundaryViolation(
                    file_path=str(path),
                    line=1,
                    column=0,
                    category="file_error",
                    message=f"Failed to read file: {e}",
                )
            ]

    def _check_comment_pragma(self, comment_str: str, line_text: str) -> bool:
        """Verify if a pragma comment violates the entry point exception."""
        if not PRAGMA_REGEX.match(comment_str):
            return False
        normalized_line = "".join(line_text.split()).lower()
        return not ("if" + "__name__" + "==" in normalized_line and "__main__" in normalized_line)

    def _scan_comments_via_tokens(self, content: str, file_path: str, current_rank: int) -> list[BoundaryViolation]:
        """Scan comments using tokenization."""
        violations = []
        tokens = tokenize.generate_tokens(io.StringIO(content).readline)
        for token in tokens:
            if token.type != tokenize.COMMENT:
                continue
            comment_str = token.string
            line_num, col_num = token.start

            if self._check_comment_pragma(comment_str, content.splitlines()[line_num - 1]):
                violations.append(
                    BoundaryViolation(
                        file_path=file_path,
                        line=line_num,
                        column=col_num,
                        category="pragma_no_cover_abuse",
                        message=(
                            "Illegal pragma: no cover bypass detected outside if __name__ == '__main__':. "
                            "All pragma comments are strictly banned in all layers outside the entry point."
                        ),
                    )
                )

            if current_rank <= 3 and TYPE_REGEX.match(comment_str):
                violations.append(
                    BoundaryViolation(
                        file_path=file_path,
                        line=line_num,
                        column=col_num,
                        category="type_ignore_abuse",
                        message=(
                            "Illegal use of '# type' comment in inner layer. "
                            "Type comments are strictly banned in inner layers."
                        ),
                    )
                )
        return violations

    def _scan_comments_via_regex(self, content: str, file_path: str, current_rank: int) -> list[BoundaryViolation]:
        """Fallback to pure regex scan for comments if tokenization fails."""
        violations = []
        for idx, line in enumerate(content.splitlines(), start=1):
            if "#" not in line:
                continue
            comment_idx = line.find("#")
            comment_str = line[comment_idx:]

            if self._check_comment_pragma(comment_str, line):
                violations.append(
                    BoundaryViolation(
                        file_path=file_path,
                        line=idx,
                        column=comment_idx,
                        category="pragma_no_cover_abuse",
                        message=(
                            "Illegal pragma: no cover bypass detected outside if __name__ == '__main__':. "
                            "All pragma comments are strictly banned in all layers outside the entry point."
                        ),
                    )
                )

            if current_rank <= 3 and TYPE_REGEX.match(comment_str):
                violations.append(
                    BoundaryViolation(
                        file_path=file_path,
                        line=idx,
                        column=comment_idx,
                        category="type_ignore_abuse",
                        message=(
                            "Illegal use of '# type' comment in inner layer. "
                            "Type comments are strictly banned in inner layers."
                        ),
                    )
                )
        return violations

    def _scan_ast_tree(
        self, content: str, path: Path, current_layer: str, current_rank: int
    ) -> list[BoundaryViolation]:
        """Parse and run the AST boundary visitor on the content."""
        violations = []
        try:
            tree = ast.parse(content, filename=str(path))
        except SyntaxError as se:
            return [
                BoundaryViolation(
                    file_path=str(path),
                    line=se.lineno or 1,
                    column=se.offset or 0,
                    category="syntax_error",
                    message=f"Syntax error during parsing: {se.msg}",
                )
            ]

        current_module = self.resolve_module_path(path)
        visitor = BoundaryVisitor(
            file_path=str(path),
            current_layer=current_layer,
            current_rank=current_rank,
            current_module=current_module,
            scanner=self,
        )
        visitor.visit(tree)
        violations.extend(visitor.violations)
        return violations

    def scan_file(self, file_path: str) -> list[BoundaryViolation]:
        """Parse and scan a single Python file for Clean Architecture violations."""
        path = Path(file_path).resolve()
        current_layer = self.get_layer_from_path(path)
        if not current_layer:
            return []

        current_rank = self.LAYER_RANKS[current_layer]

        content, read_violations = self._read_file_content(path)
        if read_violations:
            return read_violations

        violations = []
        try:
            violations.extend(self._scan_comments_via_tokens(content, str(path), current_rank))
        except Exception:
            violations.extend(self._scan_comments_via_regex(content, str(path), current_rank))

        violations.extend(self._scan_ast_tree(content, path, current_layer, current_rank))
        return violations

    def scan_directory(self, directory_path: str) -> list[BoundaryViolation]:
        """Scan all Python files in a directory recursively for violations."""
        violations = []
        dir_path = Path(directory_path).resolve()
        for root, _, files in os.walk(dir_path):
            parts = Path(root).parts
            if any(p in parts for p in (".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache")):
                continue
            for file in files:
                if file.endswith(".py"):
                    violations.extend(self.scan_file(os.path.join(root, file)))
        return violations


class BoundaryVisitor(ast.NodeVisitor):
    """AST Visitor to inspect nodes for Clean Architecture boundary violations."""

    def __init__(
        self,
        file_path: str,
        current_layer: str,
        current_rank: int,
        current_module: str,
        scanner: CleanArchitectureBoundaryScanner,
    ) -> None:
        """Initialize the AST boundary visitor with file metadata and a scanner reference."""
        self.file_path = file_path
        self.current_layer = current_layer
        self.current_rank = current_rank
        self.current_module = current_module
        self.scanner = scanner
        self.violations: list[BoundaryViolation] = []
        self._recorded_keys: set[tuple[int, int, str]] = set()
        self.class_stack: list[ast.ClassDef] = []

    def _add_violation(self, node: ast.AST, category: str, message: str) -> None:
        key = (getattr(node, "lineno", 1), getattr(node, "col_offset", 0), category)
        if key in self._recorded_keys:
            return
        self._recorded_keys.add(key)
        self.violations.append(
            BoundaryViolation(
                file_path=self.file_path,
                line=key[0],
                column=key[1],
                category=category,
                message=message,
            )
        )

    def _check_module_dependency(self, node: ast.AST, module_name: str, category: str = "static_import") -> None:
        """Check if importing or referencing a module violates boundary ranks."""
        target_layer = self.scanner.get_layer_from_module(module_name)
        if target_layer:
            target_rank = self.scanner.LAYER_RANKS[target_layer]
            if target_rank > self.current_rank:
                self._add_violation(
                    node,
                    category,
                    f"Illegal dependency: Layer '{self.current_layer}' (rank {self.current_rank}) "
                    f"cannot access layer '{target_layer}' (rank {target_rank}) "
                    f"via module '{module_name}'.",
                )

    def _check_inner_dependency_whitelist(self, node: ast.AST, module_name: str) -> None:
        """Check that imports in inner layers (rank <= 3) are restricted to the whitelist or self-project."""
        if self.current_rank > 3:
            return
        path = Path(self.file_path)
        if path.name == "sys.py":
            return
        try:
            Path(self.file_path).resolve().relative_to(self.scanner.project_root.resolve())
        except ValueError:
            return
        if module_name == "agentic_workflow" or module_name.startswith("agentic_workflow."):
            return

        base_module = module_name.split(".")[0]
        if base_module in {"__future__", ""}:
            return

        if base_module not in self.scanner.ALLOWED_INNER_DEPENDENCIES:
            whitelist_sorted = sorted(self.scanner.ALLOWED_INNER_DEPENDENCIES)
            self._add_violation(
                node,
                "external_dependency_violation",
                f"Illegal external dependency: Inner layer '{self.current_layer}' is not allowed to import "
                f"external/third-party module '{module_name}'. Whitelist: {whitelist_sorted}",
            )

    def _get_attribute_chain(self, node: ast.AST) -> list[str]:
        """Recursively retrieve all segments of an attribute lookup chain."""
        if isinstance(node, ast.Name):
            return [node.id]
        elif isinstance(node, ast.Attribute):
            return self._get_attribute_chain(node.value) + [node.attr]
        return []

    def visit_Import(self, node: ast.Import) -> None:
        """Inspect absolute imports."""
        for alias in node.names:
            self._check_module_dependency(node, alias.name)
            self._check_inner_dependency_whitelist(node, alias.name)
            # Prevent DI locator/container import
            for locator in self.scanner.BLOCKED_LOCATORS:
                if locator in alias.name and self.current_rank < 3:
                    self._add_violation(
                        node,
                        "di_container_abuse",
                        f"Locator class reference '{alias.name}' is blocked in layer '{self.current_layer}'.",
                    )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Inspect absolute and relative imports."""
        # Resolve imported module
        module_name = node.module
        if node.level > 0:
            resolved = self.scanner.resolve_relative_import(self.current_module, module_name, node.level)
            self._check_module_dependency(node, resolved)
            self._check_inner_dependency_whitelist(node, resolved)
            module_name_resolved = resolved
        else:
            assert module_name is not None
            self._check_module_dependency(node, module_name)
            self._check_inner_dependency_whitelist(node, module_name)
            module_name_resolved = module_name

        # Inspect imported names
        for alias in node.names:
            full_name = f"{module_name_resolved}.{alias.name}"
            self._check_module_dependency(node, full_name)
            self._check_inner_dependency_whitelist(node, full_name)

            # Prevent DI locator/container import
            if alias.name in self.scanner.BLOCKED_LOCATORS and self.current_rank < 3:
                self._add_violation(
                    node,
                    "di_container_abuse",
                    f"Import of blocked locator '{alias.name}' is prohibited in layer '{self.current_layer}'.",
                )
        self.generic_visit(node)

    def _check_exec_eval(self, node: ast.Call, func_name: str) -> None:
        """Block exec and eval in inner layers."""
        if func_name in {"exec", "eval"} and self.current_rank < 3:
            self._add_violation(
                node,
                "exec_eval",
                f"Dynamic execution '{func_name}' is forbidden in inner layer '{self.current_layer}'.",
            )

    def _check_dynamic_imports(self, node: ast.Call, func_name: str) -> None:
        """Inspect dynamic imports: importlib.import_module and __import__."""
        if func_name not in {"import_module", "__import__"} or not node.args:
            return

        first_arg = node.args[0]
        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
            self._check_module_dependency(node, first_arg.value, category="dynamic_import")
        elif self.current_rank < 3:
            self._add_violation(
                node,
                "dynamic_import",
                f"Dynamic import with variable argument is prohibited in inner layer '{self.current_layer}'.",
            )

    def _check_env_access_call(self, node: ast.Call) -> None:
        """Inspect os.getenv direct environment access."""
        if self.current_rank >= 3:
            return
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "os"
            and node.func.attr == "getenv"
        ):
            self._add_violation(
                node,
                "env_access",
                f"Direct environment read via 'os.getenv' is prohibited in layer '{self.current_layer}'."
                " Use configuration injection.",
            )

    def _check_file_io_call(self, node: ast.Call, func_name: str) -> None:
        """Inspect direct file I/O operations in domain."""
        if self.current_layer != "domain":
            return

        if func_name == "open":
            self._add_violation(
                node,
                "file_io",
                "Direct file operations via 'open()' are prohibited in 'domain' layer. Use Repository ports.",
            )

        if isinstance(node.func, ast.Attribute) and node.func.attr in {
            "read_text",
            "write_text",
            "read_bytes",
            "write_bytes",
            "open",
        }:
            self._add_violation(
                node,
                "file_io",
                f"Direct file operation '{node.func.attr}' is prohibited in 'domain' layer. Use Repository ports.",
            )

    def _check_outer_instantiation_call(self, node: ast.Call) -> None:
        """Check for outer layer class instantiation inside core layers (rank < 3)."""
        if self.current_rank >= 3:
            return
        chain = self._get_attribute_chain(node.func)
        if any(segment in {"adapters", "frameworks"} for segment in chain):
            dot_path = ".".join(chain)
            self._add_violation(
                node,
                "illegal_instantiation",
                f"Illegal outer-layer class instantiation: Core layer '{self.current_layer}' "
                f"is prohibited from directly instantiating outer layer class '{dot_path}'.",
            )

    def visit_Call(self, node: ast.Call) -> None:
        """Inspect dynamic imports, exec/eval, environment variables, and file I/O."""
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        self._check_exec_eval(node, func_name)
        self._check_dynamic_imports(node, func_name)
        self._check_env_access_call(node)
        self._check_file_io_call(node, func_name)
        self._check_outer_instantiation_call(node)

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Inspect os.environ access."""
        if (
            isinstance(node.value, ast.Name)
            and node.value.id == "os"
            and node.attr == "environ"
            and self.current_rank < 3
        ):
            self._add_violation(
                node,
                "env_access",
                f"Direct environment read via 'os.environ' is prohibited in layer '{self.current_layer}'."
                " Use configuration injection.",
            )
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Inspect sys.modules query."""
        is_sys_modules = False
        val = node.value
        if isinstance(val, ast.Attribute) and isinstance(val.value, ast.Name):
            is_sys_modules = val.value.id == "sys" and val.attr == "modules"
        elif isinstance(val, ast.Name):
            is_sys_modules = val.id == "modules"

        if is_sys_modules:
            # Check the lookup key
            slice_val = getattr(node, "slice", None)
            if slice_val is not None:
                # Handle python 3.9+ Index node wrapping
                if slice_val.__class__.__name__ == "Index":
                    slice_val = getattr(slice_val, "value", None)

                if isinstance(slice_val, ast.Constant) and isinstance(slice_val.value, str):
                    self._check_module_dependency(node, slice_val.value, category="sys_modules")
                elif self.current_rank < 3:
                    self._add_violation(
                        node,
                        "sys_modules",
                        f"Dynamic module lookup via sys.modules in inner layer '{self.current_layer}' is prohibited.",
                    )

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Prevent direct references to DI locator classes."""
        if node.id in self.scanner.BLOCKED_LOCATORS and self.current_rank < 3:
            # If not in an import statement context (handled in visit_Import/visit_ImportFrom)
            self._add_violation(
                node,
                "di_container_abuse",
                f"Direct reference to blocked locator class '{node.id}' in inner layer '{self.current_layer}'.",
            )
        self.generic_visit(node)

    def _check_string_annotation(self, node: ast.AST, annotation_str: str) -> None:
        """Inspect a string annotation to verify it doesn't reference outer layers."""
        self._check_module_dependency(node, annotation_str, category="string_annotation")

    def visit_Constant(self, node: ast.Constant) -> None:
        """Handle modern Constant nodes (which represent strings in python 3.8+)."""
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Inspect string type annotations in annotated assignments."""
        if isinstance(node.annotation, ast.Constant) and isinstance(node.annotation.value, str):
            self._check_string_annotation(node, node.annotation.value)
        self.generic_visit(node)

    def visit_arg(self, node: ast.arg) -> None:
        """Inspect string type annotations in function arguments."""
        if isinstance(node.annotation, ast.Constant) and isinstance(node.annotation.value, str):
            self._check_string_annotation(node, node.annotation.value)
        self.generic_visit(node)

    def _visit_function_like(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Helper to process function definitions."""
        if isinstance(node.returns, ast.Constant) and isinstance(node.returns.value, str):
            self._check_string_annotation(node, node.returns.value)
        self._check_ellipsis(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Inspect string type annotations in function return types and check for ellipsis abuse."""
        self._visit_function_like(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Inspect string type annotations in function return types and check for ellipsis abuse."""
        self._visit_function_like(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track current class to allow ellipsis within Protocol classes."""
        self.class_stack.append(node)
        self.generic_visit(node)
        self.class_stack.pop()

    def _is_ellipsis_body(self, body: list[ast.stmt]) -> bool:
        """Check if the function body consists of exactly one Ellipsis statement."""
        if len(body) != 1:
            return False
        stmt = body[0]
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            return stmt.value.value is Ellipsis
        return False

    def _is_abstract_method(self, decorator_list: list[ast.expr]) -> bool:
        """Check if the function has an abstractmethod decorator."""
        for dec in decorator_list:
            if isinstance(dec, ast.Name) and dec.id == "abstractmethod":
                return True
            if isinstance(dec, ast.Attribute) and dec.attr == "abstractmethod":
                return True
        return False

    def _is_protocol_class(self) -> bool:
        """Check if the current class in stack is a Protocol class."""
        if not self.class_stack:
            return False
        parent_class = self.class_stack[-1]
        for base in parent_class.bases:
            if isinstance(base, ast.Name) and base.id == "Protocol":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Protocol":
                return True
        return False

    def _check_ellipsis(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Enforce pass over ellipsis in concrete dry run implementations."""
        if not self._is_ellipsis_body(node.body):
            return

        if self._is_abstract_method(node.decorator_list) or self._is_protocol_class():
            return

        self._add_violation(
            node,
            "ellipsis_abuse",
            f"Illegal use of ellipsis '...' in concrete function '{node.name}'. Must use 'pass' instead of '...'.",
        )
