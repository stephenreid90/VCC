"""D-72: every archetype's derived macro-driver paths regenerate from their declarations.

Standing rule 4. ``scripts/derive_macro_driver_paths.py`` reads each archetype's
``required_macro_drivers`` declarations and writes the derived series into every
scenario file. This asserts (a) the committed series are exactly what the
declarations produce, for EVERY archetype that declares a derived driver -- so a
hand edit to either side fails here rather than silently drifting; (b) each
derivation method does what its name says, once, on a synthetic declaration;
and (c) the DNL-specific rulings of 2 Oct 2026 still hold on the explosives data
(spread not multiple; transition-then-baseline; AI Lag gas baseline-by-absence).

Generalised 14 Oct 2026 (bridge note step 1): nothing in the generic half names
a company or a driver.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from derive_macro_driver_paths import (  # noqa: E402
    ANCHOR_YEARS, METHODS, SCENARIOS, archetypes, derive, derived_variables, interpolate, level_anchor,
)
from vcc_valuations.schemas.industry import (  # noqa: E402
    AnchorTerm, DerivationMethod, IndustryArchetype, LevelAnchor, MacroDriverDerivation, RequiredMacroDriver,
)

PERCENT = 100.0  # ssot-allow


def _committed(scenario_id, variable):
    doc = yaml.safe_load((ROOT / "data" / "scenarios" / f"{scenario_id}.yaml").read_text(encoding="utf-8"))
    for mv in doc["scenario"]["macro_variables"]:
        if mv["variable"] == variable:
            return [(p["year"], p["value"]) for p in mv["time_series"]]
    raise KeyError((scenario_id, variable))


ARCHETYPES = {a.id: a for a in archetypes()}
DERIVING = sorted(a for a in ARCHETYPES if derived_variables(ARCHETYPES[a]))
PAIRS = [(a, v) for a in DERIVING for v in derived_variables(ARCHETYPES[a])]


# ------------------------------------------------------------ (a) generic ratchet
def test_at_least_one_archetype_declares_a_derived_driver():
    assert DERIVING, "no archetype declares a derived macro driver -- the derivation is dead code"


@pytest.mark.parametrize("scenario_id", SCENARIOS)
@pytest.mark.parametrize("archetype_id,variable", PAIRS)
def test_committed_series_equal_the_declared_derivation(archetype_id, variable, scenario_id):
    series, _ = derive(ARCHETYPES[archetype_id], scenario_id)[variable]
    assert _committed(scenario_id, variable) == series, (
        "data/scenarios/%s.yaml %s is stale -- rerun "
        "`PYTHONPATH=src python scripts/derive_macro_driver_paths.py --write`"
        % (scenario_id, variable)
    )


@pytest.mark.parametrize("scenario_id", SCENARIOS)
@pytest.mark.parametrize("archetype_id,variable", PAIRS)
def test_series_sit_on_d37_anchor_years(archetype_id, variable, scenario_id):
    assert [y for y, _ in _committed(scenario_id, variable)] == list(ANCHOR_YEARS)


def test_every_declared_method_is_implemented():
    """A method in the enum without an implementation would validate and then crash at derive time."""
    for m in DerivationMethod:
        if m is DerivationMethod.SCENARIO_SERIES:
            continue
        assert m in METHODS, m


def test_scenario_series_drivers_are_native_to_every_scenario_file():
    """``scenario_series`` means the scenario carries it; check 14 would catch it, but say it here too."""
    for a in ARCHETYPES.values():
        for d in a.required_macro_drivers:
            if d.is_derived:
                continue
            for s in SCENARIOS:
                _committed(s, d.variable)


# ------------------------------------------------------------ (b) one test per method
def _synthetic(method, **kw):
    decl = RequiredMacroDriver(variable="probe", derivation=MacroDriverDerivation(method=method, **kw))
    return decl


def test_spread_adds_a_fixed_gap_whose_mean_hits_the_anchor():
    anchor = LevelAnchor(company="dnl",
                         path="normalised_baseline.revenue_growth_chain.by_scenario.{scenario}.macro.global_mining_real_growth")
    decl = _synthetic(DerivationMethod.SPREAD, series="real_gdp_growth_world", anchor=anchor)
    for s in SCENARIOS:
        series, _ = METHODS[DerivationMethod.SPREAD](decl, s)
        assert sum(v for _, v in series) / len(series) == pytest.approx(level_anchor(anchor, s), abs=0.011)
        # a spread keeps the base series' shape: differences between anchor years are preserved
        base_pts = [{"year": y, "value": v} for y, v in _committed(s, "real_gdp_growth_world")]
        base = [interpolate(base_pts, y) for y in ANCHOR_YEARS]
        gaps = {round(v - b, 2) for (_, v), b in zip(series, base)}
        assert len(gaps) == 1, (s, gaps)


def test_transition_then_baseline_switches_at_the_equilibrium_year():
    anchor = LevelAnchor(company="dnl",
                         path="normalised_baseline.revenue_growth_chain.by_scenario.{scenario}.macro.gas_price_growth")
    decl = _synthetic(DerivationMethod.TRANSITION_THEN_BASELINE, anchor=anchor, baseline_scenario="muddle_through")
    for s in SCENARIOS:
        doc = yaml.safe_load((ROOT / "data" / "scenarios" / f"{s}.yaml").read_text(encoding="utf-8"))["scenario"]
        eq = max(p["year_start"] for p in doc["time_profile"])
        series, _ = METHODS[DerivationMethod.TRANSITION_THEN_BASELINE](decl, s)
        for year, value in series:
            expect = level_anchor(anchor, s) if year < eq else level_anchor(anchor, "muddle_through")
            assert value == pytest.approx(expect), (s, year)


def test_scenario_series_derives_nothing():
    a = IndustryArchetype.model_validate({
        **ARCHETYPES[DERIVING[0]].model_dump(mode="json"),
        "required_macro_drivers": ["cpi_inflation_advanced"],
    })
    assert derived_variables(a) == []
    assert derive(a, SCENARIOS[0]) == {}


def test_bare_name_means_scenario_series():
    a = IndustryArchetype.model_validate({
        **ARCHETYPES[DERIVING[0]].model_dump(mode="json"),
        "required_macro_drivers": ["cpi_inflation_advanced"],
    })
    d = a.required_macro_drivers[0]
    assert d.variable == "cpi_inflation_advanced"
    assert d.derivation.method is DerivationMethod.SCENARIO_SERIES
    assert a.required_macro_driver_names == ["cpi_inflation_advanced"]


@pytest.mark.parametrize("bad", [
    dict(method="spread"),                                   # missing series + anchor
    dict(method="spread", series="x"),                       # missing anchor
    dict(method="transition_then_baseline", anchor={"company": "dnl", "path": "p"}),  # missing baseline
    dict(method="scenario_series", series="x"),              # extra field for a native series
])
def test_a_declaration_missing_or_carrying_the_wrong_fields_is_rejected(bad):
    with pytest.raises(Exception):
        MacroDriverDerivation.model_validate(bad)


def test_spread_over_a_sum_of_series_is_the_sum_of_the_bases_plus_one_gap():
    """A list of base series is summed (real GDP + CPI = nominal GDP) before the gap is added."""
    anchor = LevelAnchor(company="wbc", terms=[
        AnchorTerm(path="normalised_baseline.bank_build.aiea_nim_chain.shared.industry.aiea_growth"),
        AnchorTerm(path="normalised_baseline.bank_build.aiea_nim_chain.by_scenario.{scenario}.aiea_growth_delta"),
    ])
    decl = _synthetic(DerivationMethod.SPREAD, series=["real_gdp_growth_world", "cpi_inflation_advanced"], anchor=anchor)
    for s in SCENARIOS:
        series, _ = METHODS[DerivationMethod.SPREAD](decl, s)
        gdp = [{"year": y, "value": v} for y, v in _committed(s, "real_gdp_growth_world")]
        cpi = [{"year": y, "value": v} for y, v in _committed(s, "cpi_inflation_advanced")]
        base = [interpolate(gdp, y) + interpolate(cpi, y) for y in ANCHOR_YEARS]
        gaps = {round(v - b, 2) for (_, v), b in zip(series, base)}
        assert len(gaps) == 1, (s, gaps)
        assert sum(v for _, v in series) / len(series) == pytest.approx(level_anchor(anchor, s), abs=0.011)


def test_anchor_terms_are_summed_in_percent_with_their_declared_units():
    """decimal 0.045 + bps 50 = 5.0 percent; a list index picks one element of a typed path."""
    # D-91 (16 Oct 2026): nim_delta_bps is zero everywhere, so the bps term here is the
    # credit-loss shift (+50bp in Stagflation); the arithmetic under test is the same.
    bank = LevelAnchor(company="wbc", terms=[
        AnchorTerm(path="normalised_baseline.bank_build.aiea_nim_chain.shared.industry.nim_anchor"),
        AnchorTerm(path="normalised_baseline.bank_build.overlays.by_scenario.{scenario}.credit_loss_delta_bps", units="bps"),
    ])
    assert level_anchor(bank, "stagflation_persists") == pytest.approx(1.86 + 0.50)
    assert level_anchor(bank, "muddle_through") == pytest.approx(1.86)
    behring = LevelAnchor(company="csl", path="normalised_baseline.segment_fcff.by_scenario.{scenario}.behring_growth[-1]")
    assert level_anchor(behring, "muddle_through") == pytest.approx(5.5)


def test_unknown_anchor_units_are_rejected():
    with pytest.raises(Exception):
        AnchorTerm(path="x", units="per_mille")
    with pytest.raises(Exception):
        LevelAnchor(company="x")  # neither path nor terms
    with pytest.raises(Exception):
        LevelAnchor(company="x", path="a", terms=[AnchorTerm(path="b")])  # both


# ------------------------------------------------------------ (c) the DNL rulings of 2 Oct 2026
EXPLOSIVES = "industrial_explosives"


def _dnl_anchor(variable, scenario_id):
    return level_anchor(LevelAnchor(
        company="dnl",
        path=f"normalised_baseline.revenue_growth_chain.by_scenario.{{scenario}}.macro.{variable}"), scenario_id)


def test_explosives_declares_exactly_the_chains_three_drivers():
    a = ARCHETYPES[EXPLOSIVES]
    assert a.required_macro_driver_names == ["global_mining_real_growth", "cpi_inflation_advanced", "gas_price_growth"]
    assert derived_variables(a) == ["global_mining_real_growth", "gas_price_growth"]


def test_a_multiple_would_hold_stagflation_at_zero_forever():
    """Why decision 2 is a spread: the Stagflation anchor is 0.0%, and 0 x anything is 0."""
    assert _dnl_anchor("global_mining_real_growth", "stagflation_persists") == 0.0
    series = _committed("stagflation_persists", "global_mining_real_growth")
    assert min(v for _, v in series) < 0 < max(v for _, v in series)


def test_ai_lag_gas_is_the_baseline_by_absence_not_by_view():
    """The AI Lag write-up never assessed gas (gap audit §2); its anchor equals the baseline."""
    assert _dnl_anchor("gas_price_growth", "ai_productivity_lag") == _dnl_anchor("gas_price_growth", "muddle_through")


# ------------------------------------------------------------ (d) the WBC / CSL declarations of 14 Oct 2026
def test_bank_declares_balance_sheet_growth_only_and_not_nim():
    """NIM is held back: a pass-through of 1 from the policy rate is not defensible (archetype comment)."""
    a = ARCHETYPES["australian_major_banks"]
    assert a.required_macro_driver_names == ["bank_system_aiea_growth"]
    assert a.required_macro_drivers[0].derivation.series == ["real_gdp_growth_world", "cpi_inflation_advanced"]


def test_each_csl_segment_archetype_declares_one_nominal_growth_path():
    for arch, var in [("plasma_derived_therapies", "plasma_therapies_nominal_growth"),
                      ("vaccines", "seasonal_vaccines_nominal_growth"),
                      ("specialty_pharmaceuticals", "specialty_pharma_nominal_growth")]:
        a = ARCHETYPES[arch]
        assert a.required_macro_driver_names == [var], arch
        # one NOMINAL series, not a typed volume/price split (archetype comment).
        # 15 Oct 2026 (item (c)): the volume driver is US real GDP.
        assert a.required_macro_drivers[0].derivation.series == ["real_gdp_growth_us", "cpi_inflation_advanced"]


def test_muddle_through_paths_average_to_the_typed_steady_states():
    """The fixed gap is set so the path's mean over the anchor years IS the typed anchor.

    Until D-80 (14 Oct 2026) Muddle Through's world series were flat, so the path
    was flat at the anchor. D-80 lowered year-10 CPI to 2.5%, so the base slopes
    down from year 5 and the path with it (bank: 4.64 early, 4.14 at year 10,
    mean 4.5). The explicit years run a little above the anchor and the terminal a
    little below -- higher inflation early means faster nominal growth early."""
    def mean(var):
        vals = [v for _, v in _committed("muddle_through", var)]
        return sum(vals) / len(vals)
    assert mean("bank_system_aiea_growth") == pytest.approx(4.5, abs=0.01)
    assert mean("plasma_therapies_nominal_growth") == pytest.approx(5.5, abs=0.01)
    assert mean("seasonal_vaccines_nominal_growth") == pytest.approx(2.0, abs=0.01)
    assert mean("specialty_pharma_nominal_growth") == pytest.approx(7.0, abs=0.01)
    # and it is no longer flat: the year-10 point sits below the year-1 point
    pts = dict(_committed("muddle_through", "bank_system_aiea_growth"))
    assert pts[10] < pts[1]


# ------------------------------------------------- (d) scenario-level base series (R16-5)
from derive_macro_driver_paths import derive_scenario_series, scenario_derivations  # noqa: E402

SCENARIO_DERIVED = [(s, d["variable"]) for s in SCENARIOS for d in scenario_derivations(s)]


def test_r16_5_the_two_flat_offset_us_paths_are_declared_not_typed():
    """R16-5 (16 Oct 2026): AI Lag (+0.2pp) and Disorderly Climate (-0.3pp) were the two
    US paths typed as flat offsets from the world path. They are now produced from it.
    The other four US paths are distinct series Stephen approved on 15 Oct (D-82) and
    stay typed on purpose."""
    assert sorted(SCENARIO_DERIVED) == [
        ("ai_productivity_lag", "real_gdp_growth_us"),
        ("disorderly_climate_crystallisation", "real_gdp_growth_us"),
    ]


@pytest.mark.parametrize("scenario_id,variable", SCENARIO_DERIVED)
def test_committed_scenario_series_equal_the_declaration(scenario_id, variable):
    series, _ = derive_scenario_series(scenario_id)[variable]
    assert _committed(scenario_id, variable) == series, (
        "data/scenarios/%s.yaml %s is stale -- rerun "
        "`PYTHONPATH=src python scripts/derive_macro_driver_paths.py --write`"
        % (scenario_id, variable)
    )


@pytest.mark.parametrize("scenario_id,variable", SCENARIO_DERIVED)
def test_a_declared_scenario_series_appears_exactly_once(scenario_id, variable):
    doc = yaml.safe_load((ROOT / "data" / "scenarios" / f"{scenario_id}.yaml").read_text(encoding="utf-8"))
    hits = [mv for mv in doc["scenario"]["macro_variables"] if mv["variable"] == variable]
    assert len(hits) == 1, "a typed copy survives beside the produced one"
