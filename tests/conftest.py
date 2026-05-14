"""Pytest-BDD conftest — shared fixtures for BDD feature files.

Provides fixtures for domain objects, test doubles, and common setup.
Step definitions import from here for shared test infrastructure.

NOTE: Step definition implementations will be added in Stage 8 (TDD).
This file provides the fixture skeleton only.
"""

import pytest


@pytest.fixture
def docs_path(tmp_path):
    """Provide a temporary docs/ directory for test isolation."""
    docs = tmp_path / "docs"
    docs.mkdir()
    return docs


@pytest.fixture
def empty_checkpoint():
    """Provide a None checkpoint simulating fresh start."""
    return None
