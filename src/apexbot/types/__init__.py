"""Shared types: AddressComparable, state caches, pool enums, and aliases."""

from apexbot._ffi import LiquidityPool
from apexbot._ffi.dex_identity import DexIdentity, dex_identity

from .address_comparable import AddressComparable
from .concrete import BoundedCache, KeyedDefaultDict
from .pool_protocols import (
    MultiTokenSwapCalculation,
    PoolSimulation,
    StateManageablePool,
    TwoTokenSwapCalculation,
)

__all__ = (
    "AddressComparable",
    "BoundedCache",
    "DexIdentity",
    "KeyedDefaultDict",
    "LiquidityPool",
    "MultiTokenSwapCalculation",
    "PoolSimulation",
    "StateManageablePool",
    "TwoTokenSwapCalculation",
    "dex_identity",
)
