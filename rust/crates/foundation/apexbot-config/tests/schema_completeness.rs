//! Acceptance criterion: the loader's schema covers the FULL `APEXBOT_*`
//! key inventory. This test diffs the raw inventory sweep (`rg -o
//! "APEXBOT_[A-Z_]+" rust/crates --no-filename | sort -u`) against the
//! schema's env names, with the documented artifact/expansion set below.

use std::collections::BTreeSet;
use std::path::Path;
use std::process::Command;

use apexbot_config::{SCHEMA, UNPREFIXED_ENV_NAMES};

/// Raw regex matches that are NOT real static keys:
/// - `APEXBOT_JAEGER_E` — the sweep regex stops at the digit of `APEXBOT_JAEGER_E2E`.
/// - `APEXBOT_V` — the regex stops at the `3` of `APEXBOT_V3_FIXTURE_*`.
/// - `APEXBOT_RPC_WS_CHAINID_` — trailing `_` of the DYNAMIC per-chain var
///   `APEXBOT_RPC_WS_CHAINID_<chain_id>` (documented next to `SCHEMA`).
const SWEEP_ARTIFACTS: &[&str] = &[
    "APEXBOT_JAEGER_E",
    // the sweep regex stops at the digit of the dispatch profit-capture
    // stance's env name (see SWEEP_EXPANSIONS).
    "APEXBOT_ERC",
    // the family wildcard in the allocator doc comment (the loader
    // owns the four concrete APEXBOT_MIMALLOC_* keys).
    "APEXBOT_MIMALLOC_",
    "APEXBOT_V",
    // the family wildcards in the facet-invariant tests' prefix assertions
    // (the schema owns the concrete per-ecosystem backrun keys).
    "APEXBOT_STRATEGY_MEVBLOCKER_BACKRUN_",
    "APEXBOT_STRATEGY_TXPOOL_BACKRUN_",
    // ADR-051 D8: the family wildcard in the cli-core operator doc comment
    // (the loader owns the four concrete APEXBOT_FLEET_CORDON_* keys).
    "APEXBOT_FLEET_CORDON_",
    // ADR-062: the family wildcard in the capture-recapture example's doc
    // comment (the schema owns the concrete APEXBOT_RPC_*_CHAINID_<id>
    // keys and the loader owns their per-chain expansion).
    "APEXBOT_RPC_",
    // The retired click per-flag envvar fallback named in the argv doc
    // comment; the console models these inputs as argv only.
    "APEXBOT_CHUNK_SIZE",
];

/// Real static env keys the config crate reads BEFORE/OUTSIDE the schema:
/// `APEXBOT_CONFIG` selects the config FILE layer (see
/// `with_standard_file_paths` in `loader.rs`) — chicken-and-egg, it cannot
/// be an option inside the file it locates, so it is deliberately NOT a
/// schema key.
const BOOTSTRAP_KEYS: &[&str] = &["APEXBOT_CONFIG"];

/// Shell-environment inputs resolved outside the typed schema: the
/// operator-socket override, a console input resolved by cli-core's
/// `resolve_socket` cascade (ADR-051 D8). The per-chain RPC families, the
/// session chain id, and the database path are NOT here: ADR-062 D1/D2/D4
/// declared them, so the file layer and these env names are one cascade.
const DRIVER_DOMAIN_KEYS: &[&str] = &["APEXBOT_OPERATOR_SOCKET"];

/// RETIRED keys the loader guards for one release (P6YXA6 hard cutover):
/// they fail the load loudly and point at the replacement rather than
/// silently falling back — the deprecation-style hard error. They are not
/// schema keys anymore; the guard lives in the env layer of `loader.rs`.
/// Test-harness knobs (live fixtures + guards): these steer the replay
/// test tiers (fixture block pins, scan windows, trace toggles) and the
/// classifier panic-guard — they change which STATIC inputs a test sees,
/// never runtime configuration, so they are deliberately NOT schema keys.
const TEST_HARNESS_KEYS: &[&str] = &[
    // The pathfinding snapshot bench's fixture-path override
    // (`apexbot-db/benches/sweep_snapshot.rs`): selects which static DB the
    // bench opens, the same class as the offline parity-fixture dirs.
    "APEXBOT_SNAPSHOT_DB",
    "APEXBOT_CLASSIFIER_GUARD",
    "APEXBOT_FRAME_ORACLE_CAPTURE",
    "APEXBOT_ORACLE_",
    "APEXBOT_ORACLE_SCAN_BLOCKS",
    "APEXBOT_ORACLE_TRACE",
    "APEXBOT_PARITY_BLOCK",
];

const RETIRED_KEYS: &[&str] = &[
    "APEXBOT_LPT_PARTITION",
    "APEXBOT_SOLVE_EXECUTOR",
    "APEXBOT_FLEET",
    "APEXBOT_SOLVE_SIM_INFLIGHT",
    "APEXBOT_DETACHED_SOLVES",
    // ADR-043 §5 retired verbosity flags. These literals live in
    // `apexbot_core::telemetry::RETIRED_ENV_NAMES` (the boot-time detection
    // list) because the scanner sweeps the crates; the names are detected and
    // warned about, never honored.
    "APEXBOT_VERIFY_DBG",
    "APEXBOT_V2_CALC_TRACE",
    "APEXBOT_SIM_LOG_REVERTED_SWAPS",
    "APEXBOT_SIM_DIVERGENCE_LOG",
    "APEXBOT_DUMP_CALL_TRACE",
    "APEXBOT_DUMP_TICK_MAPS",
    "APEXBOT_WS_TRACE",
    "APEXBOT_DRAIN_DBG",
    "APEXBOT_TRACE_DISPATCH",
    "APEXBOT_TRACE_REGISTER_SEED",
    "APEXBOT_TRACE_LIQUIDITY",
    "APEXBOT_TRACE_TICK",
    "APEXBOT_GATE_TRACE",
    "APEXBOT_AAVE_EVTRACE",
    "APEXBOT_AAVE_TX_TRACE",
    // ADR-043 §6: the retired stderr-fmt two-tunnel switch.
    "APEXBOT_LOG_FMT",
];

