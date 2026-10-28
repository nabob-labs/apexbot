# apexbot-abi

Pure-Rust ABI type/decode/encode and function-signature parsing.

ABI type definitions, encoding, decoding, and function-signature parsing in pure Rust, so bot code builds and parses contract calls without Python-side tooling.

## Usage

```toml
apexbot-abi = "0.6.0-alpha.5"
```

Or: `cargo add apexbot-abi` (the pre-release version must be pinned explicitly, e.g. "0.6.0-alpha.5").

Part of [apexbot](https://github.com/nabob-labs/apexbot) — a Rust-first MEV bot for EVM chains. The in-repo root README and `docs/` cover the full architecture; this crate is published standalone so you can depend on exactly the pieces you need.
