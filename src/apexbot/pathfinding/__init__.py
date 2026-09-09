"""Pathfinding utilities for discovering arbitrage routes.

Barrier module (ADR-013: the Pydantic barrier): bridges the Rust
``build_path_graph`` / ``find_paths_rust`` seams from ``_ffi`` and re-exports
the deep pathfinding logic from :mod:`._pathfinding`. Importers should use::

    from apexbot.pathfinding import find_paths, find_paths_async

rather than reaching into ``apexbot._ffi`` directly.
"""

from apexbot._ffi import build_path_graph, find_paths_rust

from ._pathfinding import PathStep, find_paths, find_paths_async

__all__ = [
    "PathStep",
    "build_path_graph",
    "find_paths",
    "find_paths_async",
    "find_paths_rust",
]
