"""Single-node runner for Archon workflow steps (FR-077, FR-078, ADR-STR-033).

Executes exactly one workflow node per process invocation and persists the
resulting state through the checkpoint repository. Sequencing, loops,
conditions and gates live exclusively in the exported Archon workflow
document; this script never advances more than the named node, so it does
not constitute an internal orchestration engine. Router nodes print their
route to stdout for Archon condition constructs to consume.
"""

from __future__ import annotations

import argparse
import os
import sys

from agentic_workflow.adapters.orchestration.nodes import set_container
from self_bootstrap import build_container


def run(repo_root: str, pipeline_id: str, node: str, allow_rollback: bool) -> int:
    """Execute one workflow node against repo_root and print its route (if any)."""
    os.chdir(repo_root)
    container = build_container(allow_rollback)
    try:
        set_container(container)
        route = container.node_executor.execute(pipeline_id, node)
    finally:
        set_container(None)
    if route:
        print(route)
    return 0


def main() -> int:
    """Parse arguments and run exactly one workflow node."""
    parser = argparse.ArgumentParser(description="Execute exactly one workflow node (ADR-STR-033).")
    parser.add_argument("--node", required=True, help="Registered node or router name from the workflow document.")
    parser.add_argument("--pipeline-id", default="default", help="Pipeline identifier for the run.")
    parser.add_argument("--repo-root", default=".", help="Target repository root (default: current directory).")
    parser.add_argument(
        "--allow-rollback",
        action="store_true",
        help="Allow the rollback node to run git reset --hard (destructive).",
    )
    args = parser.parse_args()
    return run(args.repo_root, args.pipeline_id, args.node, args.allow_rollback)


if __name__ == "__main__":
    sys.exit(main())
