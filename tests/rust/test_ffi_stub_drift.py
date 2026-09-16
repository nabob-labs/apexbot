"""Registration↔stub drift gate (ergo DSWX6Z).

The PyO3 registration surface (``rust/crates/apexbot-python/src/c_api.rs`` +
the per-domain ``add_*_module`` fns) is the source of truth for what the
``apexbot._ffi`` extension exposes at runtime. The type stubs in
``src/apexbot/_ffi/*.pyi`` are hand-maintained, and nothing mechanical used
to catch drift between the two (the extension module wins over the
namespace-package stub dir at import time, so the stubs are invisible to the
runtime). This test pins both directions:

- **R1 (coverage)**: every public runtime symbol of a stubbed module must
  appear in its stub — defined (class / function / assignment) or bound via a
  top-level import.
- **R2 (honest ``__all__``)**: every ``__all__`` entry of a stub must exist at
  runtime — phantom entries would break ``import *``.
- **R3 (no phantom definitions)**: every class/function/constant a stub
  DEFINES at top level must exist at runtime. Annotation-only type imports
  are exempt: they document parameter types, not the module surface.
- **R0 (submodule coverage)**: every runtime ``apexbot._ffi.*`` submodule
  must have a stub file.
- **R4 (class-member drift)**: for a curated set of hand-maintained classes,
  the stub's declared members must match the compiled class's OWN members in
  both directions — a stub member with no runtime implementation (the A527QE
  misplaced-member shape) and a runtime member the stub omits.

Surface-changing tasks must update the affected stub in the same commit so
this gate stays green (epic C7D2CH guardrail).
"""

from __future__ import annotations

import ast
import importlib
import pathlib
import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator

_STUB_DIR = pathlib.Path(__file__).resolve().parents[2] / "src" / "apexbot" / "_ffi"


def _stub_modules() -> dict[str, pathlib.Path]:
    """Importable module name -> stub file, for the root + every submodule stub."""
    mods: dict[str, pathlib.Path] = {"apexbot._ffi": _STUB_DIR / "__init__.pyi"}
    for path in sorted(_STUB_DIR.glob("*.pyi")):
        if path.name == "__init__.pyi":
            continue
        mods[f"apexbot._ffi.{path.stem}"] = path
    return mods


def _runtime_public_names(module_name: str) -> set[str]:
    obj = importlib.import_module(module_name)
    return {n for n in dir(obj) if not n.startswith("_")}


def _top_level_nodes(stub_path: pathlib.Path) -> Iterator[ast.stmt]:
    return ast.iter_child_nodes(ast.parse(stub_path.read_text(encoding="utf-8")))


def _stub_defined_names(stub_path: pathlib.Path) -> set[str]:
    """Top-level classes / functions / assignments the stub DEFINES."""
    names: set[str] = set()
    for node in _top_level_nodes(stub_path):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id != "__all__":
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def _stub_bound_names(stub_path: pathlib.Path) -> set[str]:
    """Defined names + names bound by top-level imports (R1 coverage set)."""
    names = _stub_defined_names(stub_path)
    for node in _top_level_nodes(stub_path):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                names.add((alias.asname or alias.name).split(".")[0])
    return names


def _stub_all_names(stub_path: pathlib.Path) -> set[str] | None:
    for node in _top_level_nodes(stub_path):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    value = node.value
                    if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
                        return {el.value for el in value.elts if isinstance(el, ast.Constant)}
    return None


@pytest.mark.parametrize("module_name", sorted(_stub_modules()))
def test_runtime_symbols_are_stubbed(module_name: str) -> None:
    """R1: every public runtime symbol is documented in the stub."""
    stub = _stub_modules()[module_name]
    runtime = _runtime_public_names(module_name)
    stubbed = _stub_bound_names(stub)
    missing = sorted(runtime - stubbed)
    assert not missing, f"{module_name}: runtime symbols missing from {stub.name}: {missing}"


@pytest.mark.parametrize("module_name", sorted(_stub_modules()))
def test_stub_all_is_honest(module_name: str) -> None:
    """R2: every ``__all__`` entry exists at runtime (no phantom promises)."""
    stub = _stub_modules()[module_name]
    all_names = _stub_all_names(stub)
    if all_names is None:
        pytest.skip(f"{stub.name} declares no __all__")
    runtime = _runtime_public_names(module_name)
    phantom = sorted(all_names - runtime)
    assert not phantom, f"{module_name}: __all__ entries absent at runtime: {phantom}"


@pytest.mark.parametrize("module_name", sorted(_stub_modules()))
def test_stub_definitions_exist_at_runtime(module_name: str) -> None:
    """R3: classes/functions/constants the stub defines exist at runtime."""
    stub = _stub_modules()[module_name]
    runtime = _runtime_public_names(module_name)
    phantom = sorted(_stub_defined_names(stub) - runtime)
    assert not phantom, (
        f"{module_name}: stub defines names absent at runtime (phantom surface): {phantom}"
    )


