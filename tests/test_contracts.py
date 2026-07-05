"""Contract verification suite: static lint, property-based fuzzing, and symbolic checking.

Three verification layers over the icontract Design-by-Contract annotations:
- pyicontract-lint     -> static contract well-formedness over src/
- icontract-hypothesis -> property-based fuzzing driven by contract-inferred strategies
- CrossHair            -> Z3-backed symbolic checking of contract consistency

Traceable to: TC-CONTRACT-001 ~ TC-CONTRACT-004, INV-015, INV-016
"""

import pathlib
import subprocess
import sys
import typing
from collections.abc import Callable

import hypothesis
import hypothesis.strategies as st
import icontract_hypothesis

import icontract_lint
from agentic_workflow.domain.algorithms.convergence import ConvergenceDetector
from agentic_workflow.domain.algorithms.rice_scoring import RiceScorer

_root = pathlib.Path(__file__).parent.parent.resolve()
_src_dir = _root / "src"

# Modules verified symbolically. Keep entries pure and deterministic so the
# Z3 exploration budget below stays sufficient.
_crosshair_target_modules = (
    "src/agentic_workflow/domain/algorithms/convergence.py",
    "src/agentic_workflow/domain/algorithms/rice_scoring.py",
    "src/agentic_workflow/domain/entities/stage.py",
    "src/agentic_workflow/domain/aggregates/pipeline.py",
)
# 5s per condition keeps full-suite latency tolerable; raise when running deep audits.
_crosshair_per_condition_timeout = "5"

_fuzz_max_examples = 50


def test_pyicontract_lint_src_clean() -> None:
    """TC-CONTRACT-001: pyicontract-lint reports zero contract errors across src/."""
    errors = icontract_lint.check_recursively(_src_dir)
    report = [f"{e.filename}:{e.lineno}: {e.identifier}: {e.description}" for e in errors]
    assert not report, "pyicontract-lint violations:\n" + "\n".join(report)


def test_contract_fuzz_check_convergence() -> None:
    """TC-CONTRACT-002: fuzz ConvergenceDetector.check_convergence via contract-inferred strategies."""
    target = ConvergenceDetector.check_convergence
    runner = typing.cast("Callable[..., object]", target)
    strategy = icontract_hypothesis.infer_strategy(target)

    @hypothesis.given(strategy)
    @hypothesis.settings(max_examples=_fuzz_max_examples, deadline=None)
    def run(kwargs: dict[str, object]) -> None:
        arguments = dict(kwargs)
        # infer_strategy on a classmethod also emits a 'self' binding; drop it.
        arguments.pop("self", None)
        runner(**arguments)

    run()


def test_contract_fuzz_rice_score() -> None:
    """TC-CONTRACT-003: fuzz RiceScorer.score with explicit strategies.

    The inferred strategy filters floats() through the sparse VALID_IMPACT_VALUES
    membership predicate, which fails hypothesis health checks; impact is therefore
    sampled directly from the valid set while the remaining preconditions keep
    their inferred bounds.
    """
    valid_impacts = sorted(RiceScorer.VALID_IMPACT_VALUES)

    @hypothesis.given(
        reach=st.integers(min_value=1, max_value=100),
        impact=st.sampled_from(valid_impacts),
        confidence=st.floats(min_value=0.5, max_value=1.0),
        effort=st.floats(min_value=0, exclude_min=True, allow_nan=False, allow_infinity=False),
    )
    @hypothesis.settings(max_examples=_fuzz_max_examples, deadline=None)
    def run(reach: int, impact: float, confidence: float, effort: float) -> None:
        RiceScorer.score(reach=reach, impact=impact, confidence=confidence, effort=effort)

    run()


def test_crosshair_symbolic_contract_check() -> None:
    """TC-CONTRACT-004: CrossHair finds no counterexample to any contract in the target modules."""
    timeout = _crosshair_per_condition_timeout
    modules = _crosshair_target_modules
    cmd = [
        sys.executable,
        "-m",
        "crosshair",
        "check",
        "--analysis_kind",
        "icontract",
        "--per_condition_timeout",
        timeout,
        *modules,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=False, cwd=_root)
    assert result.returncode == 0, (
        f"CrossHair found contract counterexamples (exit {result.returncode}).\n"
        f"Stdout:\n{result.stdout}\n"
        f"Stderr:\n{result.stderr}"
    )
