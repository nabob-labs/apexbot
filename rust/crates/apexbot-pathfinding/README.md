# apexbot-pathfinding

Pure-Rust arbitrage pathfinding graph + DFS (zero-dependency leaf; no pyo3/tokio/alloy).

The arbitrage pathfinding graph and DFS as a zero-dependency leaf (no pyo3, tokio, or alloy): route discovery across pooled DEX edges only.

## Usage

```toml
apexbot-pathfinding = "0.6.0-alpha.5"
```

Or: `cargo add apexbot-pathfinding` (the pre-release version must be pinned explicitly, e.g. "0.6.0-alpha.5").

Part of [apexbot](https://github.com/BowTiedDevil/apexbot) — a Rust-first MEV bot for EVM chains. The in-repo root README and `docs/` cover the full architecture; this crate is published standalone so you can depend on exactly the pieces you need.
