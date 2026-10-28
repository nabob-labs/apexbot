//! The frozen metric-name parity gate (ADR-083).
//!
//! `instruments.rs` is the one owner of the metric names, and those names are
//! COUPLED verbatim to Grafana dashboards and alert queries (e.g.
//! `apexbot_epoch_header_to_publish_seconds`). This gate pins the closed
//! name set bidirectionally against the construction calls in
//! `instruments.rs`: a rename in code without moving the dashboard + alert
//! consumers fails HERE — the same moment the developer is editing the
//! census, not a silent scrape regression.

use std::path::Path;

/// The frozen `OTel` instrument names `instruments.rs` may construct. Add a
/// name ONLY in the same change that moves every dashboard/alert consumer
/// (see the PROMETHEUS NAME COUPLING notes on the fields).
const FROZEN_NAMES: &[&str] = &[
    "apexbot.backfills.executed",
    "apexbot.backrun.feed.connected",
    "apexbot.backrun.feed.dropped_ring",
    "apexbot.backrun.feed.frames",
    "apexbot.backrun.feed.reconnects",
    "apexbot.backrun.feed.rejected_chain_id",
    "apexbot.backrun.feed.rejected_parse",
    "apexbot.backrun.feed.seconds_since_event",
    "apexbot.backrun.frame.observed",
    "apexbot.block.header_to_first_log",
    "apexbot.block.log_burst",
    "apexbot.block.settle_wait",
    "apexbot.blocks.observed",
    "apexbot.candidates.found",
    "apexbot.cgroup.throttled",
    "apexbot.detached.applied",
    "apexbot.detached.degraded_cycles",
    "apexbot.detached.in_flight",
    "apexbot.detached.leads_expired",
    "apexbot.detached.merge_panic",
    "apexbot.detached.send_failed",
    "apexbot.detached.shed",
    "apexbot.detached.stale_dropped",
    "apexbot.dispatch.gas_used",
    "apexbot.dispatch.gross_profit",
    "apexbot.dispatch.net_profit",
    "apexbot.engine.quarantined_pools",
    "apexbot.engine.registered_paths",
    "apexbot.epoch.header_to_publish",
    "apexbot.epoch.logs_applied",
    "apexbot.epoch.logs_block",
    "apexbot.epoch.logs_ignored",
    "apexbot.epoch.logs_received",
    "apexbot.epoch.logs_seen",
    "apexbot.epoch.stale_drops",
    "apexbot.errors",
    "apexbot.fleet.intake_backlog",
    "apexbot.fleet.profile",
    "apexbot.late_log.admitted",
    "apexbot.log.decode",
    "apexbot.logs.applied",
    "apexbot.logs.apply_missed",
    "apexbot.logs.decoded",
    "apexbot.logs.received",
    "apexbot.logs.undecoded",
    "apexbot.monitor.outcomes",
    "apexbot.process.rss",
    "apexbot.pump.seconds_since_apply",
    "apexbot.pump.seconds_since_header",
    "apexbot.quiesce.window_ms",
    "apexbot.registration.skips",
    "apexbot.reorg.depth_blocks",
    "apexbot.reorg.recovery_dropped",
    "apexbot.reorg.unwound_pools",
    "apexbot.reorg.windows",
    "apexbot.sim.error_reason",
    "apexbot.simulate.duration",
    "apexbot.simulate.verdicts",
    "apexbot.solve.duration",
    "apexbot.solve.gate_duration",
    "apexbot.solve.mutex_hold",
    "apexbot.solve.path_duration",
    "apexbot.solver.clamps",
    "apexbot.solver.walk_memo_cache_plays",
    "apexbot.solver.walk_memo_hits",
    "apexbot.solver.walk_memo_negative_entries",
    "apexbot.solver.walk_memo_negatives_played",
    "apexbot.solver.walk_memo_probes",
    "apexbot.solves.executed",
    "apexbot.stage.publish_cycle",
    "apexbot.stage.rewind",
    "apexbot.stage.rewind_duration",
    "apexbot.stage.streaming_age",
    "apexbot.state.apply",
    "apexbot.state.head_lag_blocks",
    "apexbot.state_lock.hold",
    "apexbot.state_lock.wait",
    "apexbot.submit.latency",
    "apexbot.submit.outcomes",
    "apexbot.updater.rpc_round_trips",
    "apexbot.updater.stage.duration",
    "apexbot.updater.write_lock_hold",
    "apexbot.updater.write_lock_hold_last",
    "apexbot.worker.census",
    "apexbot.ws.logs.seen",
];

fn instruments_source() -> String {
    let path = Path::new(env!("CARGO_MANIFEST_DIR")).join("src/instruments.rs");
    #[expect(clippy::expect_used)] // the census module's source is part of the crate
    std::fs::read_to_string(path).expect("instruments.rs is readable")
}

/// Every instrument constructed in `instruments.rs` is in the frozen set.
#[test]
fn every_constructed_name_is_frozen() {
    let source = instruments_source();
    let mut constructed: Vec<&str> = Vec::new();
    for ctor in [
        "f64_histogram(\"",
        "u64_counter(\"",
        "f64_gauge(\"",
        "u64_gauge(\"",
        "u64_histogram(\"",
    ] {
        let mut rest = source.as_str();
        while let Some(idx) = rest.find(ctor) {
            let after = &rest[idx + ctor.len()..];
            if let Some(end) = after.find('"') {
                constructed.push(&after[..end]);
                rest = &after[end..];
            } else {
                break;
            }
        }
    }
    let mut unnamed: Vec<&str> = constructed
        .iter()
        .copied()
        .filter(|name| !FROZEN_NAMES.contains(name))
        .collect();
    unnamed.sort_unstable();
    unnamed.dedup();
    assert!(
        unnamed.is_empty(),
        "instrument names constructed but not frozen (move the dashboard + \n  alert consumers in the SAME change): {unnamed:?}"
    );
}

/// Every frozen name is actually constructed — a stale frozen row is a lie
/// about the census (and a dashboard querying a retired metric).
#[test]
fn every_frozen_name_is_constructed() {
    let source = instruments_source();
    let missing: Vec<&str> = FROZEN_NAMES
        .iter()
        .copied()
        .filter(|name| !source.contains(&format!("\"{name}\"")))
        .collect();
    assert!(
        missing.is_empty(),
        "frozen names no longer constructed (retire the row AND its dashboard \n  consumers): {missing:?}"
    );
}
