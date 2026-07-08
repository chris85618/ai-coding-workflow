"""Adapters Layer — Interface Adapters.

Converts data between use case format and external format.
Implements port interfaces defined in application/ports/.

Subpackages:
    orchestration/ : workflow node functions + state mapper + single-node executor
    mcp/         : GitKraken + Sequential Thinking MCP adapters
    persistence/ : File repo, checkpoint repo, markdown reader/writer
    llm/         : LLM provider adapter (Agent alpha/beta)
    events/      : In-memory event bus implementation
"""

from agentic_workflow.adapters.filesystem import (
    default_exists,
    default_extract_symbols_ast,
    default_glob,
    default_is_dir,
    default_list_files,
    default_read_text,
    default_read_text_absolute,
)
from agentic_workflow.adapters.subprocess import default_run_cmd
from agentic_workflow.domain.algorithms.pipeline_completeness import PipelineCompletenessChecker
from agentic_workflow.domain.algorithms.repo_map_builder import RepoMapBuilder
from agentic_workflow.domain.services.hook_runner.hook_runner import HookRunner

# Register concrete adapter implementations to domain class provider registries (Composition Root)
PipelineCompletenessChecker.default_exists_fn = default_exists
PipelineCompletenessChecker.default_read_text_fn = default_read_text
PipelineCompletenessChecker.default_glob_fn = default_glob

RepoMapBuilder.default_list_files_fn = default_list_files
RepoMapBuilder.default_read_text_fn = default_read_text_absolute
RepoMapBuilder.default_extract_symbols_fn = default_extract_symbols_ast
RepoMapBuilder.default_is_dir_fn = default_is_dir

HookRunner.default_run_cmd_fn = default_run_cmd
