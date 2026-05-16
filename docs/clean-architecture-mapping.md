# Clean Architecture Layer Mapping

This document categorizes the current files in the `ai-coding-workflow` project into Clean Architecture layers and explains the dependency relationships.

## 🏛️ Layer Overview

| Layer | Directory | Role | Responsibilities |
|-------|-----------|------|------------------|
| **Entities (Domain)** | `src/agentic_workflow/domain/` | Core Business Rules | Domain Models, Value Objects, Aggregates, Domain Services. |
| **Use Cases (Application)** | `src/agentic_workflow/application/` | Application Business Rules | Orchestrating domain objects, defining interfaces (Ports). |
| **Interface Adapters** | `src/agentic_workflow/adapters/` | Technical Implementation | Implementing Repositories, Gateways (LLM, MCP, Persistence). |
| **Frameworks & Drivers** | `src/agentic_workflow/frameworks/` | Infrastructure / Tools | External frameworks like LangGraph, global config. |

## 📂 Detailed Mapping

### 1. Entities Layer (Domain)
- **Aggregates**: `domain/aggregates/pipeline.py` (Aggregate Root)
- **Entities**: `domain/entities/stage.py`, `domain/entities/traceable_id.py`
- **Enums**: `domain/enums/*.py` (GateDecision, PipelineStatus, etc.)
- **Algorithms**: `domain/algorithms/*.py` (e.g., `blast_radius.py`, `sonarcloud_gate.py`)
    - *Note*: These are currently "pure" algorithms but Task 5 aims to convert them to **Specifications** or **Domain Services**.

### 2. Use Cases Layer (Application)
- **Use Cases**: `application/use_cases/advance_pipeline.py`, `start_pipeline.py`
- **Ports (Interfaces)**: `application/ports/`
    - `repositories/checkpoint_repository.py`
    - `gateways/llm_gateway.py`, `quality_gateway.py`

### 3. Interface Adapters Layer
- **Persistence**: `adapters/persistence/file_repository.py` (Writes to `docs/`)
- **Gateways**: `adapters/llm/llm_adapter.py`, `adapters/mcp/mcp_adapter.py`
- **Integration**: `adapters/langgraph/nodes.py` (LangGraph nodes calling Use Cases)

### 4. Frameworks & Drivers
- **Graph Engine**: `frameworks/graph/`
- **Configuration**: `frameworks/config.py` (Centralized environment access)

## 🔗 Dependency Relationships

### Standard Clean Architecture Rule
**Dependencies point inwards.**
`Adapters` → `Use Cases` → `Entities`.

### Current Status & Task 2 Alignment
- **Use Cases** depend only on **Entities** and **Ports** (Interfaces).
- **Adapters** implement **Ports**.
- **Entities** have NO dependencies on outer layers.

### ❓ Why this mapping?
1. **Separation of Concerns**: Domain logic (how a pipeline advances) is separated from how it's stored (Markdown files) or how AI reasoning is performed (Anthropic/OpenAI).
2. **Testability**: The Domain and Application layers can be tested without hitting real LLMs or the filesystem by mocking Ports.
3. **Flexibility**: We can swap LangGraph for another engine or change from Markdown to a Database by only modifying the Adapter layer.

## 🚀 Next Steps (Task 2-8)
1. **Systematic DI**: Ensure all Adapters are injected into Use Cases via a Composition Root (likely in `main.py` or the graph entry point).
2. **Aggregate Root Hardening**: Move all state changes into `Pipeline.py`.
3. **Value Objects**: Extract `TraceableId` logic into a VO.
4. **Specification Pattern**: Refactor `algorithms/` to DDD patterns.
