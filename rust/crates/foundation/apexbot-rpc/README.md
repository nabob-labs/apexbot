# apexbot-rpc

Pure-Rust Ethereum RPC provider, contract interface, and subscription core.

The pure-Rust Ethereum RPC layer: typed provider, contract interfaces, and the subscription core the pump loop and updaters consume.

## Usage

```toml
apexbot-rpc = "0.6.0-alpha.5"
```

Or: `cargo add apexbot-rpc` (the pre-release version must be pinned explicitly, e.g. "0.6.0-alpha.5").

Part of [apexbot](https://github.com/nabob-labs/apexbot) — a Rust-first MEV bot for EVM chains. The in-repo root README and `docs/` cover the full architecture; this crate is published standalone so you can depend on exactly the pieces you need.
