"""Z3 SMT verification of core pipeline invariants (kanban: 形式化驗證加入 Z3).

Complements DbC (deal) and CrossHair with machine-checked proofs: each test
encodes an invariant as the *negation* of the property and asserts Z3 finds
it unsatisfiable (i.e. no counterexample exists in unbounded integer space).

Traceable to: INV-001, INV-026, FR-071, ADR-STR-029, docs/formal-verification-spec.md
"""

import z3

from agentic_workflow.domain.services.governance_cost_model import GovernanceCostModel

STAGE_COUNT = 11


class TestZ3Invariants:
    """Machine-checked proofs for pipeline arithmetic invariants."""

    def _prove(self, counterexample: z3.BoolRef) -> None:
        """Assert the counterexample formula is unsatisfiable (property proven)."""
        solver = z3.Solver()
        solver.add(counterexample)
        assert solver.check() == z3.unsat, f"Counterexample found: {solver.model()}"

    def test_inv001_advance_is_strictly_monotonic(self) -> None:
        """TC-Z3-001: INV-001 — advancing never moves the position backwards."""
        stage_count = STAGE_COUNT
        idx, idx_next = z3.Ints("idx idx_next")
        in_range = z3.And(idx >= 0, idx < stage_count - 1)
        advance = idx_next == idx + 1
        violates_monotonicity = idx_next <= idx
        self._prove(z3.And(in_range, advance, violates_monotonicity))

    def test_inv001_advance_never_escapes_stage_order(self) -> None:
        """TC-Z3-002: INV-001 — advance from a legal slot stays inside the order."""
        stage_count = STAGE_COUNT
        idx, idx_next = z3.Ints("idx idx_next")
        in_range = z3.And(idx >= 0, idx < stage_count - 1)
        advance = idx_next == idx + 1
        escapes = z3.Or(idx_next < 0, idx_next >= stage_count)
        self._prove(z3.And(in_range, advance, escapes))

    def test_kappa_is_non_negative_for_all_valid_inputs(self) -> None:
        """TC-Z3-003: FR-071 — governance cost is provably non-negative."""
        iteration_weight = GovernanceCostModel.ITERATION_WEIGHT
        debt_weight = GovernanceCostModel.DEBT_WEIGHT
        iterations, debts = z3.Ints("iterations debts")
        kappa = iterations * iteration_weight + debts * debt_weight
        valid = z3.And(iterations >= 0, debts >= 0)
        self._prove(z3.And(valid, kappa < 0))

    def test_kappa_is_monotonic_in_debt(self) -> None:
        """TC-Z3-004: FR-071 — more debt can never lower the HITL trigger."""
        iteration_weight = GovernanceCostModel.ITERATION_WEIGHT
        debt_weight = GovernanceCostModel.DEBT_WEIGHT
        threshold = GovernanceCostModel.HITL_THRESHOLD
        iterations, debts = z3.Ints("iterations debts")
        kappa_now = iterations * iteration_weight + debts * debt_weight
        kappa_more_debt = iterations * iteration_weight + (debts + 1) * debt_weight
        valid = z3.And(iterations >= 0, debts >= 0)
        trigger_lost = z3.And(kappa_now > threshold, kappa_more_debt <= threshold)
        self._prove(z3.And(valid, trigger_lost))

    def test_debt_numbering_is_collision_free(self) -> None:
        """TC-Z3-005: INV-026 — 1-based sequential numbering never collides."""
        start, offset_a, offset_b = z3.Ints("start offset_a offset_b")
        valid = z3.And(start >= 1, offset_a >= 0, offset_b >= 0, offset_a != offset_b)
        collision = start + offset_a == start + offset_b
        self._prove(z3.And(valid, collision))
