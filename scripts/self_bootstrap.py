"""Self-bootstrap pipeline runner (kanban: 執行自舉管線).

Composes the production dependency container over a target repository and
invokes the master pipeline graph end-to-end (Ouroboros closure, ADR-STR-029).
Without a configured LLM provider the run degrades to the OfflineReasoner
(ADR-GOV-017). Rollback is disabled unless --allow-rollback is passed, so a
bootstrap run can never damage the working tree (ADR-GOV-015).
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Any

from agentic_workflow.adapters.langgraph.nodes import set_container
from agentic_workflow.adapters.llm.offline_reasoner import OfflineReasoner
from agentic_workflow.adapters.persistence.markdown_pipeline_repository import MarkdownPipelineRepository
from agentic_workflow.adapters.persistence.markdown_writer import MarkdownDocumentIO
from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner
from agentic_workflow.application.ports.gateways.version_control_gateway import IVersionControlGateway
from agentic_workflow.domain.value_objects.model_config import ModelConfig
from agentic_workflow.frameworks.dependency_container import DependencyContainer
from agentic_workflow.frameworks.graph.master_graph_builder import MasterGraphBuilder
from agentic_workflow.frameworks.persistence.checkpoint_repository import FileCheckpointRepository

_API_KEY_ENV = "ANTHROPIC_API_KEY"
_DEFAULT_MODEL = "claude-sonnet-4-6"


class ReadOnlyVersionControl(IVersionControlGateway):
    """Refuses rollbacks so a bootstrap run can never damage the working tree."""

    def current_ref(self) -> str:
        """Report a placeholder ref; the read-only gateway never touches git."""
        return "read-only"

    def rollback_to(self, ref: str) -> bool:
        """Refuse the rollback and report failure transparently."""
        return False

    def tag_universal_base(self) -> str:
        """Report the canonical tag name without creating it."""
        return "universal-base"


@dataclass
class BootstrapContainer(DependencyContainer):
    """Container variant whose version control is read-only by default."""

    allow_rollback: bool = False

    @property
    def version_control(self) -> IVersionControlGateway:
        """Get the real git gateway only when rollback was explicitly allowed."""
        from agentic_workflow.frameworks.git_version_control import GitVersionControl

        gateway: IVersionControlGateway = GitVersionControl() if self.allow_rollback else ReadOnlyVersionControl()
        return gateway


def build_reasoner() -> IAgentReasoner:
    """Build the Anthropic reasoner when a key is configured; degrade offline otherwise."""
    api_key_env = _API_KEY_ENV
    api_key = os.environ.get(api_key_env)
    if not api_key:
        return OfflineReasoner()
    from agentic_workflow.frameworks.llm.anthropic_reasoner import AnthropicReasoner

    default_model = _DEFAULT_MODEL
    return AnthropicReasoner(ModelConfig(provider="anthropic", model=default_model, api_key=api_key))


def build_container(allow_rollback: bool) -> BootstrapContainer:
    """Compose the production container over the current working directory."""
    from agentic_workflow.adapters.filesystem import register_filesystem
    from agentic_workflow.adapters.subprocess import register_executor
    from agentic_workflow.frameworks.filesystem_io import OSFilesystemIO
    from agentic_workflow.frameworks.subprocess_executor import OSSubprocessExecutor

    register_filesystem(OSFilesystemIO())
    register_executor(OSSubprocessExecutor())
    doc_io = MarkdownDocumentIO(".")
    return BootstrapContainer(
        pipeline_repo=MarkdownPipelineRepository(doc_io),
        checkpoint_repo=FileCheckpointRepository("."),
        doc_io=doc_io,
        reasoner=build_reasoner(),
        allow_rollback=allow_rollback,
    )


def summarize(final_state: dict[str, Any]) -> str:
    """Render the observable outcome of a bootstrap run."""
    metadata = final_state.get("metadata", {})
    lines = [
        f"pipeline_id       : {final_state.get('pipeline_id')}",
        f"pipeline_status   : {final_state.get('pipeline_status')}",
        f"current_position  : {final_state.get('current_position')}",
        f"gate_decision     : {final_state.get('gate_decision')}",
        f"debt_items        : {len(metadata.get('debt_items', []))}",
        f"hitl_required     : {metadata.get('hitl_required', False)}",
        f"rollback_performed: {metadata.get('rollback_performed', False)}",
        f"last_error        : {final_state.get('last_error')}",
    ]
    return "\n".join(lines)


def run(repo_root: str, pipeline_id: str, allow_rollback: bool) -> int:
    """Execute the master pipeline against repo_root and report the outcome."""
    os.chdir(repo_root)
    container = build_container(allow_rollback)
    try:
        set_container(container)
        app = MasterGraphBuilder.build()
        final_state = app.invoke({"pipeline_id": pipeline_id, "stage_status": "pending"})
    finally:
        set_container(None)
    print(summarize(dict(final_state)))
    return 0


def main() -> int:
    """Parse arguments and run the self-bootstrap pipeline."""
    parser = argparse.ArgumentParser(description="Run the master pipeline end-to-end (self-bootstrap).")
    parser.add_argument("--repo-root", default=".", help="Target repository root (default: current directory).")
    parser.add_argument("--pipeline-id", default="self-bootstrap", help="Pipeline identifier for the run.")
    parser.add_argument(
        "--allow-rollback",
        action="store_true",
        help="Allow the DIVERGING degradation path to run git reset --hard (destructive).",
    )
    args = parser.parse_args()
    return run(args.repo_root, args.pipeline_id, args.allow_rollback)


if __name__ == "__main__":
    sys.exit(main())
