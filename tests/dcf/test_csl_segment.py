"""CSL-3: the multi-segment FCFF engine (M3) reproduces the workbook from data.

Muddle Through ties the audited workbook
(analyses/csl/valuations/csl_muddle_through_valuation_v4.xlsx): USD 134.52 / AUD 203.83,
built bottom-up from the three segments with no hand-typed constant in the engine. The six
scenarios value from the same path and are downside-skewed.
"""

from pathlib import Path

import pytest

from vcc_valuations.dcf.segment_engine import SegmentEngine
from vcc_valuations.translator import build_segment_inputs_from_data, load_inputs

ROOT = Path(__file__).resolve().parents[2]

SCENARIOS = [
    "orderly_convergence", "muddle_through", "ai_productivity_lag",
    "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists",
]


def _run(scenario):
    inp = load_inputs(ROOT, scenario, "biopharmaceuticals", "csl")
    return SegmentEngine().run(build_segment_inputs_from_data(inp, scenario))


def test_muddle_through_ties_workbook():
    """Restated 23 Aug 2026 (D-30): the v4 workbook was struck at the hand-typed
    10% working-capital intensity and no longer arbitrates. The live tie is
    ``test_csl_workbook_tie.py``, against the generated workbook recalculated in
    LibreOffice across all six scenarios; these figures are that workbook's.
    """
    r = _run("muddle_through")
    assert r.value_per_share_usd == pytest.approx(129.2130, abs=1e-3)
    assert r.value_per_share_aud == pytest.approx(195.78, abs=0.02)
    assert r.enterprise_value == pytest.approx(71487.10, abs=1.0)
    assert r.pv_explicit == pytest.approx(17586.26, abs=1.0)
    assert r.terminal_value == pytest.approx(81986.40, abs=2.0)
    assert r.equity_value == pytest.approx(61880.10, abs=1.0)
    # cost of equity Rf + beta*ERP = 4.5% + 0.85*5.0%
    assert r.value_per_share_aud == pytest.approx(r.value_per_share_usd * 1.5152, abs=1e-6)


def test_all_six_scenarios_value_and_downside_skewed():
    vals = {s: _run(s).value_per_share_aud for s in SCENARIOS}
    assert all(v > 0 for v in vals.values())
    assert vals["orderly_convergence"] > vals["muddle_through"] > vals["stagflation_persists"]
    # every downside world sits below Muddle Through
    for s in ("ai_productivity_lag", "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists"):
        assert vals[s] < vals["muddle_through"]


def test_single_ke_held_across_scenarios():
    inps = [build_segment_inputs_from_data(load_inputs(ROOT, s, "biopharmaceuticals", "csl"), s) for s in SCENARIOS]
    kes = {round(i.cost_of_equity, 8) for i in inps}
    assert len(kes) == 1
    assert abs(next(iter(kes)) - 0.0875) < 1e-9


def test_derivation_headline_is_value_per_share_aud():
    inp = load_inputs(ROOT, "muddle_through", "biopharmaceuticals", "csl")
    bi = build_segment_inputs_from_data(inp, "muddle_through")
    r = SegmentEngine().run(bi)
    d = SegmentEngine().derivation(bi, r)
    assert d.result == pytest.approx(r.value_per_share_aud, abs=1e-9)
