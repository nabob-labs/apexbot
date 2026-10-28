//! Solady `LibZip` (`FastLZ`) `PyO3` wrappers over the pure `apexbot_core::libzip`
//! core. Mirrors the core surface; no per-domain feature gate (the libzip code
//! lives in `apexbot-core`, which is always a dependency).

pub mod libzip;

use pyo3::prelude::*;

/// The `apexbot._ffi.solady` Python submodule (declarative `#[pymodule]`),
/// carrying the Solady `LibZip` functions `flz_compress` / `flz_decompress`.
/// The parent module registers the submodule itself and its `sys.modules`
/// entry.
#[pymodule(submodule)]
#[pyo3(module = "apexbot._ffi")]
pub mod solady {
    #[pymodule_export]
    use super::libzip::{flz_compress, flz_decompress};
}
