"""Base classes for the Specification Pattern."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Specification[T](ABC):
    """Abstract base class for specifications."""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if the candidate satisfies the specification."""
        pass

    def __and__(self, other: Specification[T]) -> Specification[T]:
        """Combine with another specification using AND."""
        return AndSpecification(self, other)

    def __or__(self, other: Specification[T]) -> Specification[T]:
        """Combine with another specification using OR."""
        return OrSpecification(self, other)

    def __invert__(self) -> Specification[T]:
        """Negate the specification."""
        return NotSpecification(self)


class AndSpecification[T](Specification[T]):
    """Composite specification for AND logic."""

    def __init__(self, left: Specification[T], right: Specification[T]):
        """Initialize with two sub-specifications."""
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if both sub-specifications are satisfied."""
        return self._left.is_satisfied_by(candidate) and self._right.is_satisfied_by(candidate)


class OrSpecification[T](Specification[T]):
    """Composite specification for OR logic."""

    def __init__(self, left: Specification[T], right: Specification[T]):
        """Initialize with two sub-specifications."""
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if either sub-specification is satisfied."""
        return self._left.is_satisfied_by(candidate) or self._right.is_satisfied_by(candidate)


class NotSpecification[T](Specification[T]):
    """Composite specification for NOT logic."""

    def __init__(self, spec: Specification[T]):
        """Initialize with a specification to negate."""
        self._spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if the sub-specification is NOT satisfied."""
        return not self._spec.is_satisfied_by(candidate)
