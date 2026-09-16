"""Stable companion home for Curve StableSwap math functions.

Re-exports the Rust-backed math from the ``apexbot._ffi.curve_math``
submodule with un-prefixed names. Importers should use::

    from apexbot.curve.math import stableswap_get_y

rather than reaching into ``apexbot._ffi`` directly — this path is stable
across future Rust reshuffles, and lets the Rust crate structure
(``apexbot-curve-math``) show through to Python.

The functions are thin PyO3 wrappers over the pure-Rust
``apexbot-curve-math`` core crate; see that crate's docs for math semantics.
"""

from apexbot._ffi.curve_math import (
    derive_rate_and_precision_multipliers,
    stableswap_get_d,
    stableswap_get_y,
    stableswap_get_y_d,
    stableswap_newton_y,
    stableswap_reduction_coefficient,
)

__all__ = [
    "derive_rate_and_precision_multipliers",
    "stableswap_get_d",
    "stableswap_get_y",
    "stableswap_get_y_d",
    "stableswap_newton_y",
    "stableswap_reduction_coefficient",
]
