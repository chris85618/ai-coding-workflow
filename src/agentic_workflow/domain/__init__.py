"""Domain Layer — Pure business logic.

Zero external dependencies. All classes use icontract decorators.
All algorithms are deterministic (no LLM, no I/O).

Subpackages:
    models/      : Aggregate Roots, Entities, Value Objects
    services/    : Domain Services
    algorithms/  : Pure deterministic algorithms
    events/      : Immutable domain event dataclasses
    contracts/   : icontract predicate functions
"""
