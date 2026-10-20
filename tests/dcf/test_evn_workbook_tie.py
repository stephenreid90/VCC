"""The resource engine ties to an independently recalculated Excel workbook (gap 9, 20 Oct 2026).

The companion to ``test_dnl_workbook_tie.py`` and ``test_csl_workbook_tie.py`` for the
fourth engine. ``ui_prototypes/_generator/resource_workbook.py`` writes a formula-only
workbook (standing rule 1): the yellow Assumptions cells are the only inputs and every
other cell is an Excel formula, so recalculating it in LibreOffice evaluates the
mine-by-mine depletion run-off independently of the Python engine. The oracle
(``golden/<cid>_workbook_all_scenarios.json``) comes from
``golden/_recalc_generated_workbooks.py``; ``test_workbook_recalc_live.py`` (marked
``libreoffice``) checks the committed oracle against a fresh recalculation.

What ties: every per-period line the engine reports (metal, revenue, royalty, operating
cost, EBITDA, D&A, tax, capital, working capital, FCFF, PV, the D-104 multiplier), the
present values, the equity bridge, value per share, the run-off share and the life, for
all six scenarios, to 1e-6. The company is whatever ``data/companies`` declares with
``engine: resource``; nothing here names one.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from size_resource_valuation import resource_companies, run  # noqa: E402

VECTORS = ["gold_koz", "copper_kt", "revenue", "royalty", "operating_cost", "ebitda", "da", "tax",
           "capex", "delta_wc", "fcff", "pv_fcff", "cost_price_link"]
SCALARS = ["pv_explicit", "pv_terminal", "terminal_value", "enterprise_value", "equity_value",
           "value_per_share", "terminal_share_of_ev", "life_years"]
COMPANIES = resource_companies()


def _oracle(cid: str) -> dict:
    return json.loads((Path(__file__).parent / "golden" / f"{cid}_workbook_all_scenarios.json").read_text())


@pytest.fixture(scope="module", params=COMPANIES, ids=[c for c, _ in COMPANIES])
def company(request):
    cid, arch = request.param
    oracle = _oracle(cid)
    return cid, oracle, {sid: run(cid, arch, sid)[0] for sid in oracle}


def test_every_scenario_has_an_oracle(company) -> None:
    cid, oracle, results = company
    assert len(oracle) == 6, f"{cid}: {sorted(oracle)}"


@pytest.mark.parametrize("attr", VECTORS)
def test_line_vectors_tie_to_workbook(company, attr: str) -> None:
    cid, oracle, results = company
    for sid, r in results.items():
        want = oracle[sid]["vectors"][attr]
        got = getattr(r, attr)
        assert len(got) == len(want) == oracle[sid]["scalars"]["periods"], f"{cid}.{sid}.{attr}: {len(got)} vs {len(want)}"
        for t, (g, w) in enumerate(zip(got, want)):
            assert g == pytest.approx(w, rel=1e-6, abs=1e-6), f"{cid}.{sid}.{attr}[{t}]: engine {g}, workbook {w}"


def test_scalars_tie_to_workbook(company) -> None:
    cid, oracle, results = company
    for sid, r in results.items():
        for attr in SCALARS:
            got, want = getattr(r, attr), oracle[sid]["scalars"][attr]
            assert got == pytest.approx(want, rel=1e-6, abs=1e-6), f"{cid}.{sid}.{attr}: engine {got}, workbook {want}"


def test_terminal_is_the_run_off_not_a_perpetuity(company) -> None:
    """D-97: the workbook's post-horizon value is the PV of dated cash flows, nothing after the last closure."""
    cid, oracle, results = company
    for sid, r in results.items():
        pv = oracle[sid]["vectors"]["pv_fcff"]
        assert sum(pv[r.horizon_years + 1:]) == pytest.approx(oracle[sid]["scalars"]["pv_terminal"], rel=1e-9)
