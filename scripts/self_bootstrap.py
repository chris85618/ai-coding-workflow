"""Self-bootstrap pipeline runner.

Composes the production dependency container over a target repository,
exports the master pipeline as an Archon workflow document and dispatches
it via the archon CLI — the sole orchestration engine (ADR-STR-033).
Without a configured LLM provider node executions degrade to the
OfflineReasoner; without the archon binary the dispatch degrades to the
exported document plus manual/AI-driven step execution through
scripts/run_node.py (ADR-GOV-017). No internal fallback runner exists by
design (ADR-STR-033 prohibition). Rollback is disabled unless
--allow-rollback is passed, so a bootstrap run can never damage the
working tree (ADR-GOV-015).
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass

from agentic_workflow.adapters.llm.offline_reasoner import OfflineReasoner
from agentic_workflow.adapters.persistence.markdown_pipeline_repository import MarkdownPipelineRepository
from agentic_workflow.adapters.persistence.markdown_writer import MarkdownDocumentIO
from agentic_workflow.application.ports.gateways.agent_reasoner import IAgentReasoner
from agentic_workflow.application.ports.gateways.version_control_gateway import IVersionControlGateway
from agentic_workflow.domain.aggregates.pipeline import Pipeline
from agentic_workflow.domain.value_objects.model_config import ModelConfig
from agentic_workflow.frameworks.archon_orchestrator import WORKFLOW_DOC_DIR
from agentic_workflow.frameworks.dependency_container import DependencyContainer
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


def summarize(pipeline_id: str, dispatched: bool) -> str:
    """Render the observable outcome of a bootstrap dispatch."""
    workflow_doc_dir = WORKFLOW_DOC_DIR
    lines = [
        f"pipeline_id : {pipeline_id}",
        f"workflow_doc: {workflow_doc_dir}/agentic-workflow-{pipeline_id}.yaml",
        f"dispatched  : {dispatched}",
    ]
    if not dispatched:
        lines.append(
            "degraded    : archon CLI unavailable; execute steps via "
            "scripts/run_node.py per the exported document (ADR-GOV-017)"
        )
    return "\n".join(lines)


def run(repo_root: str, pipeline_id: str, allow_rollback: bool) -> int:
    """Export the Archon workflow for repo_root and dispatch it (ADR-STR-033)."""
    os.chdir(repo_root)
    container = build_container(allow_rollback)
    gateway = container.agent_orchestrator
    positions = list(Pipeline(pipeline_id=pipeline_id).stages)
    workflow_doc = gateway.export_workflow(pipeline_id, positions)
    dispatched = gateway.dispatch(workflow_doc)
    print(summarize(pipeline_id, dispatched))
    return 0 if dispatched else 1


def main() -> int:
    """Parse arguments and run the self-bootstrap dispatch."""
    parser = argparse.ArgumentParser(description="Export and dispatch the master pipeline via Archon.")
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
