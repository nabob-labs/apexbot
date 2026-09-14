//! Acceptance criterion: the loader's schema covers the FULL `APEXBOT_*`
//! key inventory. This test diffs the raw inventory sweep (`rg -o
//! "APEXBOT_[A-Z_]+" rust/crates --no-filename | sort -u`) against the
//! schema's env names, with the documented artifact/expansion set below.

use std::collections::BTreeSet;
use std::path::Path;
use std::process::Command;

use apexbot_config::SCHEMA;

/// Raw regex matches that are NOT real static keys:
/// - `APEXBOT_JAEGER_E` — the sweep regex stops at the digit of `APEXBOT_JAEGER_E2E`.
/// - `APEXBOT_V` — the regex stops at the `3` of `APEXBOT_V3_FIXTURE_*`.
/// - `APEXBOT_RPC_WS_CHAINID_` — trailing `_` of the DYNAMIC per-chain var
///   `APEXBOT_RPC_WS_CHAINID_<chain_id>` (documented next to `SCHEMA`).
const SWEEP_ARTIFACTS: &[&str] = &[
    "APEXBOT_JAEGER_E",
    // KAHU5W: the family wildcard in the allocator doc comment (the loader
    // owns the four concrete APEXBOT_MIMALLOC_* keys).
    "APEXBOT_MIMALLOC_",
    "APEXBOT_RPC_WS_CHAINID_",
    // JLFE2F: the family wildcard named by the retired-layout refusal text
    // in the loader (the dynamic per-chain var
    // APEXBOT_RPC_HTTP_CHAINID_<chain_id>).
    "APEXBOT_RPC_HTTP_CHAINID_",
    "APEXBOT_V",
];

/// Build-receipt keys (commit 1e1c0ddf7): compile-time build-artifact
/// variables around `apexbot-python/build.rs` — `APEXBOT_BUILD_NUMBER_FILE`
/// locates the receipt file at build time, and `APEXBOT_BUILD_NUMBER` /
/// `APEXBOT_BUILD_FINGERPRINT` are `cargo:rustc-env` outputs consumed by
/// `build_info`. They are not runtime configuration keys.
const BUILD_ARTIFACT_KEYS: &[&str] = &[
    "APEXBOT_BUILD_FINGERPRINT",
    "APEXBOT_BUILD_NUMBER",
    "APEXBOT_BUILD_NUMBER_FILE",
];

/// Real static env keys the config crate reads BEFORE/OUTSIDE the schema:
/// `APEXBOT_CONFIG` selects the config FILE layer (see
/// `with_standard_file_paths` in `loader.rs`) — chicken-and-egg, it cannot
/// be an option inside the file it locates, so it is deliberately NOT a
/// schema key.
const BOOTSTRAP_KEYS: &[&str] = &["APEXBOT_CONFIG"];

/// RETIRED keys the loader guards for one release (P6YXA6 hard cutover):
/// they fail the load loudly and point at the replacement rather than
/// silently falling back — the deprecation-style hard error. They are not
/// schema keys anymore; the guard lives in the env layer of `loader.rs`.
const RETIRED_KEYS: &[&str] = &[
    "APEXBOT_LPT_PARTITION",
    "APEXBOT_SOLVE_EXECUTOR",
    "APEXBOT_FLEET",
    "APEXBOT_SOLVE_SIM_INFLIGHT",
    "APEXBOT_DETACHED_SOLVES",
];

/// Real static keys the artifact regex cannot capture (digit-terminated
/// matches expand to these full names).
const SWEEP_EXPANSIONS: &[&str] = &[
    "APEXBOT_JAEGER_E2E",
    // KAHU5W: the V2 in APEXBOT_V2_CALC_TRACE ends the artifact match.
    "APEXBOT_V2_CALC_TRACE",
    "APEXBOT_V3_FIXTURE_RPC",
    "APEXBOT_V3_FIXTURE_BLOCK",
];

/// Committed snapshot of the sweep, used verbatim when `rg` is not installed
/// (standalone-consumer checkouts). Refresh in-repo with:
/// `rg -o 'APEXBOT_[A-Z_]+' rust/crates --no-filename −g '!**/apexbot_env_inventory.txt' | sort -u > <snapshot>`
const SNAPSHOT: &str = include_str!("apexbot_env_inventory.txt");

fn repo_root() -> &'static Path {
    let Some(root) = Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(3) else {
        unreachable!("repo root is three levels above the crate manifest dir");
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

#[test]
fn schema_covers_the_full_key_inventory() {
    let sweep: BTreeSet<String> = inventory().into_iter().collect();
    assert!(!sweep.is_empty(), "inventory sweep produced no keys");

    let mut expected: BTreeSet<String> = sweep
        .iter()
        .filter(|k| {
            !SWEEP_ARTIFACTS.contains(&k.as_str())
                && !BOOTSTRAP_KEYS.contains(&k.as_str())
                && !BUILD_ARTIFACT_KEYS.contains(&k.as_str())
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

    let actual: BTreeSet<String> = SCHEMA.iter().map(|k| k.env.to_string()).collect();

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
    let mut expected: BTreeSet<String> = sweep
        .iter()
        .filter(|k| {
            !SWEEP_ARTIFACTS.contains(&k.as_str())
                && !BOOTSTRAP_KEYS.contains(&k.as_str())
                && !BUILD_ARTIFACT_KEYS.contains(&k.as_str())
                && !RETIRED_KEYS.contains(&k.as_str())
        })
        .cloned()
        .collect();
    for expansion in SWEEP_EXPANSIONS {
        let _ = expected.insert((*expansion).to_string());
    }
    let actual: BTreeSet<String> = SCHEMA.iter().map(|k| k.env.to_string()).collect();
    assert_eq!(actual, expected);
}
