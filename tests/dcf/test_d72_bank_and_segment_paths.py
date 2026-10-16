"""D-72 for the bank and segment archetypes (14 Oct 2026): WBC and CSL read the scenario paths.

The same shape DNL already had: growth inside the explicit period comes from the
scenario's own year-by-year series (declared by the archetype, derived into the
scenario files) plus a company offset that lives in the company layer. Pins:

1. Muddle Through reproduces the typed rates exactly -- its world series are flat,
   so the path IS the old flat anchor (the base ties cannot move).
2. The company offset is the typed path less its own steady state, so Behring's
   J-curve survives in every scenario and a flat CAGR carries no offset.
3. The bank path is the scenario series plus WBC's Five Forces offset, per year.
4. A segment archetype must declare exactly ONE growth driver; nothing is picked.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vcc_valuations.dcf.bank_engine import BankEngine, BankInputs
from vcc_valuations.translator import (
    chain_terms_at_year,
    bank_aiea_growth_path_from_data, build_bank_inputs_from_data, load_inputs,
    macro_series_at, segment_archetype_growth_variable, segment_growth_path_from_data,
)

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = ["muddle_through", "orderly_convergence", "ai_productivity_lag",
             "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists"]


def _wbc(s):
    return load_inputs(ROOT, s, "australian_major_banks", "wbc")


def _csl(s):
    return load_inputs(ROOT, s, "biopharmaceuticals", "csl")


# ------------------------------------------------------------------ bank
def test_bank_muddle_through_path_averages_to_the_old_flat_rate():
    """D-80 (14 Oct 2026): Muddle Through's CPI slopes down to year 10, so the path is
    no longer flat; the D-72 gap keeps its mean over the anchor years (1, 3, 5, 7, 10)
    at the typed industry rate plus the company offset."""
    inp = _wbc("muddle_through")
    # R16-6: the industry anchor sits in the bank archetype, not in WBC's file; Muddle
    # Through's own shift is zero, so the anchor IS the old flat rate.
    flat = sum(t.archetype_value("muddle_through") for t in inp["archetype"].driver_anchor("bank_system_aiea_growth").terms)
    # D-81: the company offset now glides to zero by its expiry year, so the
    # identity is struck on the INDUSTRY series alone (path minus the year's offset).
    path = bank_aiea_growth_path_from_data(inp, 10)
    industry = [path[y - 1] - chain_terms_at_year(inp, y).get("company_offset.aiea_growth_offset") for y in range(1, 11)]
    at_anchors = [industry[y - 1] for y in (1, 3, 5, 7, 10)]
    assert sum(at_anchors) / len(at_anchors) == pytest.approx(flat, abs=1e-4)
    assert industry[9] < industry[0]


@pytest.mark.parametrize("s", SCENARIOS)
def test_bank_path_is_scenario_series_plus_company_offset_per_year(s):
    inp = _wbc(s)
    typed = inp["company_raw"]["normalised_baseline"]["bank_build"]["aiea_nim_chain"]["shared"]["company_offset"]["aiea_growth_offset"]
    path = bank_aiea_growth_path_from_data(inp, 10)
    # D-81: the offset at year y is its typed value glided linearly to its
    # equilibrium value (zero) by the archetype's expires_by_year (5), then held.
    expiry = inp["archetype"].chain_term_expiries["company_offset.aiea_growth_offset"]
    offsets = [typed * (1 - min(1.0, y / expiry)) for y in range(1, 11)]
    assert offsets[expiry - 1] == 0.0 and offsets[0] == pytest.approx(typed * (1 - 1 / expiry))
    assert path == pytest.approx([macro_series_at(inp, "bank_system_aiea_growth", y) + offsets[y - 1] for y in range(1, 11)])
    bi = build_bank_inputs_from_data(inp, s)
    assert BankEngine.aiea_growth_path(bi) == pytest.approx(path)


def test_bank_engine_still_accepts_a_scalar_and_holds_it_flat():
    bi = build_bank_inputs_from_data(_wbc("muddle_through"), "muddle_through")
    flat = BankEngine.aiea_growth_path(bi)[0]
    scalar = BankInputs(**{**bi.__dict__, "aiea_growth": flat})
    as_list = BankInputs(**{**bi.__dict__, "aiea_growth": [flat] * 10})
    assert BankEngine().run(scalar).value_per_share == pytest.approx(BankEngine().run(as_list).value_per_share, abs=1e-9)


def test_bank_path_of_the_wrong_length_is_rejected():
    bi = build_bank_inputs_from_data(_wbc("muddle_through"), "muddle_through")
    bad = BankInputs(**{**bi.__dict__, "aiea_growth": [0.04, 0.04]})
    with pytest.raises(ValueError):
        BankEngine().run(bad)


# --------------------------------------------------------------- segments
SEGMENTS = {"csl_behring": "plasma_therapies_nominal_growth",
            "csl_seqirus": "seasonal_vaccines_nominal_growth",
            "csl_vifor": "specialty_pharma_nominal_growth"}


@pytest.mark.parametrize("seg,var", sorted(SEGMENTS.items()))
def test_each_segment_reads_its_own_archetypes_single_declared_series(seg, var):
    assert segment_archetype_growth_variable(_csl("muddle_through"), seg) == var


def test_muddle_through_segment_paths_average_to_the_typed_paths():
    """D-80 (14 Oct 2026): Muddle Through's CPI slopes down to year 10, so the segment
    series are no longer flat at the typed rate; the D-72 gap keeps each series' mean
    over the anchor years (1, 3, 5, 7, 10) at the typed steady state, and the Behring
    J-curve offset rides on top unchanged."""
    inp = _csl("muddle_through")
    scen = inp["company_raw"]["normalised_baseline"]["segment_fcff"]["by_scenario"]["muddle_through"]
    def anchor_mean(path):  # path[0] is year 1
        pts = [path[y - 1] for y in (1, 3, 5, 7, 10)]
        return sum(pts) / len(pts)
    # D-71: ten years; the typed Behring path (FY26..FY31) holds its steady state to FY36
    typed = scen["behring_growth"]
    behring = segment_growth_path_from_data(inp, "muddle_through", "csl_behring", 10)
    series_only = [b - (t - typed[-1]) for b, t in zip(behring, typed + [typed[-1]] * 5)]
    assert anchor_mean(series_only) == pytest.approx(typed[-1], abs=1e-4)
    assert anchor_mean(segment_growth_path_from_data(inp, "muddle_through", "csl_seqirus", 10)) == pytest.approx(scen["seqirus_cagr"], abs=1e-4)
    assert anchor_mean(segment_growth_path_from_data(inp, "muddle_through", "csl_vifor", 10)) == pytest.approx(scen["vifor_cagr"], abs=1e-4)


@pytest.mark.parametrize("s", SCENARIOS)
def test_behring_j_curve_offset_survives_in_every_scenario(s):
    """The offset is the typed path less its steady state, so the recovery shape is scenario-invariant."""
    inp = _csl(s)
    scen = inp["company_raw"]["normalised_baseline"]["segment_fcff"]["by_scenario"][s]
    typed = scen["behring_growth"]; typed = typed + [typed[-1]] * (11 - len(typed))
    path = segment_growth_path_from_data(inp, s, "csl_behring", 10)
    series = [macro_series_at(inp, SEGMENTS["csl_behring"], t + 1) for t in range(11)]
    assert [p - x for p, x in zip(path, series)] == pytest.approx([g - typed[-1] for g in typed], abs=1e-12)
    assert path[-1] == pytest.approx(series[-1])      # steady state = the archetype series


@pytest.mark.parametrize("s", SCENARIOS)
def test_a_flat_cagr_segment_carries_no_company_offset(s):
    inp = _csl(s)
    for seg in ("csl_seqirus", "csl_vifor"):
        path = segment_growth_path_from_data(inp, s, seg, 10)
        assert path == pytest.approx([macro_series_at(inp, SEGMENTS[seg], t + 1) for t in range(11)])
