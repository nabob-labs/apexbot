"""Block identifier resolution helpers."""

from typing import TYPE_CHECKING, cast

from apexbot.exceptions import ApexbotValueError
from apexbot.provider import AlloyProvider
from apexbot.types.aliases import BlockNumber
from apexbot.types.rpc_types import BlockIdentifier


def get_number_for_block_identifier(
    identifier: BlockIdentifier | None,
    provider: AlloyProvider,
) -> BlockNumber:
    """Convert a block identifier to a block number.

    Args:
        identifier: Block identifier (None, int, or string tag like 'latest')
        provider: AlloyProvider instance

    Returns:
        Block number as integer

    Raises:
        ApexbotValueError: If the block identifier is invalid or block not found.

    """
    match identifier:
        case None:
            return provider.get_block_number()
        case int() as block_number_as_int:
            return block_number_as_int
        case "latest" | "earliest" | "pending" | "safe" | "finalized" as block_tag:
            block = provider.get_block(cast("int | str", identifier))
            if block is None:
                raise ApexbotValueError(message=f"Block {block_tag} not found")
            block_number = block.get("number")
            if TYPE_CHECKING:
                assert block_number is not None
            return block_number
        case str() as block_number_as_str:
            try:
                return int(block_number_as_str, 16)
            except ValueError:
                raise ApexbotValueError(
                    message=f"Invalid block identifier {identifier!r}",
                ) from None
        case bytes() as block_number_as_bytes:
            return int.from_bytes(block_number_as_bytes, byteorder="big")
        case _:
            raise ApexbotValueError(message=f"Invalid block identifier {identifier!r}")
