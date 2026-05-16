"""IDPrefix Enum — Traceable ID prefix. Maps to pipeline stages."""

from enum import StrEnum


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
