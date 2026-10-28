"""Companion→FFI alias-identity contract for the whole companion surface.

ADR-005 puts apexbot in three layers: a Rust engine (exposed through the
PyO3 wrapper ``apexbot._ffi``), thin companion packages that re-export the
FFI symbols under stable, seam-agnostic names, and the Python driver.

The load-bearing invariant of the middle layer: every companion re-export
must be a **direct alias** (``from apexbot._ffi import PyX as X``), not a
subclass or Python wrapper. The Rust engine constructs and consumes these
pyclasses/pyfunctions directly and driver code passes the instances back to
Rust, so a subclass/wrapper re-export would break type identity at the Rust
FFI boundary. For exceptions, the same is true for ``except``: matching —
Rust raises the exact ``#[pyclass]`` type, so a subclass re-export would
silently break the catch in policy/driver code.

This module replaces the per-feature reexport-identity test family with one
parametrized table. Each row asserts the companion attr ``is`` the FFI attr
named by ``(companion_module, companion_attr, ffi_module, ffi_attr)``.
Rows that formerly compared a name imported from a single module against
itself (true tautologies) were deleted, not migrated; the rows below were
each verified to compare symbols from two different modules.

Pinned by this table:
- ``apexbot.dispatch`` (dispatch/sim/submission seams)
- ``apexbot.updater`` (updater/cancel/db seams)
- ``apexbot.exceptions`` (verification/arbitrage exception seams)
- ``apexbot.types`` (dex-identity seam)
- ``apexbot.chainlink`` / ``apexbot.aave`` (price seam)
- ``apexbot.uniswap.math`` / ``apexbot.aerodrome.math`` (v2-math re-export seam)
"""

from __future__ import annotations

import importlib

import pytest

import apexbot.dispatch

# Module aliases keep each table row on a single line.
_DISPATCH = "apexbot.dispatch"
_SIM = "apexbot._ffi.simulation"
_SUBMIT = "apexbot._ffi.submission"
_UPDATER = "apexbot.updater"
_CANCEL = "apexbot._ffi.cancel"
_DB = "apexbot._ffi.db"
_EXCEPTIONS = "apexbot.exceptions"
_VERIF = "apexbot.exceptions.verification"
_ARBITRAGE = "apexbot.exceptions.arbitrage"
_TYPES = "apexbot.types"
_DEX_ID = "apexbot._ffi.dex_identity"
_CHAINLINK = "apexbot.chainlink"
_AAVE = "apexbot.aave"
_PRICE = "apexbot._ffi.price"
_UNI_MATH = "apexbot.uniswap.math"
_AERO_MATH = "apexbot.aerodrome.math"
_V2_MATH = "apexbot._ffi.v2_math"


# Each row: companion_module, companion_attr, ffi_module, ffi_attr
ALIAS_TABLE: list[tuple[str, str, str, str]] = [
    # apexbot.dispatch — simulation seam
    (_DISPATCH, "CandidateAssembly", _SIM, "CandidateAssembly"),
    (_DISPATCH, "DispatchCandidate", _SIM, "DispatchCandidate"),
    (_DISPATCH, "assemble_dispatch_candidates", _SIM, "assemble_dispatch_candidates_py"),
    (_DISPATCH, "build_batch_executor", _SIM, "build_batch_executor_py"),
    (_DISPATCH, "DispatchOutcome", _SIM, "DispatchOutcome"),
    (_DISPATCH, "SimulateContext", _SIM, "SimulateContext"),
    (_DISPATCH, "PayloadOutcome", _SIM, "PayloadOutcome"),
    (_DISPATCH, "PayloadVerdict", _SIM, "PayloadVerdict"),
    (_DISPATCH, "dispatch_profitable", _SIM, "dispatch_profitable_py"),
    (_DISPATCH, "merge_payload_results", _SIM, "merge_payload_results_py"),
    # apexbot.dispatch — submission seam
    # dispatch_and_submit is deliberately NOT pinned here: it is the one
    # non-alias on the seam, a thin async wrapper decoding the leaf's record
    # dicts into the typed records of apexbot.dispatch.records (behavior is
    # pinned by tests/dispatch/test_submit_records.py).
    (_DISPATCH, "Dispatcher", _SUBMIT, "Dispatcher"),
    (_DISPATCH, "SimSubmitPipeline", _SUBMIT, "SimSubmitPipeline"),
    (_DISPATCH, "TxSigner", _SUBMIT, "TxSigner"),
    (_DISPATCH, "fetch_fee_history", _SUBMIT, "fetch_fee_history_py"),
    # apexbot.updater
    (_UPDATER, "CancelHandle", _CANCEL, "CancelHandle"),
    (_UPDATER, "LiquidityUpdateEvent", _DB, "LiquidityUpdateEvent"),
    (_UPDATER, "V2PoolRowInput", _DB, "V2PoolRowInput"),
    (_UPDATER, "V3PoolRowInput", _DB, "V3PoolRowInput"),
    (_UPDATER, "V4PoolRowInput", _DB, "V4PoolRowInput"),
    # apexbot.exceptions — the companion root must alias the seam submodules
    (_EXCEPTIONS, "VerificationRpcError", _VERIF, "VerificationRpcError"),
    (_EXCEPTIONS, "VerificationMismatchError", _VERIF, "VerificationMismatchError"),
    (_EXCEPTIONS, "HookedPoolRejectedError", _ARBITRAGE, "HookedPoolRejectedError"),
    (_EXCEPTIONS, "DynamicFeePoolRejectedError", _ARBITRAGE, "DynamicFeePoolRejectedError"),
    # apexbot.types — dex identity
    (_TYPES, "DexIdentity", _DEX_ID, "DexIdentity"),
    (_TYPES, "dex_identity", _DEX_ID, "dex_identity"),
    # price seam
    (_CHAINLINK, "ChainlinkPriceFeed", _PRICE, "ChainlinkPriceFeed"),
    (_AAVE, "AavePriceOracle", _PRICE, "AavePriceOracle"),
    # v2-math reexports
    (_UNI_MATH, "calc_exact_in_v2", _V2_MATH, "calc_exact_in_v2"),
    (_UNI_MATH, "calc_exact_out_v2", _V2_MATH, "calc_exact_out_v2"),
    (_AERO_MATH, "calc_exact_out_v2", _V2_MATH, "calc_exact_out_v2"),
]


