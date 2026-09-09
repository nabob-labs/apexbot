"""Ban ``from apexbot._ffi`` in driver-facing example code.

The three-layer architecture (ADR-005) requires that driver code — including
the canonical ``examples/*.py`` bot templates — import only from the companion
package ``apexbot.*``. The PyO3 wrapper ``apexbot._ffi`` (the leading
underscore marks it private) is the FFI seam, an implementation detail of the
companion; it is not a public API for drivers.

This guard mechanically enforces the invariant so the import-reorder footgun
cannot recur: a contributor who adds ``from apexbot._ffi import ...`` to an
example bot will see this test fail, not silently shadow a companion symbol
(the original symptom that surfaced this work — ``AlloyProvider`` was imported
from both the FFI and ``apexbot.provider``, and a reorder would have swapped
which binding held).

Scope: ``examples/`` only. The ~60 ``src/apexbot/**`` internal
``apexbot._ffi`` imports are companion-layer modules using their own FFI seam
and are not in scope (the companion is allowed to reach its own FFI; the
driver is not). Test files are also out of scope — tests may reach the FFI
seam to verify identity / alias invariants.
"""

from __future__ import annotations

import pathlib

import pytest

# Patterns that indicate a direct import of the FFI seam. Each is checked as a
# plain substring of the source text (no AST needed — the import forms are
# distinctive enough that a source scan is sufficient and far cheaper).
_FORBIDDEN_PATTERNS = (
    "from apexbot._ffi import",
    "from apexbot_rs import",  # legacy name, in case of partial reverts
    "import apexbot._ffi",
    "import apexbot_rs",
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_EXAMPLES_DIR = _REPO_ROOT / "examples"


def _example_py_files() -> list[pathlib.Path]:
    """Every ``*.py`` under ``examples/``, relative to the repo root."""
    return sorted(_EXAMPLES_DIR.rglob("*.py"))


@pytest.mark.parametrize(
    "example_file",
    _example_py_files(),
    ids=lambda p: str(p.relative_to(_REPO_ROOT)),
)
def test_no_ffi_import_in_examples(example_file: pathlib.Path) -> None:
    """No ``examples/*.py`` imports the FFI seam directly.

    Raises:
        AssertionError: If any forbidden FFI-import pattern is found, naming
            the offending file and the matched pattern.

    """
    source = example_file.read_text(encoding="utf-8")
    for pattern in _FORBIDDEN_PATTERNS:
        assert pattern not in source, (
            f"{example_file.relative_to(_REPO_ROOT)} imports the FFI seam "
            f"directly via '{pattern}' — driver code must import from "
            f"apexbot.* (the companion), not apexbot._ffi (the PyO3 wrapper)."
        )