# ---------------------------------------------------------------------------
# R4 — class-member drift (ergo S3FOCH / review A527QE)
# ---------------------------------------------------------------------------
# R1/R3 pin only the module's TOP-LEVEL symbols. Review A527QE found a stub
# method sitting on the WRONG class ('pump_finished_future' on 'Bot' instead
# of 'ArbitrageEngine') while the gate stayed green. R4 closes that hole: for
# a curated set of hand-maintained classes it compares the stub's declared
# member set against the compiled class's OWN members, in BOTH directions — a
# stub member with no runtime implementation (misplaced or phantom) AND a
# runtime member the stub never declares (undocumented surface). Add one row
# to '_CLASS_STUBS' to extend coverage.
#
# Introspection uses 'vars(cls)' — 'dir(cls)' restricted to the class's own
# '__dict__' — so members *inherited* from a builtin base (e.g.
# 'Exception.args' / 'with_traceback' on the error classes) are not mistaken
# for undocumented surface. The stub side resolves same-file stub base classes
# transitively for the same reason.
#
# Dunder filter: every '#[pyclass]' gets the same default Python
# object-protocol dunders from PyO3; the hand-maintained stubs legitimately
# omit them, so '_DEFAULT_PY_DUNDERS' is filtered from BOTH sides. Only
# DEFAULTS are filtered: a non-default dunder the stub declares
# ('__iter__' / '__next__' / '__aiter__' / '__anext__') is still compared,
# because a misplaced iterator dunder is exactly the class of bug this gate
# must catch.

_DEFAULT_PY_DUNDERS = frozenset({
    "__class__",
    "__delattr__",
    "__dir__",
    "__doc__",
    "__eq__",
    "__format__",
    "__ge__",
    "__getattribute__",
    "__getstate__",
    "__gt__",
    "__hash__",
    "__init__",
    "__init_subclass__",
    "__le__",
    "__lt__",
    "__module__",
    "__ne__",
    "__new__",
    "__reduce__",
    "__reduce_ex__",
    "__repr__",
    "__setattr__",
    "__sizeof__",
    "__str__",
    "__subclasshook__",
    "__weakref__",
})

# Curated top-N of the hand-maintained classes with a meaningful surface.
# Excludes the exception classes: their runtime members are inherited from
# 'RuntimeError'/'ValueError' and already covered by R1/R3 (they declare no
# members of their own).
_CLASS_STUBS: tuple[tuple[str, str], ...] = (
    ("apexbot._ffi", "PathIterator"),
    ("apexbot._ffi", "PathBatchIterator"),
    ("apexbot._ffi", "Erc20Token"),
    ("apexbot._ffi", "LiquidityPool"),
    ("apexbot._ffi", "Erc20TokenRow"),
    ("apexbot._ffi", "BotIo"),
    ("apexbot._ffi", "Bot"),
    ("apexbot._ffi", "ArbitrageEngine"),
    ("apexbot._ffi", "BlockStream"),
    ("apexbot._ffi", "IntakeReceipt"),
    ("apexbot._ffi", "Pool"),
    ("apexbot._ffi", "ReservePairView"),
    ("apexbot._ffi", "ConcentratedLiquidityView"),
    ("apexbot._ffi", "BalanceVectorView"),
    ("apexbot._ffi.cancel", "CancelHandle"),
    ("apexbot._ffi.contract", "Contract"),
    ("apexbot._ffi.contract", "AsyncContract"),
    ("apexbot._ffi.curve_dy", "DyCalculationInputs"),
    ("apexbot._ffi.db", "V2PoolRowInput"),
    ("apexbot._ffi.db", "V3PoolRowInput"),
    ("apexbot._ffi.db", "V4PoolRowInput"),
    ("apexbot._ffi.db", "DatabaseSnapshot"),
    ("apexbot._ffi.db", "DatabasePositionQuery"),
    ("apexbot._ffi.db", "CollateralPositionData"),
    ("apexbot._ffi.db", "DebtPositionData"),
    ("apexbot._ffi.db", "UserPositionSummary"),
    ("apexbot._ffi.db", "LiquidityPoolRow"),
    ("apexbot._ffi.db", "ExchangeRow"),
    ("apexbot._ffi.db", "PoolManagerRow"),
    ("apexbot._ffi.db", "LiquidityUpdateEvent"),
    ("apexbot._ffi.dex_identity", "DexIdentity"),
    ("apexbot._ffi.execution", "SolveResult"),
    ("apexbot._ffi.execution", "PayloadComposer"),
    ("apexbot._ffi.fork", "AnvilFork"),
    ("apexbot._ffi.price", "ChainlinkPriceFeed"),
    ("apexbot._ffi.price", "AavePriceOracle"),
    ("apexbot._ffi.provider", "AlloyProvider"),
    ("apexbot._ffi.provider", "LogFilter"),
    ("apexbot._ffi.provider", "AsyncAlloyProvider"),
    ("apexbot._ffi.provider", "AlloySubscription"),
    ("apexbot._ffi.simulation", "SimulateContext"),
    ("apexbot._ffi.simulation", "DispatchCandidate"),
    ("apexbot._ffi.simulation", "DispatchOutcome"),
    ("apexbot._ffi.simulation", "PayloadVerdict"),
    ("apexbot._ffi.simulation", "PayloadOutcome"),
    ("apexbot._ffi.submission", "Dispatcher"),
    ("apexbot._ffi.submission", "DivergentPool"),
    ("apexbot._ffi.submission", "TxSigner"),
    ("apexbot._ffi.submission", "TxParams"),
    ("apexbot._ffi.submission", "SubmitCandidate"),
)


