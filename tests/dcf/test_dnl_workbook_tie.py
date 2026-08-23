"""DNL: the engine ties to an independently recalculated Excel workbook.

Six scenarios, line for line. The oracle
(``golden/dnl_workbook_all_scenarios.json``) is produced by
``golden/_recalc_dnl_workbook.py``, which recalculates the formula-only workbook
in LibreOffice; no engine number goes into it. That is the point: the
working-capital rows and the normalised terminal introduced on 23 August 2026
retire the ``capitalise_last_fcff`` oracle in ``test_e2e_dnl_mt.py``, and an
engine change without a spreadsheet to check it against is exactly the
self-certification D-13 warns about.

Tolerance is tight (1e-6 relative) because both sides evaluate the same formulas
from the same inputs — this is a tie, not a reconciliation. A failure means the
engine and the workbook have diverged, which is always worth reading before
re-pinning anything.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from vcc_valuations.dcf.fcf_engine import FcfEngine
from vcc_valuations.translator import build_engine_inputs_from_data, load_inputs

ROOT = Path(__file__).resolve().parents[2]
ORACLE = json.loads(
    (Path(__file__).parent / "golden" / "dnl_workbook_all_scenarios.json").read_text()
)
SCENARIOS = list(ORACLE)
VECTORS = ["revenue", "ebit", "nopat", "da", "capex", "delta_wc", "fcff", "pv_fcff"]
SCALARS = ["pv_explicit", "terminal_fcff", "terminal_value", "pv_terminal",
           "enterprise_value", "equity_value", "value_per_share"]


def _result(scenario: str):
    inputs = load_inputs(
        ROOT, scenario_id=scenario, archetype_id="industrial_explosives", company_id="dnl"
    )
    return FcfEngine().run(build_engine_inputs_from_data(inputs, scenario))


@pytest.fixture(scope="module")
def results():
    return {s: _result(s) for s in SCENARIOS}


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("attr", VECTORS)
def test_line_vectors_tie_to_workbook(results, scenario: str, attr: str) -> None:
    got = getattr(results[scenario], attr)
    want = ORACLE[scenario]["vectors"][attr]
    assert len(got) == len(want)
    for period, (g, w) in enumerate(zip(got, want)):
        assert g == pytest.approx(w, rel=1e-6, abs=1e-6), (
            f"{scenario}.{attr}[{period}]: engine {g}, workbook {w}"
        )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_scalars_tie_to_workbook(results, scenario: str) -> None:
    for attr in SCALARS:
        got = getattr(results[scenario], attr)
        want = ORACLE[scenario]["scalars"][attr]
        assert got == pytest.approx(want, rel=1e-6, abs=1e-6), (
            f"{scenario}.{attr}: engine {got}, workbook {want}"
        )


def test_working_capital_is_actually_booked(results) -> None:
    """Guards the defect this work exists to fix: a silent vector of zeros.

    Every period must carry a working-capital outflow, and from Y2 on — where
    both ends of the step are full years — each one must equal the intensity
    times that year's revenue increment. That is the identity that catches an
    off-by-one in the run-rate chain, which the stub and Y1 obscure because the
    stub is a part-year flow.
    """
    for scenario, r in results.items():
        assert all(w < 0 for w in r.delta_wc), f"{scenario}: delta_wc not booked"
        intensity = r.terminal_working_capital_intensity
        assert intensity is not None
        for k in range(2, len(r.revenue)):
            step = intensity * (r.revenue[k] - r.revenue[k - 1])
            assert -r.delta_wc[k] == pytest.approx(step, rel=1e-9), f"{scenario} Y{k}"


def test_terminal_is_normalised_not_capitalised(results) -> None:
    """The terminal must be rebuilt, not grown from the last explicit FCFF.

    Without this the explicit period's ~6% growth carries its working-capital
    build into a ~2.5% perpetuity, and the terminal capex stays wherever the
    scenario left it in year five.
    """
    for scenario, r in results.items():
        assert r.terminal_reinvestment == "normalised", scenario
        assert r.terminal_capex_pct_revenue == pytest.approx(r.da[0] / r.revenue[0])
        assert r.terminal_fcff != pytest.approx(r.fcff[-1] * (1.0 + r.terminal_growth))
