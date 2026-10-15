"""D-81 (15 Oct 2026): current-cycle chain terms expire INSIDE the explicit period.

Each term the archetype calls current_cycle declares ``expires_by_year``. Inside the
explicit period it glides linearly from its typed value (year 0, the base year) to its
``equilibrium_value`` at that year and holds there (``translator.chain_terms_at_year``).
The revenue-growth path is the full chain each year on those values, so by the final
explicit year it sits ON the equilibrium chain, the uncapped terminal growth. Where the
D-72 nominal-GDP cap binds, g sits below the final year and the step is disclosed, not
bridged. D-36's end-of-period fade and D-70's fade length are retired; nothing in code
names a company, a term or a year. The bank's company offset follows the same rule.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from vcc_valuations.schemas.industry import ChainTermRole, GrowthChainTerm
from vcc_valuations.translator import (
    bank_aiea_growth_path_from_data, build_engine_inputs_from_data, chain_terms_at_year,
    equilibrium_chain_terms, growth_chain_shared_block, load_inputs,
    revenue_growth_chain_from_data, revenue_growth_path_from_data, terminal_growth_from_data,
)
import vcc_valuations.translator as translator

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = sorted(p.stem for p in (ROOT / "data" / "scenarios").glob("*.yaml"))
ARCHETYPES = sorted(p.stem for p in (ROOT / "data" / "industries").glob("*.yaml"))


def _dnl(scenario="muddle_through"):
    return load_inputs(ROOT, scenario, "industrial_explosives", "dnl")


def _wbc(scenario="muddle_through"):
    return load_inputs(ROOT, scenario, "australian_major_banks", "wbc")


def _leaf(shared, path):
    node = shared
    for key in path.split("."):
        node = node[key]
    return float(node)


# ----------------------------------------------------------------- declaration

def test_an_equilibrium_term_may_not_carry_an_expiry():
    with pytest.raises(ValueError, match="expires_by_year"):
        GrowthChainTerm(path="x.y", role=ChainTermRole.EQUILIBRIUM, expires_by_year=5)


def test_an_expiry_must_be_a_positive_year():
    with pytest.raises(ValueError, match="expires_by_year"):
        GrowthChainTerm(path="x.y", role=ChainTermRole.CURRENT_CYCLE,
                        equilibrium_value=0.0, basis="b", expires_by_year=0)


@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_every_declared_current_cycle_term_carries_an_expiry_inside_ten_years(archetype):
    doc = yaml.safe_load((ROOT / "data" / "industries" / f"{archetype}.yaml").read_text(encoding="utf-8"))
    terms = doc["industry"].get("growth_chain_terms") if "industry" in doc else doc.get("growth_chain_terms")
    for t in terms or []:
        if t["role"] == "current_cycle":
            assert 1 <= t["expires_by_year"] <= 10, (archetype, t["path"])
        else:
            assert "expires_by_year" not in t, (archetype, t["path"])


def test_the_ratified_dnl_expiries():
    """Stephen's ruling, 15 Oct 2026: slow structural trends over the whole period,
    one-cycle terms over five years, the named project ramp over three."""
    exp = _dnl()["archetype"].chain_term_expiries
    ff = "company_offset.five_forces_offset."
    assert exp == {
        "industry_structure.volume_coefficient_a": 10,
        "industry_structure.volume_constant_b": 10,
        "industry_structure.productivity_sharing": 5,
        "company_offset.em_growth_premium": 10,
        ff + "rivalry_competitive_position": 5,
        ff + "rivalry_product_mix": 5,
        ff + "new_entrants_pipeline_uplift": 3,
        ff + "buyer_supplier_substitutes": 5,
    }


def test_the_ratified_wbc_expiry():
    """Stephen's ruling, 15 Oct 2026: the share-loss offset is one cycle, the same
    as the industrial chain's Five Forces offsets."""
    assert _wbc()["archetype"].chain_term_expiries == {"company_offset.aiea_growth_offset": 5}


# ------------------------------------------------------------------ the glide

def test_terms_glide_linearly_from_typed_to_equilibrium_and_hold():
    inp = _dnl()
    shared = growth_chain_shared_block(inp)
    eq = equilibrium_chain_terms(inp)
    expiries = inp["archetype"].chain_term_expiries
    assert set(chain_terms_at_year(inp, 1)) == set(eq)
    for path, eq_value in eq.items():
        typed = _leaf(shared, path)
        n = expiries[path]
        assert chain_terms_at_year(inp, 0)[path] == pytest.approx(typed)
        assert chain_terms_at_year(inp, n)[path] == pytest.approx(eq_value)
        assert chain_terms_at_year(inp, n + 3)[path] == pytest.approx(eq_value)
        mid = chain_terms_at_year(inp, n / 2)[path]
        assert mid == pytest.approx(typed + (eq_value - typed) / 2)


