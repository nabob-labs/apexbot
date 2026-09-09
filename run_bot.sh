#!/usr/bin/env bash
# Drive the settlement-arbitrage bot with all output teed to a log file.
#
# A self-contained launcher so the bot can be started/stopped deterministically
# without rediscovering the launch mechanics each time.
#
#   ./run_bot.sh            # foreground (output -> console + log)
#   ./run_bot.sh start      # detached (setsid), pid -> logs/bot_run.pid
#   ./run_bot.sh stop       # kill the running bot (by pidfile + pkill)
#   ./run_bot.sh status     # is it running?
set -u
cd /workspaces/apexbot
LOGDIR=/workspaces/apexbot/logs
LOG="$LOGDIR/bot_run.log"
PIDFILE="$LOGDIR/bot_run.pid"
mkdir -p "$LOGDIR"

# --------------------------------------------------------------------------
# Conservative (HARD/LOUD) defaults now live in the CODE, not here (Z4KQXF).
# Every invocation — run_bot.sh, a hand-run, a CI/harness — gets loud failure
# by default; there is no liberal default posture anymore. Flags that follow
# are all default-ON in code via `bot_env_flag_default_on` (opt OUT with =0):
#   (RETIRED: APEXBOT_ASSERT_SOLVER_STATE — the ADR-021 per-solve solver-state
#     tripwire is GONE with MROOY7 task 2UVG3E and the key no longer exists in
#     the config schema (docs/rust-config-keys.md). Standing verification is
#     on-demand: sim failures arm a divergence probe (APEXBOT_SIM_DIVERGENCE_LOG)
#     and APEXBOT_VERIFY_SPOTCHECK_PERMYRIAD adds random ops spot-checks.)
#   APEXBOT_VERIFY_DBG          (structural verify diagnostics / divergence set)
#   APEXBOT_DUMP_CALL_TRACE     (full revm call trace on sim failure)
#   APEXBOT_V2_CALC_TRACE       (V2 reserves slot8 before each sim)
#   APEXBOT_SIM_LOG_REVERTED_SWAPS (per-hop actual-vs-predicted on revert)
#   APEXBOT_SIM_EXIT_ON_FAIL  (stop on first sim failure) - see below: this
#     script DEFAULTS it to 0; failing sims are identified via OTel traces.
#   APEXBOT_WS_COMPLETENESS    (per-block eth_getLogs vs WS delivery cross-
#     check; NEW default-ON since B4GX7C, so a live WS log drop aborts loudly)
# Script-defaulted high-noise traces (set =0 to opt out; the Rust gate is
# presence-gated on "1"/"true", so these are OFF in hand-runs by default):
#   APEXBOT_WS_TRACE           # [trace] ws-log for EVERY relevant-topic WS
#     log with block/log_index/tx_index/topic0/removed/decision — high-volume,
#     but the catch-all for "did this log even arrive and apply before the
#     solver-state check fired" desync investigations
# Per-target/high-noise (still OFF): APEXBOT_DRAIN_DBG, APEXBOT_TRACE_REGISTER_SEED
#   APEXBOT_DUMP_TICK_MAPS  (opt-in: dump full seed + verifier tick maps for the
#     tick-map desync re-assembly aid; high volume, set only for an investigation)
#
# Sim-failure policy: this script DEFAULTS APEXBOT_SIM_EXIT_ON_FAIL=0 (keep
# running through thin-margin/no-profit reverts - the routine arb-filter
# outcome). Failing simulations are identified from OTel traces/metrics going
# forward, not by killing the bot. Override to 1 to restore the old fail-fast.
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Debug-visible instrumented runs (default ON here).
#
# The Rust core's granular diagnostics ([solver-dbg],
# [solver-st], [v2-calc-trace], ...) are gated behind the `debug` tracing
# level AND the Python-side DEBUG logger (see docs/logging.md). Set BOTH below
# so those lines reach logs/bot_run.log in these instrumented runs:
#
#   * RUST_LOG        is the Rust `tracing` EnvFilter gate. Raising the
#                     apexbot_* crates to `debug` makes the fine-grained
#                     diagnostics visible while `info` keeps routine status
#                     lines; the alloy/tungstenite targets are held at `warn`
#                     to mirror the code's built-in default and stop their
#                     lifecycle INFO noise from flooding the log.
#   * APEXBOT_DEBUG=1 is the Python `logging` gate. Without it the crate-root
#                     Python loggers stay at INFO and drop the debug records
#                     before they reach the log/bot_run.log tee.
#
# Both respect a pre-set value: set RUST_LOG / APEXBOT_DEBUG yourself to opt
# out (e.g. RUST_LOG=warn ./run_bot.sh) or tighten the scope.
# --------------------------------------------------------------------------
DEFAULT_RUST_LOG="info,apexbot_bot=debug,apexbot_arbitrage=debug,apexbot_simulation=debug,apexbot_solvers=debug,alloy_pubsub=warn,alloy_transport=warn,alloy_transport_ws=warn,alloy_transport_ipc=warn,alloy_transport_http=warn,alloy_provider=warn,alloy_rpc=warn,alloy_network=warn,alloy_contract=warn,tungstenite=warn"
export RUST_LOG="${RUST_LOG:-$DEFAULT_RUST_LOG}"
export APEXBOT_DEBUG="${APEXBOT_DEBUG:-1}"
export APEXBOT_OTEL="${APEXBOT_OTEL:-1}"
# SIMPIPE2 T4 soak arm: the ENGINE-side inline sim (worker seam). Default 0
# (legacy option-A FFI pipeline); the soak flips 0/1 across equal windows.
export APEXBOT_SOLVE_INLINE_SIM="${APEXBOT_SOLVE_INLINE_SIM:-1}"
export APEXBOT_SIM_EXIT_ON_FAIL="${APEXBOT_SIM_EXIT_ON_FAIL:-0}"
export APEXBOT_WS_TRACE="${APEXBOT_WS_TRACE:-1}"
# Publish-debounce window (ms), last dirty log -> settle decision. A/B'd on
# 2026-09-04 (telemetry-latency-playbook S7): bursts complete in 1.3-27.5 ms
# while the 50 ms code default settled full-length on ~every block — a fixed
# settle tax. 15 ms cuts ~33 ms/block with no extra solve cycles observed.
# Code default stays 50 ms; invalid/zero env values fall back to 50 ms.
export APEXBOT_PUMP_DEBOUNCE_MS="${APEXBOT_PUMP_DEBOUNCE_MS:-15}"
# Typed-config parity (KAHU5W): every APEXBOT_* env above still works
# (12-factor parity) but each key also has a typed TOML path — these exports
# map to telemetry.otel, solve.solve_inline_sim, simulation.sim_exit_on_fail,
# trace.ws_trace, and pump.pump_debounce_ms in config.toml; the full key
# table lives in docs/rust-config-keys.md. Observability note (MROOY7): the
# retired pump/queue surface (spans apexbot.pump.block / pump.log_wait /
# pump.apply_stream, series apexbot_drain_queue_depth) is succeeded by the
# stage telemetry — spans apexbot.epoch + apexbot.stage.{streaming,quiesced,
# publish,finalize,rewind}, series apexbot_stage_publish_cycle_seconds /
# apexbot_stage_rewind_total / _duration_seconds; the metrics endpoint is
# APEXBOT_METRICS_ADDR (default 127.0.0.1:9464).
# Solver-state verification policy: ON-DEMAND ONLY (the ADR-021 publish
# tripwire and its APEXBOT_ASSERT_SOLVER_STATE knob are RETIRED — MROOY7
# task 2UVG3E: the overnight scan measured 29k tripwire WARNs and tens-of-
# seconds verify spans with zero caught desyncs in 6.5h, and the knob is no
# longer in the config schema, so exporting it here would be a dead knob).
# Standing verification: sim failures arm a divergence probe on the failing
# path's next sim (APEXBOT_SIM_DIVERGENCE_LOG=1 merges the engine-vs-RPC
# divergence logs), APEXBOT_VERIFY_SPOTCHECK_PERMYRIAD adds random spot-
# checks for operators, and APEXBOT_WS_COMPLETENESS (default ON) aborts
# loudly on a dropped WS log before state can drift. Desync containment runs
# through the resolve-seam quarantine gate (watch the
# apexbot_engine_quarantined_pools gauge / ApexbotDesyncQuarantine alert).

