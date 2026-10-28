# apexbot-order-index

Convex-hull / upper-envelope order index for ranking path results by net profit under a variable gas price.

The convex-hull / upper-envelope order index that ranks arbitrage path results by net profit under a variable gas price — the final filter before settlement.

## Usage

```toml
apexbot-order-index = "0.6.0-alpha.5"
```

Or: `cargo add apexbot-order-index` (the pre-release version must be pinned explicitly, e.g. "0.6.0-alpha.5").

Part of [apexbot](https://github.com/nabob-labs/apexbot) — a Rust-first MEV bot for EVM chains. The in-repo root README and `docs/` cover the full architecture; this crate is published standalone so you can depend on exactly the pieces you need.
