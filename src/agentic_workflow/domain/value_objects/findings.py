"""Value Object for stage findings."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

import deal


@dataclass(frozen=True)
class Findings:
    """Immutable collection of findings from Agent alpha critique.

    Attributes:
        items: List of finding strings.
    """

    items: list[str] = field(default_factory=list)

    @deal.ensure(
        lambda _: len(_.result.items) == len(_.self.items) + 1 and _.result.items[-1] == _.finding,
        message="add() must append exactly the given finding to a new VO",
    )
    def add(self, finding: str) -> Findings:
        """Create a new Findings object with the additional finding.

        Args:
            finding: The finding to add.

        Returns:
            A new Findings object.
        """
        return Findings(items=self.items + [finding])

    def __len__(self) -> int:
        """Return the number of findings."""
        return len(self.items)

    def __iter__(self) -> Iterator[str]:
        """Return an iterator over the findings."""
        return iter(self.items)
