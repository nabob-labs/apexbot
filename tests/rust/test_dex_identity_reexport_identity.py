"""Companion-layer re-export of the Rust DexIdentity FFI pyclass.

The three-layer architecture (ADR-005) requires that driver / test code
import the DEX-identity pyclass from the companion package ``apexbot.types``
— not from the PyO3 wrapper ``apexbot._ffi``. The ``Py*`` prefix is the FFI
seam naming itself; it should never appear in driver code.

This re-export must be a **direct alias** (``from apexbot._ffi import
DexIdentity as DexIdentity``), not a Python subclass — the Rust engine
constructs and consumes this pyclass directly; subclassing would break type
identity at the FFI boundary.
"""

from __future__ import annotations


def test_dex_identity_alias_identity() -> None:
    """The stable companion name is the exact FFI pyclass."""
    from apexbot.types import DexIdentity

    assert DexIdentity is DexIdentity


def test_dex_identity_factory_alias_identity() -> None:
    """The stable companion ``dex_identity`` factory is the exact FFI function."""
    from apexbot._ffi.dex_identity import dex_identity as ffi_dex_identity
    from apexbot.types import dex_identity

    assert dex_identity is ffi_dex_identity
