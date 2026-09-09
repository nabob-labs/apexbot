"""Database session management and Alembic configuration."""

from typing import TYPE_CHECKING

from apexbot.database.operations import get_alembic_config, get_scoped_sqlite_session
from apexbot.database.session_manager import DatabaseSessionManager

if TYPE_CHECKING:
    # ADR-013: stable home for the FFI ERC-20 DB row type so a leaf module
    # (apexbot.builders.erc20_builder) need not import apexbot._ffi directly.
    # TYPE_CHECKING-only: it is used solely in annotations (`from __future__
    # import annotations` keeps those lazy at runtime).
    from apexbot._ffi import Erc20TokenRow as Erc20TokenRow

__all__ = (
    "DatabaseSessionManager",
    "get_alembic_config",
    "get_scoped_sqlite_session",
)
