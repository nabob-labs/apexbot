"""Rust-backed database row types + operations — the stable mirror home for ``_ffi.db``.

Re-exports the Rust-backed database surface from the ``apexbot._ffi.db``
submodule. Importers should use::

    from apexbot.db import db_backup_database

    (the pool-updater row-input/event types now live exclusively in
    ``apexbot.updater``)

rather than reaching into ``apexbot._ffi`` directly — this path is stable
across future Rust reshuffles, and lets the Rust crate structure
(``apexbot-db``) show through to Python.

The functions are thin PyO3 wrappers over the pure-Rust ``apexbot-db``
core crate; the ``db_`` prefix is retained on the submodule names (unlike
the math submodules which dropped their prefix) because ``db_`` is a clear
functional namespace marker for the ~45 database operations.

The classes are ADR-005 ``Py*`` aliases / ``*Row``/``*RowInput`` types.

This is the sole Python database mirror: it owns the Rust-backed row types and
operations, while the pure-Rust ``apexbot-db`` crate owns the schema and
upgrades it at open (ADR-052).
"""

from apexbot._ffi import Erc20TokenRow
from apexbot._ffi.db import (
    CollateralPositionData,
    DatabasePositionQuery,
    DatabaseSnapshot,
    DebtPositionData,
    DiscoveryPoolRow,
    ExchangeRow,
    LiquidityPoolRow,
    PoolManagerRow,
    UserPositionSummary,
    analyze_aave_user_position,
    db_apply_v3_liquidity_updates,
    db_apply_v4_liquidity_updates,
    db_backup_database,
    db_compact_database,
    db_fetch_discovery_rows,
    db_fetch_exchange,
    db_fetch_exchange_by_name,
    db_fetch_graph_edition,
    db_fetch_pool_row,
    db_heal_database,
    db_inspect_schema_state,
    db_resolve_token_ids,
    db_schema_version,
    db_set_exchange_active,
    db_set_exchange_last_update_block,
    db_upgrade_database,
    db_upsert_exchange,
    db_upsert_pool_manager,
    db_upsert_v2_pools,
    db_upsert_v3_pools,
    db_upsert_v4_pools,
)

__all__ = [
    "CollateralPositionData",
    "DatabasePositionQuery",
    "DatabaseSnapshot",
    "DebtPositionData",
    "DiscoveryPoolRow",
    "Erc20TokenRow",
    "ExchangeRow",
    "LiquidityPoolRow",
    "PoolManagerRow",
    "UserPositionSummary",
    "analyze_aave_user_position",
    "db_apply_v3_liquidity_updates",
    "db_apply_v4_liquidity_updates",
    "db_backup_database",
    "db_compact_database",
    "db_fetch_discovery_rows",
    "db_fetch_exchange",
    "db_fetch_exchange_by_name",
    "db_fetch_graph_edition",
    "db_fetch_pool_row",
    "db_heal_database",
    "db_inspect_schema_state",
    "db_resolve_token_ids",
    "db_schema_version",
    "db_set_exchange_active",
    "db_set_exchange_last_update_block",
    "db_upgrade_database",
    "db_upsert_exchange",
    "db_upsert_pool_manager",
    "db_upsert_v2_pools",
    "db_upsert_v3_pools",
    "db_upsert_v4_pools",
]