@pytest.mark.parametrize(
    ("companion_module", "companion_attr", "ffi_module", "ffi_attr"),
    ALIAS_TABLE,
)
def test_companion_alias_is_ffi_symbol(
    companion_module: str,
    companion_attr: str,
    ffi_module: str,
    ffi_attr: str,
) -> None:
    """The companion re-export is the exact FFI symbol, not a subclass."""

    companion = getattr(importlib.import_module(companion_module), companion_attr)
    ffi = getattr(importlib.import_module(ffi_module), ffi_attr)

    assert companion is ffi, (
        f"{companion_module}.{companion_attr} is not the exact FFI symbol "
        f"{ffi_module}.{ffi_attr} — a subclass/wrapper re-export breaks type "
        "identity at the Rust FFI boundary"
    )


def test_dispatch_all_pins_public_surface() -> None:
    """Every stable dispatch name is exported from ``apexbot.dispatch``.

    ``SubmitCandidate`` joined the surface with the inline-sim seam
    (SIMPIPE2 T3): the runner builds submit records from payload batches,
    so it is a public name alongside the FFI leaf wrappers. Added
    the payload seam (``merge_payload_results`` + the two pyclasses) when
    the payload arm started routing through the same Rust sim join.
    """

    d = apexbot.dispatch
    expected = {
        "AssemblyVerdict",
        "BatchExecutor",
        "BatchOutcome",
        "BatchOutcomeSet",
        "CandidateAssembly",
        "DispatchCandidate",
        "DispatchOutcome",
        "Dispatcher",
        "FailureDetail",
        "FailureKind",
        "PayloadOutcome",
        "PayloadVerdict",
        "SimReceipt",
        "SimSubmitPipeline",
        "SimulateContext",
        "SimulateVerdict",
        "SkippedRecord",
        "SubmitCandidate",
        "SubmitContext",
        "SubmitRecord",
        "SubmitSkipReason",
        "SubmitVerdict",
        "SubmittedRecord",
        "TxSigner",
        "assemble_dispatch_candidates",
        "build_batch_executor",
        "dispatch_and_submit",
        "dispatch_profitable",
        "fetch_fee_history",
        "merge_payload_results",
        "typed_submit_record",
    }
    assert expected.issubset(set(dir(d)))
    assert expected == set(d.__all__)


def test_rust_raised_exception_is_caught_by_companion_alias() -> None:
    """An instance the Rust pyclass raises is catchable by the companion name.

    The core retry classification raises ``VerificationRpcError`` through the
    ``apexbot._ffi.VerificationRpcError`` pyclass, while the driver shell
    catches the companion name. The alias makes those the same type so
    ``except`` matches; the raise here goes through the FFI symbol and the
    catch through the companion symbol to pin the cross-module contract.
    """
    from apexbot._ffi import VerificationRpcError as FfiVerificationRpcError
    from apexbot.exceptions import VerificationRpcError

    msg = "transport blip"
    with pytest.raises(VerificationRpcError) as caught:
        raise FfiVerificationRpcError(msg)

    assert "transport blip" in str(caught.value)
