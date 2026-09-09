"""Companion-layer re-exports of Rust updater + database FFI pyclasses.

The three-layer architecture (ADR-005) requires that driver / CLI code import
updater input pyclasses from the companion package ``apexbot.updater`` — not
from the PyO3 wrapper ``apexbot._ffi``.

These re-exports must be **direct aliases**, not Python subclasses — the Rust
engine constructs and consumes these pyclasses directly; subclassing would
break type identity at the FFI boundary.
"""

from __future__ import annotations

from apexbot._ffi.cancel import CancelHandle
from apexbot._ffi.db import (
    LiquidityUpdateEvent,
    V2PoolRowInput,
    V3PoolRowInput,
    V4PoolRowInput,
)
from apexbot.exceptions import DatabaseSchemaStale


def test_cancel_handle_alias() -> None:
    from apexbot.updater import CancelHandle as CompanionCancelHandle

    assert CompanionCancelHandle is CancelHandle


def test_liquidity_update_event_alias() -> None:
    from apexbot.updater import LiquidityUpdateEvent as CompanionLiquidityUpdateEvent

    assert CompanionLiquidityUpdateEvent is LiquidityUpdateEvent


def test_v2_pool_row_input_alias() -> None:
    from apexbot.updater import V2PoolRowInput as CompanionV2PoolRowInput

    assert CompanionV2PoolRowInput is V2PoolRowInput


def test_v3_pool_row_input_alias() -> None:
    from apexbot.updater import V3PoolRowInput as CompanionV3PoolRowInput

    assert CompanionV3PoolRowInput is V3PoolRowInput


def test_v4_pool_row_input_alias() -> None:
    from apexbot.updater import V4PoolRowInput as CompanionV4PoolRowInput

    assert CompanionV4PoolRowInput is V4PoolRowInput


def test_database_schema_stale_alias() -> None:
    """DatabaseSchemaStale is the exact Rust-raised type under apexbot.exceptions.

    ``apexbot.db`` no longer re-exports it (4JASRW) — identity is asserted
    against the physical ``apexbot._ffi.db`` home.
    """
    from apexbot._ffi.db import DatabaseSchemaStale as FfiDatabaseSchemaStale

    assert DatabaseSchemaStale is FfiDatabaseSchemaStale
