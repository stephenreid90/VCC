"""DNL x Muddle Through — the ratified valuation assembled ENTIRELY from data.

``translator.build_engine_inputs_from_data`` composes the whole
``FcfEngineInputs`` from the YAML files: the data-driven WACC (β 1.10), the
per-year engine overlays (§11), the structured equity-bridge adjustments
(§4.2/§4.3), the §11 revenue-growth chain (industry baseline x geo-mix + net
Five-Forces offset, derived — not a stored scalar), the migrated valuation base
/ timing scalars, and the equity-bridge run-rates. No field is a hand-typed
constant: every input traces to a data file.

This closes the M2 assembly for DNL Muddle Through. ``dnl_mt_inputs`` (the
hand-typed golden) survives ONLY as the cross-check oracle here and as the
β-0.95 engine-mechanics oracle in ``test_e2e_dnl_mt.py``; nothing in the
production path imports it.
"""

from __future__ import annotations

from pathlib import Path

from vcc_valuations.translator import (
    load_inputs,
    build_engine_inputs_from_data,
    revenue_growth_from_data,
)
from vcc_valuations.dcf.fcf_engine import FcfEngine
from tests.dcf.golden.dnl_mt_inputs import (
    dnl_muddle_through_inputs,
    _revenue_growth_chain,
)

ROOT = Path(__file__).resolve().parents[2]


def _load():
    return load_inputs(
        ROOT,
        scenario_id="muddle_through",
        archetype_id="industrial_explosives",
        company_id="dnl",
    )


def test_engine_inputs_assembled_from_data_reproduce_ratified_per_share():
    """The whole engine input is built from data and reproduces the ratified
    β-1.10 headline: 3.073/share, EV 7,009.2, WACC 8.8772%."""
    inp = build_engine_inputs_from_data(_load(), "muddle_through")
    r = FcfEngine().run(inp)
    assert abs(r.wacc - 0.088772) < 1e-4
    assert round(r.enterprise_value, 1) == 7009.2
    assert round(r.value_per_share, 3) == 3.073
    assert r.value_per_share < r.market_reference_price


def test_revenue_growth_chain_derived_from_data_ties_golden():
    """The §11 revenue-growth chain, derived from the archetype-baseline +
    company-offset data rows, reproduces the hand-typed golden derivation."""
    g = revenue_growth_from_data(_load(), "muddle_through")
    assert g is not None
    assert abs(g - _revenue_growth_chain()) < 1e-12


def test_assembled_inputs_match_the_golden_field_by_field():
    """Every resolved field the data assembler emits matches the hand-typed
    golden stand-in (the WACC-half excepted: the golden pins β 0.95, the data
    the ratified β 1.10). Proves the migration is faithful, not merely close."""
    data = build_engine_inputs_from_data(_load(), "muddle_through")
    gold = dnl_muddle_through_inputs()

    assert data.base_year_revenue == gold.base_year_revenue
    assert data.horizon_years == gold.horizon_years
    assert data.stub_years == gold.stub_years
    assert abs(data.revenue_growth - gold.revenue_growth) < 1e-12
    assert data.base_ebit_margin == gold.base_ebit_margin
    assert data.margin_transformation == gold.margin_transformation
    assert data.margin_gas_rolloff == gold.margin_gas_rolloff
    assert data.tax_rate_glide == gold.tax_rate_glide
    assert data.capex_pct == gold.capex_pct
    assert data.terminal_growth == gold.terminal_growth

    db, gb = data.equity_bridge, gold.equity_bridge
    assert abs(db.net_debt_at_valuation - gb.net_debt_at_valuation) < 1e-9
    assert abs(db.equity_bridge_adjustments_net - gb.equity_bridge_adjustments_net) < 1e-9
    assert db.lease_liabilities == gb.lease_liabilities
    assert db.shares_outstanding == gb.shares_outstanding
    assert db.market_reference_price == gb.market_reference_price

    # The one intended difference: β (data ratified 1.10, golden 0.95).
    assert data.wacc.beta == 1.10
    assert gold.wacc.beta == 0.95


def test_geo_mix_is_derived_from_geographic_concentration():
    """The developed/emerging split feeding geo-mix comes from the segment's
    geographic_concentration (US + AU = DM ~90%, RoW = EM ~10%), not a stored
    weight — so a change to the concentration data would move the growth chain."""
    inp = _load()
    g_full = revenue_growth_from_data(inp, "muddle_through")

    # Perturb the concentration: shift 10pp from the US (DM) to RoW (EM). With a
    # >1.0 EM premium this must RAISE the geo-mix and hence company growth.
    regions = (
        inp["company_raw"]["company_position"]["segments"][0]
        ["risk_exposures"]["geographic_concentration"]["regions"]
    )
    by_geo = {r["geo"]: r for r in regions}
    by_geo["United States"]["share_of_revenue"] -= 0.10
    by_geo["Rest of World"]["share_of_revenue"] += 0.10
    g_shifted = revenue_growth_from_data(inp, "muddle_through")

    assert g_shifted > g_full
