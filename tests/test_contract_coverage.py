"""Contract Coverage gate: every concrete public domain callable carries deal contracts.

Contract coverage is measured with deal.introspection over the runtime objects,
not by source grepping, so decorators applied through helpers still count.

Scope: every public method of every public concrete class in agentic_workflow.domain.
Exclusions (by construction, not whitelist):
- dunder / private members
- properties (attribute-shaped reads carry class invariants instead)
- abstract method declarations (specs live on implementations)
- Enum / Exception members
- injected provider slots (class attributes holding callables registered by
  outer layers, detected via __qualname__ ownership)

Traceable to: TC-CONTRACT-005, ADR-STR-028, docs/formal-verification-spec.md §1
"""

import importlib
import inspect
import pkgutil
from collections.abc import Callable

import deal.introspection

import agentic_workflow.domain as domain_pkg


def _unwrap(member: object) -> Callable[..., object] | None:
    """Return the underlying function for plain/class/static methods, else None."""
    fn = member
    if isinstance(member, (classmethod, staticmethod)):
        fn = member.__func__
    if isinstance(fn, property) or not callable(fn):
        return None
    return fn


def _is_abstract(fn: Callable[..., object]) -> bool:
    """True when the callable is only an abstract declaration."""
    return bool(getattr(fn, "__isabstractmethod__", False))


def _iter_public_domain_methods() -> list[tuple[str, Callable[..., object]]]:
    """Enumerate (label, function) for every concrete public domain method."""
    found: list[tuple[str, Callable[..., object]]] = []
    for modinfo in pkgutil.walk_packages(domain_pkg.__path__, prefix="agentic_workflow.domain."):
        module = importlib.import_module(modinfo.name)
        for cls_name, cls in vars(module).items():
            is_local_public_class = inspect.isclass(cls) and cls.__module__ == modinfo.name
            if not is_local_public_class or cls_name.startswith("_") or issubclass(cls, Exception):
                continue
            for name, member in vars(cls).items():
                fn = _unwrap(member)
                if fn is None or name.startswith("_") or _is_abstract(fn):
                    continue
                qualname = getattr(fn, "__qualname__", "")
                if not qualname.startswith(f"{cls.__qualname__}."):
                    continue  # injected provider slot, not a method of this class
                found.append((f"{modinfo.name}.{cls_name}.{name}", fn))
    return found


def _has_contract(fn: Callable[..., object]) -> bool:
    """True when deal.introspection reports at least one contract on fn."""
    return bool(list(deal.introspection.get_contracts(fn)))


def test_domain_contract_coverage_is_total() -> None:
    """TC-CONTRACT-005: 100% of concrete public domain methods carry >=1 deal contract."""
    methods = _iter_public_domain_methods()
    assert methods, "Domain scan found no public methods; the scanner itself is broken"
    missing = sorted(label for label, fn in methods if not _has_contract(fn))
    covered = len(methods) - len(missing)
    assert not missing, (
        f"Contract coverage {covered}/{len(methods)} "
        f"({covered / len(methods):.1%}) — methods without any deal contract:\n" + "\n".join(missing)
    )
