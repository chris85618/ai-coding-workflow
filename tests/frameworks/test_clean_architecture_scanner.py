"""Unit and integration tests for CleanArchitectureBoundaryScanner.

Verifies boundary scans under various legal and illegal conditions, including
static imports, relative imports, dynamic imports, exec/eval, sys.modules,
DI container locator references, string type annotations, os.environ/os.getenv read,
and direct file I/O operations inside inner layers.
"""

from pathlib import Path

import pytest

from agentic_workflow.frameworks.validation.clean_architecture_scanner import (
    CleanArchitectureBoundaryScanner,
)


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create a mock workspace with clean architecture layers for deterministic scanning."""
    # Structure:
    # tmp_path/
    #   src/
    #     agentic_workflow/
    #       domain/
    #       application/
    #       adapters/
    #       frameworks/
    (tmp_path / "src" / "agentic_workflow" / "domain").mkdir(parents=True)
    (tmp_path / "src" / "agentic_workflow" / "application").mkdir(parents=True)
    (tmp_path / "src" / "agentic_workflow" / "adapters").mkdir(parents=True)
    (tmp_path / "src" / "agentic_workflow" / "frameworks").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def scanner(temp_project: Path) -> CleanArchitectureBoundaryScanner:
    """Provide a scanner configured with the mock project root."""
    return CleanArchitectureBoundaryScanner(project_root=str(temp_project))


# ── Test Suite: Layer Determination & Resolve Module Path Edge Cases ─────────


def test_get_layer_from_path(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Verify correct CA layer classification based on file paths."""
    domain_file = temp_project / "src" / "agentic_workflow" / "domain" / "aggregates" / "pipeline.py"
    app_file = temp_project / "src" / "agentic_workflow" / "application" / "use_cases" / "start.py"
    adapter_file = temp_project / "src" / "agentic_workflow" / "adapters" / "persistence" / "db.py"
    framework_file = temp_project / "src" / "agentic_workflow" / "frameworks" / "graph" / "main.py"
    external_file = temp_project / "scripts" / "build.py"

    assert scanner.get_layer_from_path(domain_file) == "domain"
    assert scanner.get_layer_from_path(app_file) == "application"
    assert scanner.get_layer_from_path(adapter_file) == "adapters"
    assert scanner.get_layer_from_path(framework_file) == "frameworks"
    assert scanner.get_layer_from_path(external_file) is None


def test_get_layer_from_path_value_error(scanner: CleanArchitectureBoundaryScanner) -> None:
    """Trigger ValueError in get_layer_from_path by passing a path that cannot be relative to project_root."""
    out_of_bounds_path = Path("/etc/non_existent_folder/domain/test.py")
    # This should fall back to out_of_bounds_path.parts and still locate "domain"!
    assert scanner.get_layer_from_path(out_of_bounds_path) == "domain"


def test_get_layer_from_module(scanner: CleanArchitectureBoundaryScanner) -> None:
    """Verify correct CA layer classification based on python module dot names."""
    assert scanner.get_layer_from_module("agentic_workflow.domain.aggregates.pipeline") == "domain"
    assert scanner.get_layer_from_module("agentic_workflow.application.use_cases.start") == "application"
    assert scanner.get_layer_from_module("agentic_workflow.adapters.persistence.db") == "adapters"
    assert scanner.get_layer_from_module("agentic_workflow.frameworks.graph.main") == "frameworks"
    assert scanner.get_layer_from_module("os.path") is None


