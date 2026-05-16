"""LinkType Enum — Trace link relationship type."""

from enum import StrEnum


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
