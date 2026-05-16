"""TaskType Enum — LLM task type for Strategy Pattern model selection."""

from enum import StrEnum


class TaskType(StrEnum):
    """LLM task type for Strategy Pattern model selection (ALG-008).

    Each type maps to a different model tier:
        CRITIQUE   -> reasoning model (Agent alpha)
        RESOLVE    -> editing model (Agent beta)
        COMPREHEND -> reasoning model (Phase 1)
        CHARTER    -> reasoning model (Phase 2)
        FORMAT     -> cheap model (simple formatting)
    """

    CRITIQUE = "critique"
    RESOLVE = "resolve"
    COMPREHEND = "comprehend"
    CHARTER = "charter"
    FORMAT = "format"
