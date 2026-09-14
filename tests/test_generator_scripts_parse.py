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


def _text_access_without_encoding(tree: ast.AST) -> list[str]:
    """Every text-mode file access in a tree that does not name an encoding.

    Python picks the platform default codec when none is given. On Linux that is
    UTF-8 and nothing goes wrong; on Windows it is cp1252, and a file containing
    an arrow or an em dash raises UnicodeEncodeError on write. That is exactly
    how the base-tie rebuild died on Stephen's machine on 14 September 2026,
    having passed in the container minutes earlier.

    The first version of this guard checked writes only, which turned out to be
    half the class. `engine_workbook.py` read `cfgs_gen.json` back with a bare
    `open()` at three sites; that file carries curly quotes, arrows, Δ, β and ≈,
    so on Windows the read raised UnicodeDecodeError, the module-scoped `books`
    fixture died, and all eleven tests in `test_engine_workbook.py` errored —
    while this guard sat green, because none of the three was a write. Reading
    is the more common direction and was the unguarded one.

    So the rule is now the whole class: any text-mode `open`, `Path.read_text`
    or `Path.write_text` must name its encoding, in either direction. Binary
    modes are exempt — they have no codec to get wrong. A mode the AST cannot
    resolve to a constant is treated as text, because the safe assumption is the
    one that asks for an explicit encoding.
    """
    bad: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        else:
            continue
        if name not in ("open", "read_text", "write_text"):
            continue
        if name == "open":
            mode = ""
            if len(node.args) > 1:
                mode = (
                    str(node.args[1].value)
                    if isinstance(node.args[1], ast.Constant)
                    else "?"
                )
            for kw in node.keywords:
                if kw.arg == "mode":
                    mode = (
                        str(kw.value.value)
                        if isinstance(kw.value, ast.Constant)
                        else "?"
                    )
            if "b" in mode:
                continue
        if not any(kw.arg == "encoding" for kw in node.keywords):
            bad.append(f"{name}() line {node.lineno}")
    return bad


@pytest.mark.parametrize("path", _sources(), ids=lambda p: str(p.relative_to(ROOT)))
def test_text_file_access_names_its_encoding(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    bad = _text_access_without_encoding(tree)
    assert not bad, (
        f"{path.relative_to(ROOT)}: text file access without encoding= at "
        f"{', '.join(bad)}. The platform default codec is cp1252 on Windows "
        f"and will fail on any non-Latin-1 character, reading or writing."
    )
