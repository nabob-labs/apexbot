//! `apexbot-abi` `PyO3` wrappers (`#[pyfunction]` decode/encode over the pure core).
//! Mirrors `crates/foundation/apexbot-abi/`.

pub mod decoder;
pub mod encoder;

use pyo3::prelude::*;

/// The `apexbot._ffi.abi` Python submodule (declarative `#[pymodule]`).
///
/// Carries the ABI decode/encode fns (`decode`/`decode_single`/`encode`/
/// `encode_packed`/`encode_single`). Unlike the math submodules, no
/// de-prefixing is needed — these fns were already un-prefixed; the win is
/// the submodule + companion home (importers reach them via
/// `apexbot.abi_adapter`, not `apexbot._ffi`). The parent module
/// registers the submodule itself and its `sys.modules` entry.
#[pymodule(submodule)]
#[pyo3(module = "apexbot._ffi")]
pub mod abi {
    #[pymodule_export]
    use super::decoder::{decode, decode_single};

    #[pymodule_export]
    use super::encoder::{encode, encode_packed, encode_single};
}