# Two-runtime contract (7LV6VN T5): solve bins, rayon resolve, sim runtime,
# and the sim-driver cap all derive from the detected cgroup budget inside
# the Rust core (cpu_budget::leftover_worker_budget), leaving the I/O
# headroom to the ambient runtime by construction. An operator export of
# APEXBOT_SOLVE_CPUS / APEXBOT_INLINE_SIM_WORKERS / APEXBOT_SOLVE_SIM_INFLIGHT
# still wins when set explicitly - none are pre-set here.

# The actual bot invocation (uv rebuilds the Rust extension if any rust
# source / Cargo.toml is newer than the installed build).
BOT_CMD=(uv run python examples/eth_settlement_arbitrage_v2_v3_v4_rust.py)

start() {
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "[runner] bot already running (pid $(cat "$PIDFILE"))" >&2
        return 1
    fi
    : > "$LOG"
    : > "$PIDFILE"
    # setsid: new session + no controlling terminal, so the launching shell
    # can exit without the pump dying (SIGHUP) and the tool shell's return
    # isn't entangled with the bot's life. exec is NOT used so `$!` is the
    # (setsid'd) uv pid we record. Output is captured by direct fd redirection
    # (never a tee pipeline), so the log is authoritative and survives the
    # launching shell going away.
    setsid "${BOT_CMD[@]}" >>"$LOG" 2>&1 < /dev/null &
    echo $! > "$PIDFILE"
    # Runner diagnostics go to the log too, so the whole launch is in one place.
    echo "[runner] started bot pid $(cat "$PIDFILE") $(date -Is)" | tee -a "$LOG" >&2
}

