//! KAHU5W: the process-wide typed `BotConfig` holder.
//!
//! Exactly ONE site reads the environment for `APEXBOT_*` keys: the
//! apexbot-config loader. The owner (the Python driver / \`Bot::new\` /
//! the example boots) loads it once and installs the resulting value here;
//! every former environment-reading call site reads a typed field off
//! [`config`] instead. This is a plain VALUE holder — it performs no
//! environment access of its own (the ADR-021 tripwire pattern, extended
//! process-wide: the object carries data, never the environment).
//!
//! Tests that never install a config observe the schema defaults, which is
//! byte-compatible with running in a clean environment.

use std::sync::Arc;

/// Install the loaded config (thin delegate to the crate-level holder).
#[must_use]
pub fn install(cfg: Arc<::apexbot_config::BotConfig>) -> bool {
    ::apexbot_config::holder::install(cfg)
}

/// The installed config, or the schema defaults when none was installed.
#[must_use]
pub fn config() -> &'static ::apexbot_config::BotConfig {
    ::apexbot_config::holder::config()
}

/// Was a config installed by a real boot (vs test defaults)?
#[must_use]
pub fn installed() -> bool {
    ::apexbot_config::holder::installed()
}
