"""Contract verification suite: static lint, property-based fuzzing, and symbolic checking.

Three verification layers over the deal Design-by-Contract annotations:
- deal lint  -> static contract well-formedness over src/
- deal.cases -> property-based fuzzing driven by contract-inferred strategies (hypothesis)
- CrossHair  -> Z3-backed symbolic checking of contract consistency (analysis_kind=deal)

Traceable to: TC-CONTRACT-001 ~ TC-CONTRACT-004, INV-015, INV-016
"""

import pathlib
import subprocess
import sys
import typing
from collections.abc import Callable

import deal
import hypothesis
import hypothesis.strategies as st

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


def test_deal_lint_src_clean() -> None:
    """TC-CONTRACT-001: deal lint reports zero contract errors across src/."""
    cmd = [sys.executable, "-m", "deal", "lint", "--nocolor", str(_src_dir)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=False, cwd=_root)
    assert result.returncode == 0, (
        f"deal lint violations (exit {result.returncode}).\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
    )


def _classmethod_target(owner: type, name: str) -> Callable[..., object]:
    """Unwrap a contracted classmethod to its raw function for deal.cases."""
    return typing.cast("Callable[..., object]", owner.__dict__[name].__func__)


_fuzz_settings = hypothesis.settings(
    deadline=None,
    # Sparse preconditions (e.g. VALID_IMPACT_VALUES membership) reject most
    # generated floats; that is expected pruning, not a test-health problem.
    suppress_health_check=[hypothesis.HealthCheck.filter_too_much, hypothesis.HealthCheck.too_slow],
)


def test_contract_fuzz_check_convergence() -> None:
    """TC-CONTRACT-002: fuzz ConvergenceDetector.check_convergence via contract-driven cases."""
    fuzz = deal.cases(
        _classmethod_target(ConvergenceDetector, "check_convergence"),
        kwargs={"cls": ConvergenceDetector},
        count=_fuzz_max_examples,
        settings=_fuzz_settings,
    )
    fuzz()


def test_contract_fuzz_rice_score() -> None:
    """TC-CONTRACT-003: fuzz RiceScorer.score with explicit strategies.

    The sparse VALID_IMPACT_VALUES membership precondition rejects nearly every
    inferred float, so impact is sampled directly from the valid set while the
    deal pre/ensure contracts stay fully enforced at call time.
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
        "deal",
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
