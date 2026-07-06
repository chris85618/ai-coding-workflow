"""AssumptionRegistry Domain Service — Ouroboros constraint closure.

Traceable to: FR-070, ADR-STR-029, FEA-030, ALG-019
Pipeline v2: retro lessons become rigid L2 output-affecting assumptions that
are injected into the next session START node, so every session hardens the
physical defenses of the next one.
"""

from __future__ import annotations

import deal

from agentic_workflow.domain.value_objects.assumption import Assumption


class AssumptionRegistry:
    """ALG-019: Holds output-affecting assumptions for session-start injection."""

    def __init__(self) -> None:
        """Initialize an empty registry keyed by assumption id."""
        self._items: dict[str, Assumption] = {}

    @deal.has()
    def register(self, assumption: Assumption) -> None:
        """Register an assumption; the newest statement for an id wins (idempotent)."""
        self._items[assumption.assumption_id] = assumption

    @deal.post(lambda result: all(bool(statement) for statement in result))
    def active_statements(self) -> list[str]:
        """Return the statements of all active assumptions for injection."""
        return [item.statement for item in self._items.values() if item.active]

    @deal.post(lambda result: result >= 0)
    def count(self) -> int:
        """Return the number of registered assumptions."""
        return len(self._items)

    @classmethod
    @deal.pre(lambda _: _.start_index >= 1, message="Assumption numbering is 1-based")
    @deal.post(lambda result: all(item.assumption_id.startswith("ASM-") for item in result))
    def from_lessons(cls, lessons: list[str], start_index: int = 1) -> list[Assumption]:
        """Convert retro lessons into sequentially numbered assumptions.

        Args:
            lessons: Lesson statements extracted during Phase 10 retro.
            start_index: 1-based index for the first generated ASM id.

        Returns:
            One Assumption per non-empty lesson, numbered from start_index.
        """
        non_empty = [text for text in lessons if text]
        return [
            Assumption(
                assumption_id=f"ASM-{start_index + offset:03d}",
                statement=text,
                source_id="phase10-retro",
            )
            for offset, text in enumerate(non_empty)
        ]