def test_resolve_module_path(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Verify conversion from physical path to python absolute module path."""
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "entities" / "stage.py"
    assert scanner.resolve_module_path(file_path) == "agentic_workflow.domain.entities.stage"

    init_path = temp_project / "src" / "agentic_workflow" / "domain" / "__init__.py"
    assert scanner.resolve_module_path(init_path) == "agentic_workflow.domain"


def test_resolve_module_path_value_error(scanner: CleanArchitectureBoundaryScanner) -> None:
    """Trigger ValueError in resolve_module_path by using an absolute out-of-bounds path."""
    out_of_bounds_path = Path("/etc/external_src/my_module.py")
    res = scanner.resolve_module_path(out_of_bounds_path)
    assert res.endswith("etc.external_src.my_module")


def test_resolve_relative_import_edge_cases(scanner: CleanArchitectureBoundaryScanner) -> None:
    """Verify relative import resolution edge cases, such as level larger than module segments."""
    assert scanner.resolve_relative_import("a.b.c", None, 4) == ""
    assert scanner.resolve_relative_import("a.b.c", "d", 4) == "d"
    assert scanner.resolve_relative_import("a.b.c", "d", 2) == "a.d"


# ── Test Suite: Legal Scenarios ──────────────────────────────────────────────


def test_scan_perfectly_legal_domain_file(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """A pure domain file must have exactly zero violations."""
    code = """
class Pipeline:
    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
        self.status = "pending"

    def start(self) -> None:
        self.status = "running"
"""
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "entities" / "pipeline.py"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(code, encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    assert len(violations) == 0


def test_scan_legal_downward_dependencies(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Verify outer layers can legally import from inner layers."""
    code = """
from agentic_workflow.domain.entities.stage import Stage
from agentic_workflow.application.ports.repositories.pipeline_repository import IPipelineRepository

class CheckpointAdapter(IPipelineRepository):
    def save(self, stage: Stage) -> None:
        pass
"""
    file_path = temp_project / "src" / "agentic_workflow" / "adapters" / "persistence" / "checkpoint.py"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(code, encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    assert len(violations) == 0


# ── Test Suite: 8 Categories of Boundary Violations ──────────────────────────


def test_category1_static_imports(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Domain layer cannot statically import from adapters or frameworks layers."""
    code = """
from agentic_workflow.frameworks.graph import MasterGraph
import agentic_workflow.adapters.persistence.db as database
import DependencyContainer
"""
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "entities" / "broken.py"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(code, encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    assert len(violations) == 4

    categories = [v.category for v in violations]
    messages = [v.message for v in violations]
    assert "static_import" in categories
    assert "di_container_abuse" in categories
    assert "external_dependency_violation" in categories
    assert any("cannot access layer 'frameworks'" in m for m in messages)
    assert any("cannot access layer 'adapters'" in m for m in messages)


def test_category1_relative_imports_violations(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Relative imports that resolve to outer layers are prohibited in inner layers."""
    code = """
from ...adapters.persistence import db, DependencyContainer
"""
    file_path = temp_project / "src" / "agentic_workflow" / "application" / "use_cases" / "run.py"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(code, encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    assert len(violations) == 2  # DB import violation + DependencyContainer locator violation
    categories = [v.category for v in violations]
    assert "static_import" in categories
    assert "di_container_abuse" in categories


def test_category2_dynamic_imports(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Inner layers cannot dynamically import outer layers via importlib or __import__."""
    code = """
import importlib

def load_graph():
    mod = importlib.import_module("agentic_workflow.frameworks.graph")
    other = __import__("agentic_workflow.adapters.llm")
    # Trigger call to non-constant, non-string
    dynamic_val = __import__(123)
    return mod, other, dynamic_val
"""
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "broken_dynamic.py"
    file_path.write_text(code, encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    assert len(violations) >= 2
    categories = [v.category for v in violations]
    messages = [v.message for v in violations]
    non_ext_categories = [c for c in categories if c != "external_dependency_violation"]
    assert all(c == "dynamic_import" for c in non_ext_categories)
    assert any("frameworks" in m for m in messages)
    assert any("adapters" in m for m in messages)


def test_category2_dynamic_imports_generic_variable(
    scanner: CleanArchitectureBoundaryScanner, temp_project: Path
) -> None:
    """Generic variable dynamic imports are completely blocked in inner layers."""
    code = """
import importlib

def load_any(module_name: str):
    return importlib.import_module(module_name)
"""
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "generic_dynamic.py"
    file_path.write_text(code, encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    non_ext_violations = [v for v in violations if v.category != "external_dependency_violation"]
    assert len(non_ext_violations) == 1
    assert non_ext_violations[0].category == "dynamic_import"
    assert "variable argument is prohibited" in non_ext_violations[0].message


def test_category3_exec_eval(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Use of exec or eval is prohibited in domain and application layers."""
    code = """
def run_unsafe(code_str: str):
    exec(code_str)
    return eval("2 + 2")
"""
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "exec_eval_broken.py"
    file_path.write_text(code, encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    assert len(violations) == 2
    assert violations[0].category == "exec_eval"
    assert violations[1].category == "exec_eval"


def test_category4_sys_modules_lookup(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """sys.modules lookup for outer layers is strictly forbidden."""
    code = """
import sys
from sys import modules

def hijack():
    framework_mod = sys.modules["agentic_workflow.frameworks.graph"]
    other_mod = modules["agentic_workflow.adapters.persistence"]
    dynamic_mod = sys.modules[hijack]
    return framework_mod, other_mod, dynamic_mod
"""
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "sys_modules_broken.py"
    file_path.write_text(code, encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    non_ext_violations = [v for v in violations if v.category != "external_dependency_violation"]
    assert len(non_ext_violations) == 3
    categories = [v.category for v in non_ext_violations]
    assert all(c == "sys_modules" for c in categories)


def test_category5_di_container_abuse(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """DI container classes cannot be referenced in domain or application layers."""
    code = """
class MyService:
    def execute(self):
        container = DependencyContainer.get_instance()
        return container.resolve("adapter")
"""
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "di_abuse.py"
    file_path.write_text(code, encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    assert len(violations) == 1
    assert violations[0].category == "di_container_abuse"
    assert "DependencyContainer" in violations[0].message


def test_category6_string_annotations(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """String type annotations referencing outer layers are prohibited in inner layers."""
    code = """
class DomainService:
    def process(
        self, graph: "agentic_workflow.frameworks.graph", normal_arg: int
    ) -> "agentic_workflow.adapters.persistence.db":
        local_var: "agentic_workflow.adapters.persistence.db" = None
        non_string_annot: float = 3.14
        pass
"""
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "annotations_broken.py"
    file_path.write_text(code, encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    assert len(violations) == 3
    categories = [v.category for v in violations]
    messages = [v.message for v in violations]
    assert all(c == "string_annotation" for c in categories)
    assert any("frameworks" in m for m in messages)
    assert any("adapters" in m for m in messages)


def test_category7_direct_environ_access(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Direct access to os.environ or os.getenv is prohibited in domain/application layers."""
    code = """
import os

class ConfigChecker:
    def run(self):
        token = os.getenv("API_TOKEN")
        secret = os.environ["API_SECRET"]
"""
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "env_broken.py"
    file_path.write_text(code, encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    non_ext_violations = [v for v in violations if v.category != "external_dependency_violation"]
    assert len(non_ext_violations) == 2
    categories = [v.category for v in non_ext_violations]
    messages = [v.message for v in non_ext_violations]
    assert all(c == "env_access" for c in categories)
    assert any("os.getenv" in m for m in messages)
    assert any("os.environ" in m for m in messages)


def test_category8_file_io_in_domain(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Direct file I/O operations (open, Path.read_text, etc.) are prohibited in domain layer."""
    code = """
from pathlib import Path

class Reader:
    def run(self):
        with open("test.txt", "r") as f:
            data = f.read()
        p = Path("log.txt")
        p.write_text("done")
"""
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "io_broken.py"
    file_path.write_text(code, encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    non_ext_violations = [v for v in violations if v.category != "external_dependency_violation"]
    assert len(non_ext_violations) == 2
    categories = [v.category for v in non_ext_violations]
    messages = [v.message for v in non_ext_violations]
    assert all(c == "file_io" for c in categories)
    assert any("open()" in m for m in messages)
    assert any("write_text" in m for m in messages)


# ── Test Suite: Exception Handling and File Edge Cases ──────────────────────


def test_scan_file_non_existent(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Scanning a file that does not exist should return a file_error violation."""
    non_existent_file = temp_project / "src" / "agentic_workflow" / "domain" / "non_existent.py"
    violations = scanner.scan_file(str(non_existent_file))
    assert len(violations) == 1
    assert violations[0].category == "file_error"


def test_scan_file_syntax_error(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Scanning a file with a python syntax error should return a syntax_error violation."""
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "syntax.py"
    file_path.write_text("class Broken: def invalid syntax here", encoding="utf-8")

    violations = scanner.scan_file(str(file_path))
    assert len(violations) == 1
    assert violations[0].category == "syntax_error"


def test_scan_file_no_layer(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Scanning a file that has no valid layer returns empty list."""
    file_path = temp_project / "no_layer.py"
    file_path.write_text("x = 10", encoding="utf-8")
    assert scanner.scan_file(str(file_path)) == []


# ── Test Suite: Recursive Directory Scanning ─────────────────────────────────


def test_scan_directory_recursive(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Verify recursive scanning and exclusion of cache and git directories."""
    # Write a legal domain file
    good_code = "class Valid: pass"
    good_path = temp_project / "src" / "agentic_workflow" / "domain" / "valid.py"
    good_path.write_text(good_code, encoding="utf-8")

    # Write a broken domain file
    bad_code = "from agentic_workflow.frameworks.graph import x"
    bad_path = temp_project / "src" / "agentic_workflow" / "domain" / "invalid.py"
    bad_path.write_text(bad_code, encoding="utf-8")

    # Write a file in python cache to verify exclusion
    cache_dir = temp_project / "src" / "agentic_workflow" / "domain" / "__pycache__"
    cache_dir.mkdir()
    (cache_dir / "invalid.py").write_text("from agentic_workflow.frameworks.graph import x", encoding="utf-8")

    # Write a non-py file to verify exclusion branch coverage
    (temp_project / "src" / "agentic_workflow" / "domain" / "notes.txt").write_text("some text", encoding="utf-8")

    # Write a git folder file to verify git exclusion branch coverage
    git_dir = temp_project / "src" / "agentic_workflow" / "domain" / ".git"
    git_dir.mkdir()
    (git_dir / "hidden.py").write_text("from agentic_workflow.frameworks.graph import x", encoding="utf-8")

    violations = scanner.scan_directory(str(temp_project))
    assert len(violations) == 1
    assert violations[0].file_path == str(bad_path.resolve())
    assert violations[0].category == "static_import"


# ── Test Suite: AST Index Python 3.9+ Slice Mocking ──────────────────────────


def test_sys_modules_index_mocking(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Verify handling of ast.Index node wrapping in sys.modules subscripts."""
    # Construct a custom AST node structure that has an Index node to trigger
    # slice_val.__class__.__name__ == "Index" checking.
    import ast

    code = "import sys; x = sys.modules['agentic_workflow.frameworks.graph']"
    tree = ast.parse(code)

    # Let's inspect the Subscript node and wrap its slice inside a mock class named "Index"
    class Index:
        def __init__(self, value: ast.AST) -> None:
            self.value = value

    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            # Wrap the Constant slice inside an Index
            original_slice = node.slice
            node.slice = Index(original_slice)  # type: ignore

    # Now run the visitor manually
    file_path = temp_project / "src" / "agentic_workflow" / "domain" / "entities" / "mocked_index.py"
    from agentic_workflow.frameworks.validation.clean_architecture_scanner import BoundaryVisitor

    visitor = BoundaryVisitor(
        file_path=str(file_path),
        current_layer="domain",
        current_rank=1,
        current_module="agentic_workflow.domain",
        scanner=scanner,
    )
    visitor.visit(tree)

    sys_violations = [v for v in visitor.violations if v.category == "sys_modules"]
    assert len(sys_violations) == 1
    assert sys_violations[0].category == "sys_modules"
    assert "frameworks" in sys_violations[0].message

    # Construct a subscript node with slice = None to test that branch
    no_slice_node = ast.Subscript(
        value=ast.Attribute(
            value=ast.Name(id="sys", ctx=ast.Load()),
            attr="modules",
            ctx=ast.Load(),
        ),
        slice=None,  # type: ignore
        ctx=ast.Load(),
    )
    visitor.visit(no_slice_node)


def test_scanner_extra_coverage_edge_cases(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Verify other dynamic branches in BoundaryVisitor and scanner."""
    # 1. Directory path in resolve_module_path
    dir_path = temp_project / "src" / "agentic_workflow" / "domain"
    dir_path.mkdir(parents=True, exist_ok=True)
    res_dir = scanner.resolve_module_path(dir_path)
    assert res_dir == "agentic_workflow.domain"

    # 2. Relative import with no module name (e.g. from . import x)
    code_rel = "from . import entities"
    file_rel = temp_project / "src" / "agentic_workflow" / "domain" / "entities" / "rel.py"
    file_rel.parent.mkdir(parents=True, exist_ok=True)
    file_rel.write_text(code_rel, encoding="utf-8")
    assert scanner.scan_file(str(file_rel)) == []

    # 3. Call with non-Name/Attribute func (e.g. call on a call fn()()), and subscript on a call (e.g. fn()['key'])
    code_call = "fn()()\nx = fn()['key']"
    file_call = temp_project / "src" / "agentic_workflow" / "domain" / "call.py"
    file_call.parent.mkdir(parents=True, exist_ok=True)
    file_call.write_text(code_call, encoding="utf-8")
    assert scanner.scan_file(str(file_call)) == []

    # 4. __import__() with no arguments (empty args dynamic import)
    code_import = "x = __import__()"
    file_import = temp_project / "src" / "agentic_workflow" / "domain" / "imp.py"
    file_import.parent.mkdir(parents=True, exist_ok=True)
    file_import.write_text(code_import, encoding="utf-8")
    assert scanner.scan_file(str(file_import)) == []

    # 5. sys.modules dynamic lookup and dynamic import with variable in outer layer (adapters)
    # where they are allowed (covers False branch of current_rank < 3)
    code_sys = "import sys, importlib; k = sys.modules[some_var]; importlib.import_module(some_var)"
    file_sys = temp_project / "src" / "agentic_workflow" / "adapters" / "persistence" / "sys.py"
    file_sys.parent.mkdir(parents=True, exist_ok=True)
    file_sys.write_text(code_sys, encoding="utf-8")
    assert scanner.scan_file(str(file_sys)) == []

    # 6. Function and AnnAssign with non-string annotations (e.g. def f() -> int:, x: int = 10)
    # to cover False branch of isinstance in visit_FunctionDef and visit_AnnAssign
    code_ann = "x: int = 10\ndef f() -> int: return 1"
    file_ann = temp_project / "src" / "agentic_workflow" / "domain" / "ann.py"
    file_ann.parent.mkdir(parents=True, exist_ok=True)
    file_ann.write_text(code_ann, encoding="utf-8")
    assert scanner.scan_file(str(file_ann)) == []


def test_scanner_pragma_no_cover_abuse(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Verify that any use of pragma: no cover outside of if __name__ == '__main__': is flagged."""
    # 1. Illegal use of pragma: no cover on regular line
    illegal_code = "def my_func():  # pragma: no cover\n    pass\n"
    illegal_file = temp_project / "src" / "agentic_workflow" / "domain" / "illegal.py"
    illegal_file.write_text(illegal_code, encoding="utf-8")

    violations = scanner.scan_file(str(illegal_file))
    assert len(violations) == 1
    assert violations[0].category == "pragma_no_cover_abuse"
    assert "Illegal pragma: no cover bypass detected" in violations[0].message

    # 2. Legal use of pragma: no cover on if __name__ == '__main__':
    legal_code = "if __name__ == '__main__':  # pragma: no cover\n    main()\n"
    legal_file = temp_project / "src" / "agentic_workflow" / "domain" / "legal.py"
    legal_file.write_text(legal_code, encoding="utf-8")

    assert scanner.scan_file(str(legal_file)) == []


def test_scanner_domain_whitelist(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Verify that domain imports of non-whitelisted external packages are flagged."""
    # 1. Allowed standard library and own domain imports
    allowed_code = (
        "from __future__ import annotations\n"
        "import typing\n"
        "from dataclasses import dataclass\n"
        "import deal\n"
        "from agentic_workflow.domain.value_objects import RepoMap\n"
        "from . import sibling\n"
    )
    allowed_file = temp_project / "src" / "agentic_workflow" / "domain" / "allowed_deps.py"
    allowed_file.write_text(allowed_code, encoding="utf-8")
    assert scanner.scan_file(str(allowed_file)) == []

    # 2. Forbidden third-party package import (e.g. requests)
    forbidden_code = "import requests\n"
    forbidden_file = temp_project / "src" / "agentic_workflow" / "domain" / "forbidden_deps.py"
    forbidden_file.write_text(forbidden_code, encoding="utf-8")

    violations = scanner.scan_file(str(forbidden_file))
    assert len(violations) == 1
    assert violations[0].category == "external_dependency_violation"
    assert "Illegal external dependency" in violations[0].message
    assert "requests" in violations[0].message

    # 3. Forbidden sub-package of agentic_workflow that is not domain (e.g. adapters)
    forbidden_sub_code = "from agentic_workflow.adapters import persistence\n"
    forbidden_sub_file = temp_project / "src" / "agentic_workflow" / "domain" / "forbidden_sub_deps.py"
    forbidden_sub_file.write_text(forbidden_sub_code, encoding="utf-8")

    violations_sub = scanner.scan_file(str(forbidden_sub_file))
    # It will trigger rank static_import violation!
    assert len(violations_sub) >= 1
    categories = [v.category for v in violations_sub]
    assert "static_import" in categories


def test_scanner_outer_instantiation(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Verify that direct instantiation of outer-layer classes within core layers is flagged."""
    # 1. Illegal direct instantiation in domain using namespace
    illegal_inst_code = "repo = agentic_workflow.adapters.persistence.FileRepository()\n"
    illegal_inst_file = temp_project / "src" / "agentic_workflow" / "domain" / "illegal_inst.py"
    illegal_inst_file.write_text(illegal_inst_code, encoding="utf-8")

    violations = scanner.scan_file(str(illegal_inst_file))
    assert len(violations) >= 1
    inst_violations = [v for v in violations if v.category == "illegal_instantiation"]
    assert len(inst_violations) == 1
    assert "directly instantiating outer layer class" in inst_violations[0].message
    assert "agentic_workflow.adapters.persistence.FileRepository" in inst_violations[0].message

    # 2. Legal instantiation of inner layer classes or standard libraries
    legal_inst_code = "my_vo = agentic_workflow.domain.value_objects.RepoMap()\n"
    legal_inst_file = temp_project / "src" / "agentic_workflow" / "domain" / "legal_inst.py"
    legal_inst_file.write_text(legal_inst_code, encoding="utf-8")
    assert scanner.scan_file(str(legal_inst_file)) == []


def test_scanner_blocked_locator_in_outer_layer(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Verify that importing blocked locator in adapters/frameworks is allowed (rank >= 3)."""
    code = "from agentic_workflow.frameworks.dependency_container import DependencyContainer\n"
    file_path = temp_project / "src" / "agentic_workflow" / "frameworks" / "my_framework.py"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(code, encoding="utf-8")
    assert scanner.scan_file(str(file_path)) == []


def test_scanner_hardened_type_and_pragma(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """Verify type/pragma comments are banned in inner layers / outside main, allowing normal comments."""
    # 1. Ban all pragma comments outside main (all branch permutations)
    pragma_cases = [
        ("x = 10  # pragma\n", True),
        ("x = 10  # pragma: no branch\n", True),
        ("x = 10  # pragma no cover\n", True),
        ("x = 10  # pragmatics of the logic\n", False),
        ("x = 10  # This is fine\n# pragma: no cover\n", True),
    ]
    for idx, (code_pragma, should_violate) in enumerate(pragma_cases):
        file_pragma = temp_project / "src" / "agentic_workflow" / "domain" / f"prag_{idx}.py"
        file_pragma.write_text(code_pragma, encoding="utf-8")
        violations = scanner.scan_file(str(file_pragma))
        if should_violate:
            assert len(violations) == 1, (
                f"Expected exactly 1 violation for pragma case {idx} ({code_pragma!r}), "
                f"but got {len(violations)} violations: {violations}"
            )
            assert violations[0].category == "pragma_no_cover_abuse", (
                f"Expected category 'pragma_no_cover_abuse', but got {violations[0].category!r}"
            )
            assert "All pragma comments are strictly banned" in violations[0].message, (
                f"Expected standard pragma error message, but got: {violations[0].message!r}"
            )
        else:
            assert len(violations) == 0, (
                f"Expected 0 violations for legal pragma case {idx} ({code_pragma!r}), but got violations: {violations}"
            )

    # 2. Ban all type comments in inner layers (all branch permutations)
    type_cases = [
        ("x = 10  # type\n", True),
        ("x = 10  # type: List[int]\n", True),
        ("x = 10  # type List[int]\n", True),
        ("x = 10  # typechecker helper\n", False),
        ("x = 10  # normal comment\n# type: ignore\n", True),
    ]
    for idx, (code_type, should_violate) in enumerate(type_cases):
        file_type = temp_project / "src" / "agentic_workflow" / "domain" / f"tp_{idx}.py"
        file_type.write_text(code_type, encoding="utf-8")
        violations = scanner.scan_file(str(file_type))
        if should_violate:
            assert len(violations) == 1, (
                f"Expected exactly 1 violation for type case {idx} ({code_type!r}), "
                f"but got {len(violations)} violations: {violations}"
            )
            assert violations[0].category == "type_ignore_abuse", (
                f"Expected category 'type_ignore_abuse', but got {violations[0].category!r}"
            )
            assert "Type comments are strictly banned" in violations[0].message, (
                f"Expected standard type error message, but got: {violations[0].message!r}"
            )
        else:
            assert len(violations) == 0, (
                f"Expected 0 violations for legal type case {idx} ({code_type!r}), but got violations: {violations}"
            )

    # 3. Allow normal comments containing 'type' or 'pragma' as part of other words
    code_ok = "# This type of logic is fine\n# We should be pragmatic about design\nx = 10\n"
    file_ok = temp_project / "src" / "agentic_workflow" / "domain" / "ok.py"
    file_ok.write_text(code_ok, encoding="utf-8")
    violations_ok = scanner.scan_file(str(file_ok))
    assert violations_ok == [], f"Expected 0 violations for ok.py, but got: {violations_ok}"

    # 4. Verify frameworks layer file with comments doesn't check type comments
    code_fw = "x = 10  # type: List[int] in frameworks is allowed\n# Just a normal comment in frameworks\n"
    file_fw = temp_project / "src" / "agentic_workflow" / "frameworks" / "fw.py"
    file_fw.parent.mkdir(parents=True, exist_ok=True)
    file_fw.write_text(code_fw, encoding="utf-8")
    violations_fw = scanner.scan_file(str(file_fw))
    assert violations_fw == [], f"Expected 0 violations for fw.py, but got: {violations_fw}"


def test_scanner_fallback_on_tokenization_failure(
    scanner: CleanArchitectureBoundaryScanner, temp_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify scanner falls back to regex line-by-line check if tokenize fails."""
    import tokenize
    from typing import Any

    def mock_generate_tokens(*args: Any, **kwargs: Any) -> Any:
        raise tokenize.TokenError("Mocked tokenization failure")

    monkeypatch.setattr(tokenize, "generate_tokens", mock_generate_tokens)

    # 1. Ban all pragma comments outside main
    # Line 1 covers pragma inside main (covers 184->198 False branch)
    # Line 2 covers line without '#' (covers 178->177 False branch)
    # Line 3 covers illegal pragma outside main (triggers violation)
    code_pragma = "if __name__ == '__main__':  # pragma: no cover\n    pass\nx = 10  # pragma\n"
    file_pragma = temp_project / "src" / "agentic_workflow" / "domain" / "fallback_prag.py"
    file_pragma.write_text(code_pragma, encoding="utf-8")
    violations = scanner.scan_file(str(file_pragma))
    assert len(violations) == 1, f"Expected 1 fallback violation, but got: {violations}"
    assert violations[0].category == "pragma_no_cover_abuse"

    # 2. Ban all type comments in inner layers
    code_type = "x = 10  # type: ignore\n"
    file_type = temp_project / "src" / "agentic_workflow" / "domain" / "fallback_tp.py"
    file_type.write_text(code_type, encoding="utf-8")
    violations = scanner.scan_file(str(file_type))
    assert len(violations) == 1, f"Expected 1 fallback violation, but got: {violations}"
    assert violations[0].category == "type_ignore_abuse"


# ── Test Suite: ADR-STR-027 v2 — Framework Layer pragma full ban ──────────────


def test_framework_pragma_no_branch_is_banned(scanner: CleanArchitectureBoundaryScanner, temp_project: Path) -> None:
    """ADR-STR-027 v2: # pragma: no branch must be banned in frameworks layer.

    This test EXPOSES the existing violations in:
      - frameworks/graph/iteration_nodes.py
      - frameworks/graph/master_pipeline_nodes.py
      - frameworks/graph/micro_validation_nodes.py
    """
    code = "from x import y\ndef fn(state):\n    return state  # pragma: no branch\n"
    fw_file = temp_project / "src" / "agentic_workflow" / "frameworks" / "fw_pragma.py"
    fw_file.write_text(code, encoding="utf-8")
    violations = scanner.scan_file(str(fw_file))
    pragma_violations = [v for v in violations if v.category == "pragma_no_cover_abuse"]
    assert len(pragma_violations) == 1, (
        f"Expected exactly 1 pragma_no_cover_abuse in frameworks layer, "
        f"but got {len(pragma_violations)}: {pragma_violations}"
    )
    assert "pragma" in pragma_violations[0].message.lower()


def test_framework_pragma_no_cover_outside_main_is_banned(
    scanner: CleanArchitectureBoundaryScanner, temp_project: Path
) -> None:
    """ADR-STR-027 v2: # pragma: no cover outside entry point must be banned in frameworks layer."""
    code = "x = 10  # pragma: no cover\n"
    fw_file = temp_project / "src" / "agentic_workflow" / "frameworks" / "fw_no_cover.py"
    fw_file.write_text(code, encoding="utf-8")
    violations = scanner.scan_file(str(fw_file))
    pragma_violations = [v for v in violations if v.category == "pragma_no_cover_abuse"]
    assert len(pragma_violations) == 1, (
        f"Expected 1 pragma_no_cover_abuse in frameworks, but got {len(pragma_violations)}: {pragma_violations}"
    )


def test_framework_pragma_on_main_line_is_still_allowed(
    scanner: CleanArchitectureBoundaryScanner, temp_project: Path
) -> None:
    """ADR-STR-027 v2: # pragma: no cover on 'if __name__ == __main__' line is the ONLY legal exception."""
    code = "def run() -> None:\n    pass\n\nif __name__ == '__main__':  # pragma: no cover\n    run()\n"
    fw_file = temp_project / "src" / "agentic_workflow" / "frameworks" / "fw_entry.py"
    fw_file.write_text(code, encoding="utf-8")
    violations = scanner.scan_file(str(fw_file))
    pragma_violations = [v for v in violations if v.category == "pragma_no_cover_abuse"]
    assert pragma_violations == [], f"Expected 0 pragma violations for entry-point pragma, but got: {pragma_violations}"


def test_framework_scan_real_iteration_nodes_clean() -> None:
    """ADR-STR-027 v2 regression: iteration_nodes.py must have zero pragma violations.

    Verifies that the previously exposed violations have been remediated.
    """
    import pathlib

    project_root = pathlib.Path(__file__).resolve().parents[2]
    scanner = CleanArchitectureBoundaryScanner(project_root=str(project_root))

    target = project_root / "src" / "agentic_workflow" / "frameworks" / "graph" / "iteration_nodes.py"
    violations = scanner.scan_file(str(target))
    pragma_violations = [v for v in violations if v.category == "pragma_no_cover_abuse"]

    assert pragma_violations == [], (
        f"iteration_nodes.py must have 0 pragma violations after remediation, but found: {pragma_violations}"
    )


def test_framework_scan_real_master_pipeline_nodes_clean() -> None:
    """ADR-STR-027 v2 regression: master_pipeline_nodes.py must have zero pragma violations."""
    import pathlib

    project_root = pathlib.Path(__file__).resolve().parents[2]
    scanner = CleanArchitectureBoundaryScanner(project_root=str(project_root))

    target = project_root / "src" / "agentic_workflow" / "frameworks" / "graph" / "master_pipeline_nodes.py"
    violations = scanner.scan_file(str(target))
    pragma_violations = [v for v in violations if v.category == "pragma_no_cover_abuse"]

    assert pragma_violations == [], (
        f"master_pipeline_nodes.py must have 0 pragma violations after remediation, but found: {pragma_violations}"
    )


def test_framework_scan_real_micro_validation_nodes_clean() -> None:
    """ADR-STR-027 v2 regression: micro_validation_nodes.py must have zero pragma violations."""
    import pathlib

    project_root = pathlib.Path(__file__).resolve().parents[2]
    scanner = CleanArchitectureBoundaryScanner(project_root=str(project_root))

    target = project_root / "src" / "agentic_workflow" / "frameworks" / "graph" / "micro_validation_nodes.py"
    violations = scanner.scan_file(str(target))
    pragma_violations = [v for v in violations if v.category == "pragma_no_cover_abuse"]

    assert pragma_violations == [], (
        f"micro_validation_nodes.py must have 0 pragma violations after remediation, but found: {pragma_violations}"
    )


def test_framework_scan_main_entry_point_no_violation() -> None:
    """ADR-STR-027 v2: main.py entry point pragma must NOT produce violations."""
    import pathlib

    project_root = pathlib.Path(__file__).resolve().parents[2]
    scanner = CleanArchitectureBoundaryScanner(project_root=str(project_root))

    target = project_root / "src" / "agentic_workflow" / "frameworks" / "main.py"
    violations = scanner.scan_file(str(target))
    pragma_violations = [v for v in violations if v.category == "pragma_no_cover_abuse"]

    assert pragma_violations == [], (
        f"Expected 0 pragma violations in main.py (entry point exception), but got: {pragma_violations}"
    )
