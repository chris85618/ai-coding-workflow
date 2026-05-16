"""HookEvent Enum — Lifecycle hook event types."""

from enum import StrEnum


class HookEvent(StrEnum):
    """Lifecycle hook event types (from Claude Code pattern)."""

    PRE_STAGE_START = "pre_stage_start"
    POST_STAGE_COMPLETE = "post_stage_complete"
    PRE_DOC_WRITE = "pre_doc_write"
    POST_DOC_WRITE = "post_doc_write"
