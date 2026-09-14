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


def _write_opens_without_encoding(tree: ast.AST) -> list[int]:
    """Line numbers of open(..., 'w') calls that do not name an encoding.

    Python picks the platform default codec when none is given. On Linux that is
    UTF-8 and nothing goes wrong; on Windows it is cp1252, and a file containing
    an arrow or an em dash raises UnicodeEncodeError on write. That is exactly
    how the base-tie rebuild died on Stephen's machine on 14 September 2026,
    having passed in the container minutes earlier.
    """
    bad: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (isinstance(node.func, ast.Name) and node.func.id == "open"):
            continue
        mode = ""
        if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
            mode = str(node.args[1].value)
        for kw in node.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                mode = str(kw.value.value)
        if not any(c in mode for c in "wax"):
            continue
        if not any(kw.arg == "encoding" for kw in node.keywords):
            bad.append(node.lineno)
    return bad


@pytest.mark.parametrize("path", _sources(), ids=lambda p: str(p.relative_to(ROOT)))
def test_writes_name_their_encoding(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    bad = _write_opens_without_encoding(tree)
    assert not bad, (
        f"{path.relative_to(ROOT)}: open(..., 'w') without encoding= at "
        f"line(s) {bad}. The platform default codec is cp1252 on Windows and "
        f"will fail on any non-Latin-1 character."
    )
