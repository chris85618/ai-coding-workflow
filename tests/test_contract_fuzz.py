"""Contract-driven fuzz suite over deterministic domain algorithms.

deal.cases synthesizes inputs from type hints with hypothesis, filters them
through the deal preconditions, and enforces every postcondition/raises
contract on each generated call. Any contract violation fails the test.

Targets are restricted to pure, deterministic callables whose parameter types
hypothesis can synthesize (no Any-typed aggregates, no injected callbacks).

Traceable to: TC-FUZZ-001 ~ TC-FUZZ-010, ADR-STR-028, docs/formal-verification-spec.md §1
"""

import typing
from collections.abc import Callable

import deal
import hypothesis
import pytest

from agentic_workflow.domain.algorithms.blast_radius import BlastRadiusClassifier
from agentic_workflow.domain.algorithms.context_budget import ContextBudgetAllocator
from agentic_workflow.domain.algorithms.iter_loop import IterationLoop
from agentic_workflow.domain.algorithms.micro_validation import MicroValidation
from agentic_workflow.domain.algorithms.risk_manager import RiskManager
from agentic_workflow.domain.algorithms.tech_debt_manager import TechDebtManager
from agentic_workflow.domain.algorithms.traceability_validator import (
    TraceabilityValidator,
)

_fuzz_count = 30

_fuzz_settings = hypothesis.settings(
    deadline=None,
    suppress_health_check=[hypothesis.HealthCheck.filter_too_much, hypothesis.HealthCheck.too_slow],
)


def _classmethod_target(owner: type, name: str) -> Callable[..., object]:
    """Unwrap a contracted classmethod to its raw function for deal.cases."""
    return typing.cast("Callable[..., object]", owner.__dict__[name].__func__)


_FUZZ_TARGETS: list[tuple[str, type, str]] = [
    ("TC-FUZZ-001", BlastRadiusClassifier, "classify"),
    ("TC-FUZZ-002", ContextBudgetAllocator, "estimate_tokens"),
    ("TC-FUZZ-003", RiskManager, "calculate_risk_score"),
    ("TC-FUZZ-004", RiskManager, "evaluate_treatment"),
    ("TC-FUZZ-005", TechDebtManager, "classify_quadrant"),
    ("TC-FUZZ-006", TechDebtManager, "assign_priority"),
    ("TC-FUZZ-007", IterationLoop, "route_hitl_gate"),
    ("TC-FUZZ-008", MicroValidation, "validate_format"),
    ("TC-FUZZ-009", MicroValidation, "validate_structure"),
    ("TC-FUZZ-010", TraceabilityValidator, "validate_id_format"),
]


_fuzz_targets = _FUZZ_TARGETS


@pytest.mark.parametrize(
    ("tc_id", "owner", "method"),
    _fuzz_targets,
    ids=[f"{tc_id}-{owner.__name__}.{method}" for tc_id, owner, method in _fuzz_targets],
)
def test_contract_fuzz(tc_id: str, owner: type, method: str) -> None:
    """Fuzz a contracted domain classmethod through deal.cases."""
    fuzz = deal.cases(
        _classmethod_target(owner, method),
        kwargs={"cls": owner},
        count=_fuzz_count,
        settings=_fuzz_settings,
    )
    fuzz()


def test_contract_fuzz_generate_next_id() -> None:
    """TC-FUZZ-011: generate_next_id never collides with existing IDs (INV-006)."""
    fuzz = deal.cases(
        _classmethod_target(TraceabilityValidator, "generate_next_id"),
        kwargs={"cls": TraceabilityValidator},
        count=_fuzz_count,
        settings=_fuzz_settings,
    )
    fuzz()
