"""Aave V3 lending market models, operations, and updater.

Bridges two Rust crates:
- ``apexbot-price`` — the Aave price oracle (``AavePriceOracle``)
- ``apexbot-aave-updater`` — the Aave V3 updater loop + verification
  (``run_aave_update``, ``activate_aave_market``, etc.)

The updater functions are thin PyO3 wrappers over the pure-Rust
``apexbot-aave-updater`` core crate. ``CancelHandle`` is re-exported via
``apexbot.updater``.

The former Python in-memory enrichment/processing pipeline
(``extraction``/``operations``/``events``/``models``/``calculator``/
``liquidation_patterns``/``pattern_types``/``operation_types`` + the
``enrichment/`` and ``processors/`` packages) was retired once the Rust
``apexbot-aave`` crate reached feature parity (it owns the full RPC fetch +
decode + apply + verify loop end-to-end). The ``analysis/`` read-back
package is a thin driver shell over the same Rust core's position-analysis
math. The former Python ``libraries/`` math primitives package was retired
once ``apexbot-aave::wad_ray_math`` owned the equivalents and the
analysis cutover removed the last Python importer.
"""

from apexbot._ffi.aave import (
    activate_aave_market,
    cleanup_zero_balance_positions,
    deactivate_aave_market,
    run_aave_update,
)
from apexbot._ffi.price import AavePriceOracle

__all__ = [
    "AavePriceOracle",
    "activate_aave_market",
    "cleanup_zero_balance_positions",
    "deactivate_aave_market",
    "run_aave_update",
]
