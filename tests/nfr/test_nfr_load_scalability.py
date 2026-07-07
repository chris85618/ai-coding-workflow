"""NFR-014: Load and scalability tests for domain aggregates (left-shifted).

Verifies that bulk operations behave linearly and stay correct at volume,
so scaling regressions surface before Stage 8 instead of in production.
"""

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.enums import DebtSource, Severity
from agentic_workflow.domain.services.assumption_registry import AssumptionRegistry
from agentic_workflow.domain.services.debt_accumulator import DebtAccumulator

BULK_SIZE = 5_000


class TestLoadScalability:
    """Covers correctness of bulk domain operations at volume."""

    def test_bulk_debt_absorption_preserves_ordering(self) -> None:
        """TC-NFR-004: 5k absorbed debts keep contiguous 1-based numbering."""
        bulk = BULK_SIZE
        descriptions = [f"failure {i}" for i in range(bulk)]
        items = DebtAccumulator.absorb(DebtSource.VALIDATION, Severity.MEDIUM, descriptions, start_index=1)
        assert items[0].debt_id == "DEBT-001"
        assert items[-1].debt_id == f"DEBT-{bulk:03d}"
        assert len({item.debt_id for item in items}) == bulk

    def test_bulk_assumption_registration_deduplicates(self) -> None:
        """TC-NFR-005: 5k lesson conversions register without id collisions."""
        bulk = BULK_SIZE
        registry = AssumptionRegistry()
        for assumption in AssumptionRegistry.from_lessons([f"lesson {i}" for i in range(bulk)], start_index=1):
            registry.register(assumption)
        assert registry.count() == bulk

    def test_bulk_stage_findings_on_pipeline_aggregate(self) -> None:
        """TC-NFR-006: 5k findings funnel through the aggregate root intact."""
        bulk = BULK_SIZE
        pipeline = Pipeline(pipeline_id="load-test")
        pipeline.update_stage_findings([f"YAGNI: nit {i}" for i in range(bulk)])
        assert len(pipeline.current_stage.findings) == bulk
