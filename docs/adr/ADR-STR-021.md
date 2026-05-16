# ADR-STR-021: Clean Architecture & DDD Deep Alignment

## Status
proposed

## Context
The project has undergone an initial DDD refactoring, but several architectural "smells" remain:
1. **Tight Coupling**: LangGraph nodes directly instantiate Use Cases and Adapters.
2. **Leakage**: Framework configurations (os.environ) and technical adapters (LLM) are scattered.
3. **Aggregate Weakness**: The `Pipeline` aggregate root is bypassable; nodes still think in terms of "state dictionaries".
4. **Naming Mismatch**: Coding terms don't fully align with the Ubiquitous Language defined in `AGENTS.md`.

## Decision

### 1. Dependency Inversion Principle (DIP) Enforcement
- **Application Layer**: Define all external dependencies as **Interfaces (Ports)** in `application/ports/`.
- **Infrastructure Layer**: Place all concrete implementations in `adapters/`.
- **Composition Root**: Implement a `src/agentic_workflow/main.py` (or registry) that wired up the graph with injected use cases.

### 2. Aggregate Root (AR) Hardening
- **Single Entry Point**: `Pipeline` aggregate root will encapsulate all state transitions.
- **New Methods**:
    - `advance_stage()`: Orchestrates gate recording and position movement.
    - `fail_validation(reason: str)`: Transitions current stage to FAILED and records findings.
- **Immutability**: Findings and IDs will be handled as **Value Objects**.

### 3. Specification Pattern for Governance
- Governance checks (e.g., "zero warnings", "100% coverage") will be implemented as `Specification` classes.
- Complex calculations (e.g., blast radius) will be labeled as `DomainServices`.

### 4. LLM Isolation
- `IAgentReasoner` port will be defined in the Application layer.
- `AnthropicAdapter` and `OpenAIAdapter` will implement this port in the Infrastructure layer.

### 5. Ubiquitous Language Sync
- Variables like `alpha_review`, `beta_review`, `hitl_decision` will replace generic names.
- Ensure 100% alignment with `AGENTS.md`.

## Consequences
- **Positive**: High testability (100% mockable), strict boundary enforcement, easier model swapping.
- **Negative**: Increased boilerplate (Interfaces + DTOs), slightly higher cognitive load for new developers.
