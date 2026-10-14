"""D-79 (14 Oct 2026): WBC's and CSL's terminal growth is DERIVED, the D-72 way.

Before today the bank and segment engines read a typed per-scenario ``terminal_growth``
off the company file (WBC 3.25-3.75%, CSL 2.75-3.25%) while DNL's was derived from its
chain in equilibrium and capped at scenario nominal GDP. The typed rates sat about 2pp
below the nominal GDP the scenario files assert at year 10 (4.9-5.6%). Now:

* bank: ``bank_system_aiea_growth`` at year H (the industry gap and the scenario shift
  persist, like the mining gap) + the company offset at its D-78 equilibrium reading,
  capped at nominal GDP -- ``translator.bank_terminal_growth_from_data``;
* segments: each segment's archetype series at year H (the company offset is zero
  there by construction), weighted by final-year segment revenue, capped at nominal
  GDP -- ``translator.segment_terminal_growth_from_data``.

The pinned rates at the bottom are the sizing set ``terminal_growth_sets.yaml`` repeats.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from vcc_valuations.dcf.segment_engine import SegmentEngine
from vcc_valuations.schemas.industry import ChainTermRole
from vcc_valuations.translator import (
    bank_terminal_growth_from_data, build_bank_inputs_from_data,
    build_segment_inputs_from_data, equilibrium_chain_terms, load_inputs,
    macro_series_at, nominal_gdp_at, segment_archetype_growth_variable,
    segment_terminal_growth_from_data,
)

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = [
    "orderly_convergence", "muddle_through", "ai_productivity_lag",
    "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists",
]
H = 10


def _wbc(s):
    return load_inputs(ROOT, s, "australian_major_banks", "wbc")


def _csl(s):
    return load_inputs(ROOT, s, "biopharmaceuticals", "csl")


# ------------------------------------------------------------------ the data
def test_typed_terminal_growth_has_left_both_company_files():
    wbc = yaml.safe_load((ROOT / "data" / "companies" / "wbc.yaml").read_text(encoding="utf-8"))
    csl = yaml.safe_load((ROOT / "data" / "companies" / "csl.yaml").read_text(encoding="utf-8"))
    ov = wbc["normalised_baseline"]["bank_build"]["overlays"]
    assert "terminal_growth" not in ov["baseline"]
    assert all("terminal_growth" not in v for v in ov["by_scenario"].values())
    assert all("terminal_growth" not in v for v in csl["normalised_baseline"]["segment_fcff"]["by_scenario"].values())


def test_bank_archetype_classifies_every_chain_term_and_only_the_growth_offset_is_cyclical():
    eq = equilibrium_chain_terms(_wbc("muddle_through"))
    assert eq == {"company_offset.aiea_growth_offset": 0.0}


# ------------------------------------------------------------------ the bank
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_bank_terminal_growth_is_the_series_at_year_h_capped(scenario):
    inp = _wbc(scenario)
    d = bank_terminal_growth_from_data(inp, scenario, H)
    series = macro_series_at(inp, "bank_system_aiea_growth", H)
    assert d["offset_eq"].value == 0.0
    assert d.result == pytest.approx(min(series, nominal_gdp_at(inp, H)), abs=1e-12)
    assert build_bank_inputs_from_data(inp, scenario).terminal_growth == pytest.approx(d.result, abs=1e-12)


def test_bank_offset_classification_is_live():
    """Call WBC's share-loss offset equilibrium and g falls by the 15bp offset (uncapped scenario)."""
    inp = _wbc("muddle_through")
    arch = inp["archetype"].model_copy(deep=True)
    for t in arch.growth_chain_terms:
        if t.path == "company_offset.aiea_growth_offset":
            t.role = ChainTermRole.EQUILIBRIUM; t.equilibrium_value = None; t.basis = None
    before = bank_terminal_growth_from_data(inp, "muddle_through", H).result
    after = bank_terminal_growth_from_data(dict(inp, archetype=arch), "muddle_through", H).result
    assert after == pytest.approx(before - 0.0015, abs=1e-12)


# -------------------------------------------------------------- the segments
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_segment_terminal_growth_is_final_year_revenue_weighted_series_capped(scenario):
    inp = _csl(scenario)
    d = segment_terminal_growth_from_data(inp, scenario, H)
    si = build_segment_inputs_from_data(inp, scenario)
    res = SegmentEngine().run(si)
    num = tot = 0.0
    for seg in si.segments:
        rev_h = res.segment_revenue[seg.name][-1]          # the engine's own final-year revenue
        g_h = macro_series_at(inp, segment_archetype_growth_variable(inp, seg.name), H)
        assert d[f"rev_h[{seg.name}]"].value == pytest.approx(rev_h, rel=1e-9)
        num += rev_h * g_h; tot += rev_h
    assert d.result == pytest.approx(min(num / tot, nominal_gdp_at(inp, H)), abs=1e-12)
    assert si.terminal_growth == pytest.approx(d.result, abs=1e-12)


# ------------------------------------------------- the rates, to the basis point
def test_wbc_derived_rates():
    """Orderly is capped at nominal GDP; Stagflation's shrinking system is the floor."""
    got = {s: round(bank_terminal_growth_from_data(_wbc(s), s, H).result * 100, 2) for s in SCENARIOS}
    assert got == {
        "orderly_convergence": 5.37, "muddle_through": 4.50, "ai_productivity_lag": 4.42,
        "fragmentation": 3.92, "disorderly_climate_crystallisation": 3.46, "stagflation_persists": 1.94,
    }


def test_csl_derived_rates():
    """Orderly and Muddle Through are capped at nominal GDP (Vifor's share has grown by Y10)."""
    got = {s: round(segment_terminal_growth_from_data(_csl(s), s, H).result * 100, 2) for s in SCENARIOS}
    assert got == {
        "orderly_convergence": 5.37, "muddle_through": 5.37, "ai_productivity_lag": 4.86,
        "fragmentation": 3.90, "disorderly_climate_crystallisation": 3.85, "stagflation_persists": 2.73,
    }
