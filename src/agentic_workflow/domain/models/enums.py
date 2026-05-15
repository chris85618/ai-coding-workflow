"""Enumerations for domain models.

All enums are str-based for JSON serialization compatibility.
"""

from enum import StrEnum


class PipelineStatus(StrEnum):
    """Pipeline execution status. INV-001 enforces unidirectional transitions."""

    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StageStatus(StrEnum):
    """Stage iteration status. INV-003 enforces unidirectional transitions."""

    PENDING = "pending"
    ITERATING = "iterating"
    PASSED = "passed"
    FAILED = "failed"


class GateDecision(StrEnum):
    """Auto-gate decision result. Replaces HitlChoice (ADR-STR-003)."""

    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"


class FixedPointResult(StrEnum):
    """Iteration convergence check result."""

    REACHED = "reached"
    NOT_REACHED = "not_reached"
    DIVERGING = "diverging"
    MAX_ITERATIONS = "max_iterations"


class Severity(StrEnum):
    """Finding or impact severity classification.

    COSMETIC: blast_radius == 0 (INV-012)
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    COSMETIC = "cosmetic"
    YAGNI = "yagni"


class IDPrefix(StrEnum):
    """Traceable ID prefix. Maps to pipeline stages."""

    BG = "BG"
    S = "S"
    FEA = "FEA"
    FR = "FR"
    NFR = "NFR"
    UC = "UC"
    ADR_STR = "ADR-STR"
    ADR_GOV = "ADR-GOV"
    ADR_SEC = "ADR-SEC"
    ALG = "ALG"
    CLS = "CLS"
    EVT = "EVT"
    INV = "INV"
    SC = "SC"
    TC = "TC"
    DEBT = "DEBT"
    RISK = "RISK"
    LESSON = "LESSON"


class LinkType(StrEnum):
    """Trace link relationship type."""

    DERIVES = "derives"
    DECOMPOSES = "decomposes"
    REALIZES = "realizes"
    IMPLEMENTS = "implements"
    MODELS = "models"
    FORMALIZES = "formalizes"
    COVERS = "covers"
    VALIDATES = "validates"
    JUSTIFIES = "justifies"
    EMITTED_BY = "emitted-by"
    MITIGATES = "mitigates"


class DebtSource(StrEnum):
    """Technical debt origin."""

    DESIGN = "design"
    CODE = "code"
    DOCUMENTATION = "documentation"
    TEST = "test"


class Priority(StrEnum):
    """Debt/risk priority level."""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class HookEvent(StrEnum):
    """Lifecycle hook event types (from Claude Code pattern)."""

    PRE_STAGE_START = "pre_stage_start"
    POST_STAGE_COMPLETE = "post_stage_complete"
    PRE_DOC_WRITE = "pre_doc_write"
    POST_DOC_WRITE = "post_doc_write"


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