def _stub_class_defs(stub_source: str) -> dict[str, tuple[set[str], list[str]]]:
    """Class name -> (declared member names, same-file stub base names)."""
    defs: dict[str, tuple[set[str], list[str]]] = {}
    for node in ast.iter_child_nodes(ast.parse(stub_source)):
        if not isinstance(node, ast.ClassDef):
            continue
        members: set[str] = set()
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                members.add(child.name)
            elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                members.add(child.target.id)
            elif isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name) and target.id != "__all__":
                        members.add(target.id)
        bases = [ast.unparse(base).split(".")[-1] for base in node.bases]
        defs[node.name] = (members, bases)
    return defs


def _stub_class_members(defs: dict[str, tuple[set[str], list[str]]], class_name: str) -> set[str]:
    """Members the stub declares for 'class_name', including same-file bases."""
    members: set[str] = set()
    pending = [class_name]
    seen: set[str] = set()
    while pending:
        name = pending.pop()
        if name in seen or name not in defs:
            continue
        seen.add(name)
        declared, bases = defs[name]
        members |= declared
        pending.extend(bases)
    return members


def _class_member_drift(
    module_name: str,
    class_name: str,
    stub_source: str,
) -> tuple[set[str], set[str]]:
    """Return (stub-declared-but-absent, runtime-own-but-undeclared)."""
    runtime_cls = getattr(importlib.import_module(module_name), class_name)
    stub_members = {
        name
        for name in _stub_class_members(_stub_class_defs(stub_source), class_name)
        if name not in _DEFAULT_PY_DUNDERS
    }
    runtime_members = {name for name in vars(runtime_cls) if name not in _DEFAULT_PY_DUNDERS}
    return stub_members - runtime_members, runtime_members - stub_members


@pytest.mark.parametrize(("module_name", "class_name"), _CLASS_STUBS)
def test_stub_class_members_match_runtime(module_name: str, class_name: str) -> None:
    """R4: a stub class's members match the compiled class in both directions."""
    stub = _stub_modules()[module_name]
    stub_only, impl_only = _class_member_drift(
        module_name, class_name, stub.read_text(encoding="utf-8")
    )
    problems: list[str] = []
    if stub_only:
        problems.append(
            f"stub-declared but absent at runtime (misplaced/phantom): {sorted(stub_only)}"
        )
    if impl_only:
        problems.append(
            f"runtime members absent from the stub (undocumented surface): {sorted(impl_only)}"
        )
    assert not problems, f"{module_name}.{class_name}: " + "; ".join(problems)


# Negative control: a stub whose member set is deliberately wrong. PathIterator
# is the cheapest runtime class to bind (two real dunders, no construction).
_PHANTOM_PATH_ITERATOR = """
class PathIterator:
    def __iter__(self) -> object: ...
    def __next__(self) -> object: ...
    def pump_finished_future(self) -> None: ...
"""

_OMITTED_PATH_ITERATOR = """
class PathIterator:
    def __iter__(self) -> object: ...
"""


def test_class_member_drift_bites_on_a_misplaced_stub_member() -> None:
    """Negative control (A527QE shape): R4 must flag a wrong class member.

    Both directions are proven against a deliberately-wrong stub: a real method
    name parked on the wrong class (stub-declared, no implementation), and a
    real '__next__' the stub forgot to declare.
    """
    stub_only, impl_only = _class_member_drift(
        "apexbot._ffi", "PathIterator", _PHANTOM_PATH_ITERATOR
    )
    assert stub_only == {"pump_finished_future"}, (
        f"phantom member not detected; stub_only={sorted(stub_only)}"
    )
    assert impl_only == set(), f"unexpected impl-only drift: {sorted(impl_only)}"

    stub_only, impl_only = _class_member_drift(
        "apexbot._ffi", "PathIterator", _OMITTED_PATH_ITERATOR
    )
    assert stub_only == set(), f"unexpected stub-only drift: {sorted(stub_only)}"
    assert impl_only == {"__next__"}, (
        f"undocumented member not detected; impl_only={sorted(impl_only)}"
    )


def test_every_runtime_submodule_has_a_stub() -> None:
    """R0: every runtime `apexbot._ffi.*` submodule has a stub file."""
    import apexbot._ffi  # ruff: ignore[unused-import]  (registers the submodules)

    stub_stems = {p.stem for p in _STUB_DIR.glob("*.pyi") if p.name != "__init__.pyi"}
    runtime_subs = {
        name.removeprefix("apexbot._ffi.")
        for name in sys.modules
        if name.startswith("apexbot._ffi.")
    }
    missing = sorted(runtime_subs - stub_stems)
    assert not missing, f"runtime submodules missing a stub: {missing}"
