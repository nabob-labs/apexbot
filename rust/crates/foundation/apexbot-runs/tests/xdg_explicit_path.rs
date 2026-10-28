//! Integration check: an EXPLICIT operator-set runs path is expanded as
//! written - `$XDG_STATE_HOME` never rebases it (only the built-in default
//! is XDG-rooted). Mirrors the database-path seam's Source-aware rule.

#![expect(
    clippy::expect_used,
    reason = "test fixtures fail loudly on an unconstructible prerequisite"
)]

#[test]
fn explicit_runs_dir_under_local_state_is_not_rebased() {
    let home = std::env::temp_dir().join(format!("apexbot-runs-xdg-{}-ovr", std::process::id()));
    let xdg = std::env::temp_dir().join(format!("apexbot-runs-xdg-{}-ovrxdg", std::process::id()));
    let _ = std::fs::remove_dir_all(&home);
    let _ = std::fs::remove_dir_all(&xdg);
    std::fs::create_dir_all(&home).expect("scratch home");
    std::fs::create_dir_all(&xdg).expect("scratch xdg");

    let saved = [
        ("HOME", std::env::var("HOME").ok()),
        ("XDG_STATE_HOME", std::env::var("XDG_STATE_HOME").ok()),
        ("XDG_CONFIG_HOME", std::env::var("XDG_CONFIG_HOME").ok()),
        ("APEXBOT_CONFIG", std::env::var("APEXBOT_CONFIG").ok()),
        ("APEXBOT_RUNS_DIR", std::env::var("APEXBOT_RUNS_DIR").ok()),
        (
            "APEXBOT_STATE_DIR",
            std::env::var("APEXBOT_STATE_DIR").ok(),
        ),
    ];
    std::env::set_var("HOME", &home);
    std::env::set_var("XDG_STATE_HOME", &xdg);
    std::env::set_var("APEXBOT_RUNS_DIR", "~/.local/state/mine");
    for name in ["XDG_CONFIG_HOME", "APEXBOT_CONFIG", "APEXBOT_STATE_DIR"] {
        std::env::remove_var(name);
    }

    let resolved = apexbot_runs::resolve_runs_root().expect("resolve runs root");
    assert_eq!(
        resolved,
        home.join(".local/state/mine"),
        "an explicit ~/.local/state path is the operator's literal, not an XDG alias"
    );

    for (name, value) in &saved {
        if let Some(v) = value {
            std::env::set_var(name, v);
        } else {
            std::env::remove_var(name);
        }
    }
    let _ = std::fs::remove_dir_all(&home);
    let _ = std::fs::remove_dir_all(&xdg);
}
