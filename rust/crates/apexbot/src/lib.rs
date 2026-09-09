/// The whole `apexbot-core` crate (errors, hex, EIP-55, runtime, EIP-1559).
pub use apexbot_config as config;
pub use apexbot_core as core;
/// Foundational utilities — errors, hex, EIP-55 addresses, shared runtime.
pub use apexbot_core::{address_utils, errors, hex_utils, runtime};

/// `examples/path*_solver_fixture.rs` investigate-runner dialect.
pub mod investigation;

/// The per-chain state owner + the unified multi-DEX arb engine (`bot_core`,
/// `arb_engine`); the stateless solver math lives in [`crate::solvers`].
pub use apexbot_bot as bot;
/// `BotState` state-owner surface, re-exported alongside [`crate::bot`].
pub use apexbot_bot::bot_core;
/// WS ingestion (subscriptions, topic filter, backfill fetch, watchdog
/// windows) emitting `PoolEvent` into the runtime — the standalone-Rust
/// consumer subscribes to its event stream without Python (MROOY7).
pub use apexbot_ingestion as ingestion;
/// traits (ADR-005 standalone-by-design pool value/trait layer).
pub use apexbot_pools as pools;

/// Pathfinding graph (`PathGraph`) + edge graph.
pub use apexbot_pathfinding as pathfinding;

/// Stateless solver math (Möbius composition, V3/V4 tick solving, the
/// `QuantAMM` Balancer basket solver) — relocated from `apexbot-bot` (ADR-015).
pub use apexbot_solvers as solvers;

/// The whole `apexbot-uniswap` crate (dex identity + V2 encoding + registry).
pub use apexbot_uniswap as uniswap;
/// value objects + `pub const` per-DEX presets, and the V2 swap-call encoder.
pub use apexbot_uniswap::{dex_identity, v2_encoding};

/// Uniswap V2/V3/V4 event-log decoders (alloy-only leaf).
pub use apexbot_decoders as decoders;

/// family modules, byte-verified against canonical sources by the tier-3 oracles.
pub use apexbot_math as math;

/// EIP-1559 base-fee math.
pub use apexbot_core::eip_1559;

/// `apexbot-rpc` `eth_call` (pyo3-free leaf).
pub use apexbot_price as price;

/// cmd-executor domain — simulation warmup-slot storage math (pure-Rust leaf).
pub use apexbot_executor as cmd_executor;

/// here; `apexbot-arbitrage` implements it as the default adapter.
pub use apexbot_execution as execution;
/// pending-tx receipt monitor (pure-Rust leaf).
pub use apexbot_submission as submission;

/// test/diagnostic Rust surface — deliberately no FFI exposure.
pub use apexbot_simulation as simulation;

/// co-implementation).
pub use apexbot_arbitrage as arbitrage;

/// consumer by this crate (B5L2XA).
pub use apexbot_order_index as order_index;

/// ABI encode/decode (`decoder`, `encoder`).
pub use apexbot_abi as abi;

/// optional feature the umbrella never enables).
pub use apexbot_rpc as rpc;

/// feature).
pub use apexbot_db as db;

/// `cargo add apexbot` consumer runs `run_aave_update` with no Python.
pub use apexbot_aave as aave;

/// in `$PATH` at runtime).
pub use apexbot_fork as fork;

/// Standalone-Rust core mirroring the Aave updater shape.
pub use apexbot_pool_updater as pool_updater;

// ---------------------------------------------------------------------------
// ---------------------------------------------------------------------------

pub use apexbot_bot::bot_core::pool_builder::builder::{
    build_aerodrome_v2, build_balancer_stable, build_balancer_weighted, build_curve_pool,
    build_erc20_metadata, build_v2, build_v3, build_v4, probe_pool_type, resolve_v4_identity,
    PoolBuilderError, PoolFamily, V4BuildResult, V4PoolBuildIdentity, V4PoolBuildOverrides,
};
pub use apexbot_bot::bot_core::registration_lifecycle::{
    run_cl_v3_lifecycle, run_cl_v4_lifecycle, run_v3_registration_lifecycle,
    run_v4_registration_lifecycle, RegistrationLifecycleError,
};
pub use apexbot_bot::bot_core::{
    BotState, PoolEntry, RegisterAerodromeV2PoolParams, RegisterCurvePoolParams,
    RegisterV2PoolParams, RegisterV3PoolParams, RegisterV4PoolParams, V2PoolState, V4PoolKey,
};
pub use apexbot_uniswap::dex_identity::{
    preset_for_variant, DexIdentity, DexVariant, ReservesAbi, UNISWAP_V2,
};
