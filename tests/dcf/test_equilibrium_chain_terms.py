"""D-78 (14 Oct 2026, bridge note step 4): the equilibrium reading of the growth chain is
the ARCHETYPE's declaration, not a list of term names in code.

``growth_chain_terms`` in ``data/industries/<archetype>.yaml`` says, for every term of
the company's growth chain, whether it is current_cycle (switched off at the end of the
explicit period for the reading that sets terminal growth, D-72) or equilibrium
(persists). ``translator.equilibrium_chain_terms`` reads it; an unclassified term raises.

What the data path carries today: industrial_explosives classifies all ten DNL terms
(ratified by Stephen 14 Oct 2026 as the classification D-72 implemented, so no level
moves); the bank and the three CSL segment archetypes declare an EMPTY list, because
WBC's and CSL's terminal growth is still typed per scenario, not derived.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from vcc_valuations.schemas.industry import (
    ChainTermRole, GrowthChainTerm, IndustryArchetypeFile,
)
from vcc_valuations.translator import (
    equilibrium_chain_terms, load_inputs, revenue_growth_chain_from_data,
    terminal_growth_from_data,
)

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = [
    "orderly_convergence", "muddle_through", "ai_productivity_lag",
    "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists",
]
ARCHETYPES = sorted(p.stem for p in (ROOT / "data" / "industries").glob("*.yaml"))


def _inputs(scenario="muddle_through"):
    return load_inputs(ROOT, scenario, "industrial_explosives", "dnl")


# --------------------------------------------------------------- generic half
@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_every_archetype_has_answered_the_equilibrium_question(archetype):
    doc = yaml.safe_load((ROOT / "data" / "industries" / f"{archetype}.yaml").read_text(encoding="utf-8"))
    a = IndustryArchetypeFile.model_validate(doc).industry_archetype
    assert a.growth_chain_terms is not None, f"{archetype}: growth_chain_terms not declared (D-78)"


def test_a_current_cycle_term_needs_its_off_value_and_a_basis():
    with pytest.raises(ValueError):
        GrowthChainTerm(path="x.y", role=ChainTermRole.CURRENT_CYCLE)
    with pytest.raises(ValueError):
        GrowthChainTerm(path="x.y", role=ChainTermRole.EQUILIBRIUM, equilibrium_value=0.0)
    ok = GrowthChainTerm(path="x.y", role=ChainTermRole.CURRENT_CYCLE, equilibrium_value=1.0, basis="b")
    assert ok.equilibrium_value == 1.0


def test_an_unclassified_chain_term_raises():
    inp = _inputs()
    inp = dict(inp, company_raw=copy.deepcopy(inp["company_raw"]))
    inp["company_raw"]["normalised_baseline"]["revenue_growth_chain"]["shared"]["industry_structure"]["new_term"] = 0.01
    with pytest.raises(ValueError, match="unclassified"):
        equilibrium_chain_terms(inp)


def test_a_declared_term_absent_from_the_chain_raises():
    inp = _inputs()
    arch = inp["archetype"].model_copy(deep=True)
    arch.growth_chain_terms.append(GrowthChainTerm(path="industry_structure.ghost", role=ChainTermRole.EQUILIBRIUM))
    with pytest.raises(ValueError, match="absent from the chain"):
        equilibrium_chain_terms(dict(inp, archetype=arch))


def test_a_company_with_a_chain_and_an_archetype_that_has_not_answered_raises():
    inp = _inputs()
    arch = inp["archetype"].model_copy(deep=True)
    arch.growth_chain_terms = None
    with pytest.raises(ValueError, match="D-78"):
        equilibrium_chain_terms(dict(inp, archetype=arch))


def test_reclassifying_a_term_moves_the_equilibrium_reading():
    """The declaration is live: call the inflation weight current-cycle at 0 and g falls."""
    inp = _inputs()
    before = revenue_growth_chain_from_data(inp, "muddle_through", year=10, equilibrium=True).result
    arch = inp["archetype"].model_copy(deep=True)
    for t in arch.growth_chain_terms:
        if t.path == "industry_structure.pricing_weight_inflation":
            t.role = ChainTermRole.CURRENT_CYCLE; t.equilibrium_value = 0.0; t.basis = "test"
    after = revenue_growth_chain_from_data(dict(inp, archetype=arch), "muddle_through", year=10, equilibrium=True).result
    assert after < before - 0.01


# ------------------------------------------------------------ DNL data today
def test_dnl_classification_is_the_one_d72_implemented():
    eq = equilibrium_chain_terms(_inputs())
    assert eq == {
        "industry_structure.volume_coefficient_a": 1.0,
        "industry_structure.volume_constant_b": 0.0,
        "industry_structure.productivity_sharing": 0.0,
        "company_offset.em_growth_premium": 1.0,
        "company_offset.five_forces_offset.rivalry_competitive_position": 0.0,
        "company_offset.five_forces_offset.rivalry_product_mix": 0.0,
        "company_offset.five_forces_offset.new_entrants_pipeline_uplift": 0.0,
        "company_offset.five_forces_offset.buyer_supplier_substitutes": 0.0,
    }


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_equilibrium_reading_is_mining_plus_weighted_pricing_at_year_ten(scenario):
    """With the declared terms off, the chain at Y10 collapses to the D-72 form:
    (1 + mining)(1 + w_infl * CPI + w_gas * gas) - 1, geo-mix one, no offset."""
    from vcc_valuations.translator import chain_macro_at
    inp = _inputs(scenario)
    d = revenue_growth_chain_from_data(inp, scenario, year=10, equilibrium=True)
    m = chain_macro_at(inp, 10)
    expected = (1 + m["global_mining_real_growth"]) * (1 + 0.7 * m["dm_inflation"] + 0.3 * m["gas_price_growth"]) - 1
    assert abs(d.result - expected) < 1e-12
    assert d["B36"].value == pytest.approx(1.0)
    assert d["B41"].value == 0.0


def test_terminal_growth_levels_unchanged_by_d78():
    """D-72's six derived rates, to the basis point (5.27 / 5.37 capped / 4.67 / 4.45 / 4.94 / 3.19)."""
    got = {s: round(terminal_growth_from_data(_inputs(s), s, 10).result * 100, 2) for s in SCENARIOS}
    assert got == {
        "orderly_convergence": 5.37, "muddle_through": 5.27, "ai_productivity_lag": 4.67,
        "fragmentation": 4.45, "disorderly_climate_crystallisation": 4.94, "stagflation_persists": 3.19,
    }
