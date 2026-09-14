"""Every script in the repo must at least parse.

The suite imports the engine, not the generators, so a generator can be broken on
main without a single test going red. On 14 September 2026 a `# ssot-allow` marker
was inserted mid-line in `ui_prototypes/_generator/build_cfgs.py`, commenting out
the rest of that line including a closing bracket. The file stopped parsing, the UI
config was never rebuilt, and the base-tie check went on comparing the ratified
levels against a config built weeks earlier — reporting a mismatch that had nothing
to do with the engine.

This is the cheapest possible guard: compile every `.py` under the directories the
suite does not import, and fail with the file and line if any of them will not.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCANNED = ("scripts", "ui_prototypes")


def _sources() -> list[Path]:
    out: list[Path] = []
    for d in SCANNED:
        out.extend(sorted((ROOT / d).rglob("*.py")))
    return [p for p in out if "__pycache__" not in p.parts]


def test_there_are_scripts_to_check() -> None:
    assert _sources(), "no scripts found — the scan roots have moved"


@pytest.mark.parametrize("path", _sources(), ids=lambda p: str(p.relative_to(ROOT)))
def test_script_parses(path: Path) -> None:
    src = path.read_text(encoding="utf-8")
    try:
        ast.parse(src, filename=str(path))
    except SyntaxError as exc:
        pytest.fail(f"{path.relative_to(ROOT)}:{exc.lineno}: {exc.msg}")
