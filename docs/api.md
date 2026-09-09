# API reference

The Python driver layer is documented straight from source (static parse, so the Read the Docs build needs no Rust toolchain or compiled extension). Entry points most people want first:

- {doc}`Bot <autoapi/apexbot/bot/index>` — the central session object (construction, `build_pool` / `build_erc20token` factories, pump orchestration)
- {doc}`Exceptions <autoapi/apexbot/exceptions/index>` — `VerificationMismatchError`, `VerificationRpcError`, and friends

The full tree lives at {doc}`autoapi/apexbot/index`. It is generated from the public driver modules; per [ADR-013](adr/ADR-013-ffi-seam-is-private.md) the `apexbot._ffi` seam is intentionally excluded, as are the compiled extension internals.

Tip: with the package installed, `help(apexbot.Bot)` and your IDE will show the same docstrings through the type stubs.