stop() {
    if [ -f "$PIDFILE" ]; then
        kill -TERM "$(cat "$PIDFILE")" 2>/dev/null
        sleep 1
        kill -9 "$(cat "$PIDFILE")" 2>/dev/null
        rm -f "$PIDFILE"
    fi
    # The uv wrapper may exit while its python child lingers; kill by name too.
    pkill -9 -f eth_settlement_arbitrage_v2_v3_v4 2>/dev/null
    echo "[runner] stopped $(date -Is)"
}

status() {
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "[runner] running pid $(cat "$PIDFILE")"
        ps -o pid,etime,cmd -p "$(cat "$PIDFILE")" 2>/dev/null | tail -1
    else
        echo "[runner] not running"
    fi
}

foreground() {
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "[runner] bot already running (pid $(cat "$PIDFILE")) — stop it first" >&2
        return 1
    fi
    # Fresh truncation, same as `start`, so the log always reflects this run
    # (the append-only `tee -a` behaviour is gone for determinism).
    : > "$LOG"
    : > "$PIDFILE"
    echo "[runner] starting bot $(date -Is)" | tee -a "$LOG" >&2
    # Bot output goes to the log by direct fd redirection — authoritative and
    # immune to a closing console (no `tee` pipeline to SIGPIPE and drop the
    # tail). The console is only a live mirror fed by `tail -f`.
    "${BOT_CMD[@]}" >>"$LOG" 2>&1 < /dev/null &
    BOTPID=$!
    echo "$BOTPID" > "$PIDFILE"
    tail -f -n +1 "$LOG" &
    TAILPID=$!
    # Forward Ctrl-C / TERM to the bot so it stops cleanly (the pump then gets
    # its exit path rather than being killed out from under the lock).
    trap 'kill -TERM "$BOTPID" 2>/dev/null' INT TERM
    wait "$BOTPID"
    BOTRC=$?
    kill "$TAILPID" 2>/dev/null
    wait "$TAILPID" 2>/dev/null
    rm -f "$PIDFILE"
    trap - INT TERM
    echo "[runner] bot exited rc=$BOTRC $(date -Is)" | tee -a "$LOG" >&2
    return "$BOTRC"
}

case "${1:-foreground}" in
    start) start ;;
    stop) stop ;;
    status) status ;;
    foreground) foreground ;;
    *)
        echo "usage: $0 {start|stop|status|foreground}" >&2
        exit 1
        ;;
esac
