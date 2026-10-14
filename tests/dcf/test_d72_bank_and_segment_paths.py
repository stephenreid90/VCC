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
def test_bank_muddle_through_path_is_the_old_flat_rate():
    inp = _wbc("muddle_through")
    shared = inp["company_raw"]["normalised_baseline"]["bank_build"]["aiea_nim_chain"]["shared"]
    flat = shared["industry"]["aiea_growth"] + shared["company_offset"]["aiea_growth_offset"]
    assert bank_aiea_growth_path_from_data(inp, 5) == pytest.approx([flat] * 5)


@pytest.mark.parametrize("s", SCENARIOS)
def test_bank_path_is_scenario_series_plus_company_offset_per_year(s):
    inp = _wbc(s)
    offset = inp["company_raw"]["normalised_baseline"]["bank_build"]["aiea_nim_chain"]["shared"]["company_offset"]["aiea_growth_offset"]
    path = bank_aiea_growth_path_from_data(inp, 5)
    assert path == pytest.approx([macro_series_at(inp, "bank_system_aiea_growth", y) + offset for y in range(1, 6)])
    bi = build_bank_inputs_from_data(inp, s)
    assert BankEngine.aiea_growth_path(bi) == pytest.approx(path)


def test_bank_engine_still_accepts_a_scalar_and_holds_it_flat():
    bi = build_bank_inputs_from_data(_wbc("muddle_through"), "muddle_through")
    flat = BankEngine.aiea_growth_path(bi)[0]
    scalar = BankInputs(**{**bi.__dict__, "aiea_growth": flat})
    assert BankEngine().run(scalar).value_per_share == pytest.approx(BankEngine().run(bi).value_per_share, abs=1e-9)


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


def test_muddle_through_segment_paths_are_the_typed_paths():
    inp = _csl("muddle_through")
    scen = inp["company_raw"]["normalised_baseline"]["segment_fcff"]["by_scenario"]["muddle_through"]
    assert segment_growth_path_from_data(inp, "muddle_through", "csl_behring", 5) == pytest.approx(scen["behring_growth"], abs=1e-9)
    assert segment_growth_path_from_data(inp, "muddle_through", "csl_seqirus", 5) == pytest.approx([scen["seqirus_cagr"]] * 6, abs=1e-9)
    assert segment_growth_path_from_data(inp, "muddle_through", "csl_vifor", 5) == pytest.approx([scen["vifor_cagr"]] * 6, abs=1e-9)


@pytest.mark.parametrize("s", SCENARIOS)
def test_behring_j_curve_offset_survives_in_every_scenario(s):
    """The offset is the typed path less its steady state, so the recovery shape is scenario-invariant."""
    inp = _csl(s)
    scen = inp["company_raw"]["normalised_baseline"]["segment_fcff"]["by_scenario"][s]
    typed = scen["behring_growth"]
    path = segment_growth_path_from_data(inp, s, "csl_behring", 5)
    series = [macro_series_at(inp, SEGMENTS["csl_behring"], t + 1) for t in range(6)]
    assert [p - x for p, x in zip(path, series)] == pytest.approx([g - typed[-1] for g in typed], abs=1e-12)
    assert path[-1] == pytest.approx(series[-1])      # steady state = the archetype series


@pytest.mark.parametrize("s", SCENARIOS)
def test_a_flat_cagr_segment_carries_no_company_offset(s):
    inp = _csl(s)
    for seg in ("csl_seqirus", "csl_vifor"):
        path = segment_growth_path_from_data(inp, s, seg, 5)
        assert path == pytest.approx([macro_series_at(inp, SEGMENTS[seg], t + 1) for t in range(6)])
