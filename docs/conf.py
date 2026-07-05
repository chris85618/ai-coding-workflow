"""Sphinx configuration.

Single source of truth for project metadata is pyproject.toml:
[project] supplies name/version, [tool.sphinx] supplies site texts.
Feature parity with the retired MkDocs/pdoc toolchain:
- Markdown sources        -> myst_parser
- API reference (pdoc)    -> sphinx.ext.autodoc + autosummary + napoleon + viewcode
- readthedocs theme       -> sphinx_rtd_theme
- macros version inject   -> myst_substitutions built from pyproject metadata
- Contract rendering      -> sphinx_icontract
"""

import pathlib
import sys
import tomllib

_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(_root / "src"))

with open(_root / "pyproject.toml", "rb") as _f:
    _pyproject = tomllib.load(_f)

_project_meta = _pyproject.get("project", {})
_sphinx_meta = _pyproject.get("tool", {}).get("sphinx", {})

project = _project_meta.get("name", "unknown")
release = _project_meta.get("version", "0.0.0")
version = release
author = "Agentic Workflow Team"
copyright = "2026, Agentic Workflow Team"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_icontract",
    "sphinxcontrib.mermaid",
]

myst_enable_extensions = [
    "colon_fence",
    "substitution",
]
# Render ```mermaid fences through sphinxcontrib-mermaid instead of Pygments.
myst_fence_as_directive = ["mermaid"]
myst_substitutions = {
    "version": release,
    "project_name": project,
    "site_name": _sphinx_meta.get("site_name", project),
    "site_description": _sphinx_meta.get("site_description", ""),
}
# Standalone documents are intentional; MyST xref warnings on plain markdown are noise.
suppress_warnings = ["myst.xref_missing", "myst.header", "toc.not_included"]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

html_theme = "sphinx_rtd_theme"

napoleon_google_docstring = True
napoleon_numpy_docstring = False
autodoc_member_order = "bysource"
autosummary_generate = True