def test_the_pipeline_uplift_is_gone_by_year_three_and_the_beta_is_still_gliding():
    inp = _dnl()
    at3 = chain_terms_at_year(inp, 3)
    assert at3["company_offset.five_forces_offset.new_entrants_pipeline_uplift"] == 0.0
    assert 1.0 < at3["industry_structure.volume_coefficient_a"] < 1.15


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_the_path_is_the_full_chain_on_each_years_terms(scenario):
    inp = _dnl(scenario)
    path = revenue_growth_path_from_data(inp, scenario, 10)
    assert len(path) == 10
    for k in range(1, 11):
        want = revenue_growth_chain_from_data(
            inp, scenario, year=k, term_values=chain_terms_at_year(inp, k)).result
        assert path[k - 1] == pytest.approx(want, abs=1e-15)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_the_final_year_lands_on_the_equilibrium_chain_and_g_is_the_capped_version(scenario):
    """No fade: year 10 IS the equilibrium chain. g = min(year 10, nominal GDP)."""
    inp = _dnl(scenario)
    path = revenue_growth_path_from_data(inp, scenario, 10)
    tg = terminal_growth_from_data(inp, scenario, 10)
    assert path[-1] == pytest.approx(tg["g_chain"].value, abs=1e-12)
    assert tg.result == pytest.approx(min(path[-1], tg["g_cap"].value), abs=1e-12)
    assert path[-1] >= tg.result - 1e-12


def test_the_cap_step_at_the_boundary_is_disclosed_not_bridged():
    """Orderly Convergence is the one scenario where the cap gap is material: the
    equilibrium chain (6.04%) exceeds nominal GDP (5.06%), so year 10 sits a point
    above g. Pinned so the next move is read, not absorbed."""
    inp = _dnl("orderly_convergence")
    path = revenue_growth_path_from_data(inp, "orderly_convergence", 10)
    tg = terminal_growth_from_data(inp, "orderly_convergence", 10)
    assert tg["g_cap"].value < tg["g_chain"].value
    assert path[-1] - tg.result == pytest.approx(0.0098, abs=5e-4)
    mt = _dnl("muddle_through")
    mt_path = revenue_growth_path_from_data(mt, "muddle_through", 10)
    mt_tg = terminal_growth_from_data(mt, "muddle_through", 10)
    assert mt_path[-1] - mt_tg.result == pytest.approx(0.0005, abs=2e-4)


def test_muddle_through_path_declines_monotonically_as_the_extras_glide_off():
    path = revenue_growth_path_from_data(_dnl(), "muddle_through", 10)
    assert all(a > b for a, b in zip(path, path[1:]))
    assert path[0] == pytest.approx(0.0635, abs=5e-4)
    assert path[-1] == pytest.approx(0.0491, abs=5e-4)


def test_an_expiry_past_the_horizon_raises():
    inp = _dnl()
    arch = inp["archetype"].model_copy(deep=True)
    for t in arch.growth_chain_terms:
        if t.path == "industry_structure.volume_coefficient_a":
            t.expires_by_year = 12
    with pytest.raises(ValueError, match="expire after the explicit period"):
        revenue_growth_path_from_data(dict(inp, archetype=arch), "muddle_through", 10)


def test_equilibrium_and_term_values_are_exclusive():
    inp = _dnl()
    with pytest.raises(ValueError, match="not both"):
        revenue_growth_chain_from_data(inp, "muddle_through", year=1, equilibrium=True,
                                       term_values=chain_terms_at_year(inp, 1))


# ------------------------------------------------------------ the fade is gone

def test_the_fade_is_retired():
    assert not hasattr(translator, "fade_period_length_from_data")
    assert "fade_period_length" not in translator.QUALITATIVE_DRIVER_RULES if hasattr(translator, "QUALITATIVE_DRIVER_RULES") else True
    dnl = yaml.safe_load((ROOT / "data" / "companies" / "dnl.yaml").read_text(encoding="utf-8"))
    for sid, ov in dnl["normalised_baseline"]["engine_overlays"]["by_scenario"].items():
        assert "fade_period_length_years" not in ov, sid
    matrix = (ROOT / "data" / "impact_matrix" / "by_industry" / "industrial_explosives.yaml").read_text(encoding="utf-8")
    assert "fade_period_length:" not in matrix


def test_the_engine_inputs_carry_the_glided_path():
    inp = _dnl()
    ei = build_engine_inputs_from_data(inp, "muddle_through")
    assert list(ei.revenue_growth) == pytest.approx(revenue_growth_path_from_data(inp, "muddle_through", 10))


# ------------------------------------------------------------------ the bank

def test_the_bank_offset_follows_the_same_rule():
    inp = _wbc()
    shared = growth_chain_shared_block(inp)
    typed = shared["company_offset"]["aiea_growth_offset"]
    assert typed < 0
    path = bank_aiea_growth_path_from_data(inp, 10)
    series = [translator.macro_series_at(inp, "bank_system_aiea_growth", y) for y in range(1, 11)]
    offsets = [p - s for p, s in zip(path, series)]
    assert offsets[0] == pytest.approx(typed * 0.8)
    assert offsets[4] == pytest.approx(0.0, abs=1e-15)
    assert all(abs(o) < 1e-15 for o in offsets[5:])
