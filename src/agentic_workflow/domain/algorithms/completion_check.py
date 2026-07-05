"""Completion Check Algorithm — Final release readiness.

Traceable to: Release protocols
OO Design: CompletionCheck class encapsulates all logic (ALG-010 OO mandate).
Ensures 100% test coverage and zero High/Critical risks before ship.
"""

from typing import Any

import deal


class CompletionCheck:
    """Verifies that all requirements are met before a Phase 9 ship.

    Mandates 100% test coverage (statement + branch) and zero unresolved risks.
    """

    COVERAGE_THRESHOLD: float = 1.00

    @classmethod
    @deal.pre(lambda _: 0.0 <= _.test_coverage <= 1.0, message="Coverage is a ratio in [0, 1]")
    @deal.pre(lambda _: _.open_risks >= 0 and _.pending_debts >= 0, message="Counters cannot be negative")
    @deal.ensure(
        lambda _: _.result["ready"] == (len(_.result["failures"]) == 0),
        message="Readiness must equal the absence of failures",
    )
    def verify_readiness(cls, test_coverage: float, open_risks: int, pending_debts: int = 0) -> dict[str, Any]:
        """Runs final checks before allowing Phase 9 ship.

        Args:
            test_coverage: Ratio of test coverage [0.0, 1.0].
            open_risks: Count of unresolved Critical/High risks.
            pending_debts: Count of pending P0/P1 technical debts.

        Returns:
            Dict with 'ready' (bool) and 'failures' (List[str]).
        """
        failures: list[str] = []

        # Check coverage
        if test_coverage < cls.COVERAGE_THRESHOLD:
            failures.append(f"Test coverage ({test_coverage * 100:.2f}%) below 100%.")

        # Check risks
        if open_risks > 0:
            failures.append(f"Unresolved risks count: {open_risks}.")

        # Check critical debts (P0/P1)
        if pending_debts > 0:
            failures.append(f"Pending P0/P1 technical debts: {pending_debts}.")

        return {"ready": len(failures) == 0, "failures": failures}