/// Real static keys the artifact regex cannot capture (digit-terminated
/// matches expand to these full names).
const SWEEP_EXPANSIONS: &[&str] = &[
    "APEXBOT_JAEGER_E2E",
    "APEXBOT_ERC6909_PROFIT",
    "APEXBOT_V3_FIXTURE_RPC",
    "APEXBOT_V3_FIXTURE_BLOCK",
];

/// Committed snapshot of the sweep, used verbatim when `rg` is not installed
/// (standalone-consumer checkouts). Refresh in-repo with:
/// `rg -o 'APEXBOT_[A-Z_]+' rust/crates --no-filename −g '!**/apexbot_env_inventory.txt' | sort -u > <snapshot>`
const SNAPSHOT: &str = include_str!("apexbot_env_inventory.txt");

fn repo_root() -> &'static Path {
    let Some(root) = Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(4) else {
        unreachable!("repo root is four levels above the role-grouped crate manifest dir");
    };
    root
}

/// Prefer the live sweep; fall back to the committed snapshot.
fn inventory() -> Vec<String> {
    let live = Command::new("rg")
        .args([
            "-o",
            "APEXBOT_[A-Z_]+",
            "rust/crates",
            "--no-filename",
            "-g",
            "!**/apexbot_env_inventory.txt",
            "-g",
            "!**/apexbot-config/tests/**",
        ])
        .current_dir(repo_root())
        .output();
    match live {
        Ok(out) if out.status.success() && !out.stdout.is_empty() => {
            String::from_utf8_lossy(&out.stdout)
                .lines()
                .map(str::to_string)
                .collect()
        }
        // `rg` unavailable or produced nothing: use the committed snapshot.
        _ => SNAPSHOT.lines().map(str::to_string).collect(),
    }
}

/// Every `APEXBOT_*` name the schema declares: the one set an inventory
/// sweep can produce. A declared name that predates the prefix is filtered by
/// the schema's own named exception list rather than by a second copy of it
/// here, so a key added to that list cannot pass this gate by being forgotten
/// in two places.
fn declared_prefixed_names() -> BTreeSet<String> {
    SCHEMA
        .iter()
        .map(|k| k.env.to_string())
        .filter(|env| !UNPREFIXED_ENV_NAMES.contains(&env.as_str()))
        .collect()
}

#[test]
fn schema_covers_the_full_key_inventory() {
    let sweep: BTreeSet<String> = inventory().into_iter().collect();
    assert!(!sweep.is_empty(), "inventory sweep produced no keys");

    let mut expected: BTreeSet<String> = sweep
        .iter()
        .filter(|k| {
            !SWEEP_ARTIFACTS.contains(&k.as_str())
                && !BOOTSTRAP_KEYS.contains(&k.as_str())
                && !DRIVER_DOMAIN_KEYS.contains(&k.as_str())
                && !TEST_HARNESS_KEYS.contains(&k.as_str())
                && !RETIRED_KEYS.contains(&k.as_str())
        })
        .cloned()
        .collect();
    for expansion in SWEEP_EXPANSIONS {
        // Only expand when the artifact that produced it was actually
        // observed (keeps the snapshot fallback consistent).
        if SWEEP_ARTIFACTS.iter().any(|a| sweep.contains(*a)) || sweep.contains(*expansion) {
            let _ = expected.insert((*expansion).to_string());
        }
    }

    let actual = declared_prefixed_names();

    let unknown: Vec<_> = actual.difference(&expected).collect();
    let uncovered: Vec<_> = expected.difference(&actual).collect();
    assert!(
        unknown.is_empty() && uncovered.is_empty(),
        "schema/inventory mismatch\n  schema keys not in inventory: {unknown:?}\n  inventory keys not in schema: {uncovered:?}"
    );
}

#[test]
fn snapshot_fallback_agrees_with_schema() {
    // The committed snapshot must itself satisfy the parity contract — this
    // is the standalone-consumer path (no `rg` in the build environment).
    let sweep: BTreeSet<String> = SNAPSHOT.lines().map(str::to_string).collect();
    assert!(
        !sweep.iter().any(|k| k.contains("REGEN_DOCS")),
        "snapshot is self-contaminated; regenerate it with the exclusion glob"
    );
    // This filter chain must mirror `schema_covers_the_full_key_inventory`
    // exactly — the two inventory paths (live sweep, committed snapshot) hold
    // the identical parity contract.
    let mut expected: BTreeSet<String> = sweep
        .iter()
        .filter(|k| {
            !SWEEP_ARTIFACTS.contains(&k.as_str())
                && !BOOTSTRAP_KEYS.contains(&k.as_str())
                && !DRIVER_DOMAIN_KEYS.contains(&k.as_str())
                && !TEST_HARNESS_KEYS.contains(&k.as_str())
                && !RETIRED_KEYS.contains(&k.as_str())
        })
        .cloned()
        .collect();
    for expansion in SWEEP_EXPANSIONS {
        if SWEEP_ARTIFACTS.iter().any(|a| sweep.contains(*a)) || sweep.contains(*expansion) {
            let _ = expected.insert((*expansion).to_string());
        }
    }
    assert_eq!(declared_prefixed_names(), expected);
}
