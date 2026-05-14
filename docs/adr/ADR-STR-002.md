# ADR-STR-002: Clean Architecture for LangGraph Migration

**Status**: Proposed
**Date**: 2026-05-14
**Category**: STR (Architecture)

## Context

The existing system is document-driven (33 Markdown workflow skills orchestrated by AGENTS.md, read by AI agents). The migration to LangGraph (Python) introduces executable code that must be structured to:
- Keep domain logic framework-independent (testable without LangGraph)
- Allow MCP server swapping without domain changes (GitKraken, Sequential Thinking)
- Allow LLM provider swapping without domain changes
- Enforce that all 5 algorithms (ALG-001..005) remain deterministic

## Decision

Adopt Clean Architecture with 4 layers:

1. **Domain**: Entities (CLS-001..014), algorithms (ALG-001..005), events (EVT-001..007), contracts (INV-001..019). Zero external dependencies.
2. **Application**: Use cases (UC-001..011), port interfaces (Repository, Gateway, Presenter, EventBus). Depends only on Domain.
3. **Adapters**: LangGraph nodes, MCP adapters, file repositories, LLM adapters, HITL console. Implements port interfaces.
4. **Frameworks**: LangGraph StateGraph construction, configuration, dependency injection wiring.

## Consequences

- (+) Domain logic is 100% testable without any framework
- (+) MCP servers are swappable via port interfaces
- (+) LLM providers are swappable via port interfaces
- (+) LangGraph can be replaced without touching domain/application
- (+) Deterministic algorithms are isolated from LLM-dependent code
- (-) More files and indirection than a flat structure
- (-) State mapping between LangGraph TypedDict and domain objects

## FR/NFR Justification

- FR-001 (Top-level orchestrator structure)
- FR-002 (Phase/Stage separation)
- FR-003 (Skill independence)
- NFR-002 (Submodule read-only: encapsulated via ports)

## Related Artifacts

- `docs/clean-architecture.md` — Full layer definitions and package structure
- `docs/ooad-design.md` — Class/sequence/component diagrams
- `docs/formal-verification-spec.md` — icontract mapping for all 19 INVs
