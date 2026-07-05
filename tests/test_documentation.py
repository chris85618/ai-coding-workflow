"""Tests for the Sphinx documentation ecosystem.

The documentation toolchain is Sphinx-based: MkDocs and pdoc are fully retired.
Feature mapping enforced here:
- Markdown sources        -> myst-parser
- API reference (pdoc)    -> sphinx.ext.autodoc + sphinx.ext.napoleon + sphinx.ext.viewcode
- readthedocs theme       -> sphinx_rtd_theme
- pyproject metadata SSOT -> conf.py reads [project] from pyproject.toml
- Contract rendering      -> sphinx_icontract

Traceable to: TC-DOC-001 ~ TC-DOC-005, FR-QUALITY-001
"""

import pathlib
import runpy
import subprocess
import sys
import tomllib

_root = pathlib.Path(__file__).parent.parent.resolve()
_docs_dir = _root / "docs"
_conf_path = _docs_dir / "conf.py"
_index_path = _docs_dir / "index.md"
_pyproject_path = _root / "pyproject.toml"

_required_extensions = (
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_icontract",
)

_required_dev_dependencies = (
    "sphinx",
    "myst-parser",
    "sphinx-rtd-theme",
    "sphinx-icontract",
)

_legacy_artifacts = (
    "mkdocs.yml",
    "macros.py",
    "docs/api",
)

_legacy_dependency_tokens = ("mkdocs", "pdoc")


def _load_pyproject() -> dict[str, object]:
    """Load the parsed pyproject.toml document."""
    with open(_pyproject_path, "rb") as f:
        return tomllib.load(f)


def _load_conf_namespace() -> dict[str, object]:
    """Execute docs/conf.py and return its resulting namespace."""
    return runpy.run_path(str(_conf_path))


def test_sphinx_conf_declares_required_extensions() -> None:
    """TC-DOC-001: docs/conf.py exists and declares every required Sphinx extension."""
    assert _conf_path.exists(), f"Missing Sphinx configuration: {_conf_path}"
    namespace = _load_conf_namespace()
    extensions = namespace.get("extensions")
    assert isinstance(extensions, list), "conf.py must define an 'extensions' list"
    missing = [ext for ext in _required_extensions if ext not in extensions]
    assert not missing, f"conf.py is missing required Sphinx extensions: {missing}"


def test_sphinx_conf_reads_metadata_from_pyproject() -> None:
    """TC-DOC-002: conf.py project name and version come from pyproject.toml [project] (SSOT)."""
    assert _conf_path.exists(), f"Missing Sphinx configuration: {_conf_path}"
    namespace = _load_conf_namespace()
    pyproject = _load_pyproject()
    project_table = pyproject.get("project")
    assert isinstance(project_table, dict)
    assert namespace.get("project") == project_table.get("name"), (
        "conf.py 'project' must equal pyproject.toml [project].name"
    )
    assert namespace.get("release") == project_table.get("version"), (
        "conf.py 'release' must equal pyproject.toml [project].version"
    )


def test_legacy_doc_toolchain_removed() -> None:
    """TC-DOC-003: MkDocs and pdoc artifacts and dependencies are fully retired."""
    leftovers = [artifact for artifact in _legacy_artifacts if (_root / artifact).exists()]
    assert not leftovers, f"Legacy documentation artifacts must be removed: {leftovers}"

    pyproject = _load_pyproject()
    project_table = pyproject.get("project")
    assert isinstance(project_table, dict)
    optional = project_table.get("optional-dependencies")
    assert isinstance(optional, dict)
    dev_dependencies = optional.get("dev")
    assert isinstance(dev_dependencies, list)

    normalized = [str(dep).lower() for dep in dev_dependencies]
    legacy_hits = [dep for dep in normalized if any(token in dep for token in _legacy_dependency_tokens)]
    assert not legacy_hits, f"Legacy documentation dependencies must be removed: {legacy_hits}"

    for required in _required_dev_dependencies:
        prefix = f"{required}>="
        matches = [dep for dep in normalized if dep.startswith((prefix, f"{required}=="))]
        assert matches, f"pyproject dev dependencies must pin '{required}'"


def test_docs_index_defines_toctree() -> None:
    """TC-DOC-004: docs/index.md exists and defines a MyST toctree as the navigation root."""
    assert _index_path.exists(), f"Missing documentation root: {_index_path}"
    content = _index_path.read_text(encoding="utf-8")
    assert "{toctree}" in content, "docs/index.md must define a MyST {toctree} directive"


def test_sphinx_build_succeeds(tmp_path: pathlib.Path) -> None:
    """TC-DOC-005: a full Sphinx HTML build of docs/ completes without errors."""
    output_dir = tmp_path / "html"
    cmd = [
        sys.executable,
        "-m",
        "sphinx",
        "-b",
        "html",
        "-q",
        str(_docs_dir),
        str(output_dir),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=False, cwd=_root)
    assert result.returncode == 0, (
        f"Sphinx build failed with exit code {result.returncode}.\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
    )
    assert (output_dir / "index.html").exists(), "Sphinx build must produce index.html"
