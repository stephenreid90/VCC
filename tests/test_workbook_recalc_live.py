"""The committed workbook oracles still match a live LibreOffice recalculation.

Marked ``libreoffice`` and deselected by default (see ``pytest.ini``), because
making ``soffice`` a hard suite dependency would be a poor trade: the ordinary
gate should run anywhere. Run it deliberately with::

    pytest -m libreoffice

Why it needs to exist at all. ``test_dnl_workbook_tie.py`` and
``test_csl_workbook_tie.py`` assert the engine against committed JSON fixtures,
which is exactly right for a fast suite — but a fixture is only an oracle for as
long as somebody re-derives it. Regenerating by hand is a step that gets skipped,
and a stale fixture that agrees with a drifted engine looks identical to a fresh
one that agrees with a correct engine. This test closes that: it rebuilds both
workbooks from the current data files, recalculates them in LibreOffice, and
compares against what is committed. A failure means the fixtures need
regenerating (``python tests/dcf/golden/_recalc_generated_workbooks.py``) and,
before that, that somebody should read why they moved.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "dcf" / "golden"

pytestmark = pytest.mark.libreoffice


def _recalc_module():
    sys.path.insert(0, str(GOLDEN))
    import _recalc_generated_workbooks as mod  # noqa: E402

    return mod


@pytest.mark.skipif(shutil.which("soffice") is None, reason="LibreOffice not installed")
@pytest.mark.parametrize(
    "company,builder,sheet,extractor,fixture",
    [
        ("dnl", "build_dnl_workbook_bytes", "DCF build", "_extract_dnl",
         "dnl_workbook_all_scenarios.json"),
        ("csl", "build_csl_workbook_bytes", "Segment FCFF", "_extract_csl",
         "csl_workbook_all_scenarios.json"),
    ],
)
def test_committed_oracle_matches_a_live_recalc(
    company: str, builder: str, sheet: str, extractor: str, fixture: str
) -> None:
    mod = _recalc_module()
    sys.path.insert(0, str(ROOT / "ui_prototypes" / "_generator"))
    import engine_workbook  # noqa: E402
    from openpyxl import load_workbook  # noqa: E402

    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        src = work / f"{company}.xlsx"
        src.write_bytes(getattr(engine_workbook, builder)())
        ws = load_workbook(mod._recalc(src, work), data_only=True)[sheet]
        fresh = getattr(mod, extractor)(ws)

    committed = json.loads((GOLDEN / fixture).read_text())
    assert set(fresh) == set(committed)
    for scenario in committed:
        for kind in ("vectors", "scalars"):
            for key, want in committed[scenario][kind].items():
                got = fresh[scenario][kind][key]
                if isinstance(want, list):
                    for i, (g, w) in enumerate(zip(got, want)):
                        assert g == pytest.approx(w, rel=1e-9, abs=1e-9), (
                            f"{company}.{scenario}.{key}[{i}] drifted: "
                            f"committed {w}, live recalc {g}"
                        )
                else:
                    assert got == pytest.approx(want, rel=1e-9, abs=1e-9), (
                        f"{company}.{scenario}.{key} drifted: "
                        f"committed {want}, live recalc {got}"
                    )
