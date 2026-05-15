"""Frameworks Layer — Entry Point.

Wiring for the LangGraph application.
"""

from __future__ import annotations

from agentic_workflow.frameworks.config import load_config
from agentic_workflow.frameworks.graph import build_graph


def main() -> None:
    """Main entry point."""
    print("Loading configuration... (ADR-STR-006)")
    config = load_config()
    print(f"Loaded config with models: {list(config.models.keys())}")

    print("Building LangGraph DAG...")
    build_graph()

    print("Application initialized. Ready to invoke pipelines.")
    # Example invocation:
    # state = {"pipeline_id": "test-1", "pipeline_status": "not_started"}
    # final_state = app.invoke(state)


if __name__ == "__main__":  # pragma: no cover
    main()
