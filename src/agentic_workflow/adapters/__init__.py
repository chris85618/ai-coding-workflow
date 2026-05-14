"""Adapters Layer — Interface Adapters.

Converts data between use case format and external format.
Implements port interfaces defined in application/ports/.

Subpackages:
    langgraph/   : LangGraph node functions + state mapper
    mcp/         : GitKraken + Sequential Thinking MCP adapters
    persistence/ : File repo, checkpoint repo, markdown reader/writer
    llm/         : LLM provider adapter (Agent alpha/beta)
    events/      : In-memory event bus implementation
"""
