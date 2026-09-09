"""Provider/RPC-layer exceptions owned by apexbot.

These are the apexbot-owned equivalents of the ``web3.exceptions`` types the
codebase previously imported: ``Web3Exception`` (the broad RPC base),
``ContractLogicError`` (an ``eth_call`` execution revert), and
``TransactionNotFound`` (a transaction hash the provider could not find).

Owning them here lets probe sites throughout the codebase
(:mod:`apexbot.builders.type_resolution`, :mod:`apexbot.builders.erc20_builder`)
catch a single apexbot-owned type regardless of which provider backend raised
the failure. ``apexbot.provider.alloy_errors`` converts the backend's native
failure into these types so downstream code is backend-agnostic.

Layering note: these are **provider-layer** exceptions — the RPC node reported a
revert or a missing transaction. They are distinct from the pool-math-layer
:exc:`~apexbot.exceptions.EVMRevertError` (a local pool-state simulation that
would revert). :meth:`CurveDataProvider._wrap_revert` bridges the two:
provider-layer :exc:`ContractLogicError` → pool-layer :exc:`EVMRevertError`.
"""

from apexbot.exceptions.base import ApexbotError


class RpcError(ApexbotError):
    """Base for provider/RPC-layer failures.

    The apexbot-owned equivalent of ``web3.exceptions.Web3Exception``: the
    broad base a caller can catch to mean "an RPC call failed for some reason."
    Probe sites catch this instead of backend-specific native types, so they
    remain backend-agnostic.
    """


class ContractLogicError(RpcError):
    """An ``eth_call`` execution revert reported by the provider.

    The apexbot-owned equivalent of ``web3.exceptions.ContractLogicError``.
    Raised at the provider adapter seam (see
    :func:`apexbot.provider.alloy_errors.alloy_revert_error`) so probe sites
    catch one type regardless of backend.

    Constructed with a positional revert message (mirroring the web3 type's
    constructor) so call sites can write ``ContractLogicError("... reverted")
    `` and ``str(exc)`` returns that message.
    """

    def __init__(self, message: str = "") -> None:
        """Initialize with a revert message (empty by default)."""
        self.message = message or None
        super().__init__(message=self.message)


class TransactionNotFound(RpcError):
    """A transaction hash the provider could not find.

    The apexbot-owned equivalent of
    ``web3.exceptions.TransactionNotFound``. Raised by the provider adapter
    seam when a receipt lookup misses.
    """
