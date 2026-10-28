//! The `apexbot` binary: a thin process shell over [`apexbot_cli::run`].
//!
//! All the work (argv, sinks, SIGINT, rendering) lives in the library so the
//! binary target is trivial to audit; the binary owns nothing but its exit
//! code.

fn main() {
    std::process::exit(apexbot_cli::run());
}
