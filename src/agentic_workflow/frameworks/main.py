"""Frameworks Layer — Entry Point.

Wiring for the Archon-orchestrated workflow application (ADR-STR-033).
"""

from __future__ import annotations

from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.frameworks.archon_orchestrator import ArchonOrchestrator
from agentic_workflow.frameworks.config import WorkflowConfigLoader


def main() -> None:
    """Main entry point."""
    print("Loading configuration... (ADR-STR-006)")
    config = WorkflowConfigLoader.load()
    print(f"Loaded config with models: {list(config.models.keys())}")

    print("Exporting Archon workflow document (ADR-STR-033)...")
    positions = list(Pipeline(pipeline_id="default").stages)
    ArchonOrchestrator().export_workflow("default", positions)

    print("Application initialized. Dispatch pipelines with: archon run .archon/agentic-workflow.yaml")


if __name__ == "__main__":  # pragma: no cover
    main()
