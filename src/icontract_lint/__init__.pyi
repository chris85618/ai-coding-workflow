import enum
import pathlib
from typing import Final

class ErrorID(enum.Enum):
    UNREADABLE = "unreadable"
    PRE_INVALID_ARG = "pre-invalid-arg"
    SNAPSHOT_INVALID_ARG = "snapshot-invalid-arg"
    SNAPSHOT_WO_CAPTURE = "snapshot-wo-capture"
    SNAPSHOT_WO_POST = "snapshot-wo-post"
    SNAPSHOT_WO_NAME = "snapshot-wo-name"
    POST_INVALID_ARG = "post-invalid-arg"
    POST_RESULT_NONE = "post-result-none"
    POST_RESULT_CONFLICT = "post-result-conflict"
    POST_OLD_CONFLICT = "post-old-conflict"
    INV_INVALID_ARG = "inv-invalid-arg"
    NO_CONDITION = "no-condition"
    INVALID_SYNTAX = "invalid-syntax"

class Error:
    identifier: Final[ErrorID]
    description: Final[str]
    filename: Final[str]
    lineno: Final[int | None]

def check_file(path: pathlib.Path) -> list[Error]: ...
def check_paths(paths: list[pathlib.Path]) -> list[Error]: ...
def check_recursively(path: pathlib.Path) -> list[Error]: ...
