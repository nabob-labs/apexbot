"""High-performance Ethereum RPC provider using Alloy.

This module provides a Rust-based provider for fast log fetching and RPC calls.

RPC methods return the ``LogData`` / ``BlockData`` mappings defined in
:mod:`apexbot.types.rpc_types`: plain ``bytes`` for hash and data fields,
EIP-55 checksummed strings for addresses, and Python ``int`` for numeric
fields. Log dicts use camelCase keys; block/transaction dicts use
snake_case.

The provider surface is split by concurrency: the sync mixins and
:class:`AlloyProvider` live in :mod:`apexbot.provider.sync`, the async
twins in :mod:`apexbot.provider.async_provider`.

Example:
    >>> from apexbot.provider import AlloyProvider, LogFilter
    >>> provider = AlloyProvider("https://eth-mainnet.example.com")
    >>>
    >>> # Direct property access
    >>> chain_id = provider.chain_id
    >>> block_number = provider.block_number
    >>>
    >>> # Log fetching with LogFilter
    >>> logs = provider.get_logs(
    ...     LogFilter(
    ...         from_block=18_000_000,
    ...         to_block=18_010_000,
    ...         addresses=["0x..."],
    ...     )
    ... )
    >>>
    >>> # Or using keyword arguments
    >>> logs = provider.get_logs(
    ...     from_block=18_000_000,
    ...     to_block=18_010_000,
    ...     addresses=["0x..."],
    ... )

"""

from apexbot._ffi import ChainMismatchError
from apexbot.provider._rust import RustAlloyProvider, RustAsyncAlloyProvider
from apexbot.provider.async_provider import AsyncAlloyProvider
from apexbot.provider.factory import (
    ChainIdentityMismatchError,
    get_async_provider_from_config,
    get_provider_from_config,
)
from apexbot.provider.offline_provider import OfflineProvider
from apexbot.provider.sync import AlloyProvider, LogFilter

# ADR-013 barrier: the Rust pyclasses the submodule trees (and
# offline_provider) construct are bound in :mod:`apexbot.provider._rust` —
# the one module that imports ``apexbot._ffi`` — and re-exported here.

__all__ = [
    "AlloyProvider",
    "AsyncAlloyProvider",
    "ChainIdentityMismatchError",
    "ChainMismatchError",
    "LogFilter",
    "OfflineProvider",
    "RustAlloyProvider",
    "RustAsyncAlloyProvider",
    "get_async_provider_from_config",
    "get_provider_from_config",
]
