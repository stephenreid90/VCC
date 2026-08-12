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
    revenue_growth_chain_from_data,
    wacc_build_from_data,
    equity_bridge_from_data,
    tax_bridge_from_data,
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


def test_chain_intermediate_steps_tie_v6_row_by_row():
    """Full V6 traceability: every derived row of the chain (workbook B25-B42)
    is exposed as an auditable step and ties its workbook value to the cent."""
    d = revenue_growth_chain_from_data(_load(), "muddle_through")
    assert d is not None
    expected = {
        "B25": 0.03275,        # industry volume growth   = 1.15 x 0.025 + 0.004
        "B29": 0.0285,         # industry pricing growth  = 0.7 x 0.025 + 0.3 x 0.02 + 0.005
        "B30": 0.062183375,    # industry nominal growth  = (1+vol)(1+price) - 1
        "B33": 0.90,           # DM weighting (US 0.55 + AU 0.35), derived from geo-concentration
        "B34": 0.10,           # EM weighting (RoW 0.10)
        "B36": 1.03,           # geo-mix multiplier       = 0.9 + 0.1 x 1.3
        "B41": -0.0025,        # net company offset       = -0.003 -0.001 +0.0015 +0
        "B42": 0.06154887625,  # company nominal growth   = B30 x B36 + B41
    }
    for cell, want in expected.items():
        assert abs(d[cell].value - want) < 1e-9, f"{cell}={d[cell].value} != {want}"
    assert d.result == d["B42"].value


def test_chain_steps_carry_formula_and_provenance():
    """Each step is self-describing — a formula, the inputs it consumed, and the
    originating workbook cell — so the build reads out of the engine, not Excel."""
    d = revenue_growth_chain_from_data(_load(), "muddle_through")
    assert [s.cell for s in d] == ["B25", "B29", "B30", "B33", "B34", "B36", "B41", "B42"]
    for s in d:
        assert s.formula and s.label and s.inputs, f"{s.cell} under-described"
    # the DM/EM weighting is genuinely derived from the concentration data, not a
    # stored 0.9/0.1: its inputs name the regions that were summed.
    assert set(d["B33"].inputs) == {"United States", "Australia"}
    assert set(d["B34"].inputs) == {"Rest of World"}


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
    assert len(data.tax_rate_glide) == len(gold.tax_rate_glide)
    assert all(abs(a - b) < 1e-9 for a, b in zip(data.tax_rate_glide, gold.tax_rate_glide))
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


def test_tax_bridge_derivation_derives_blended_statutory_and_glide():
    """The Tax Bridge derives the blended statutory rate (D8) from revenue-weighted
    jurisdictional rates and the applied-tax glide (B12-B16) as the effective rate
    closing the gap to statutory — reproducing the golden glide, which used to be
    STORED. Weights come from geographic_concentration (US .55/AU .35/RoW .10)."""
    d = tax_bridge_from_data(_load())
    assert d is not None
    assert abs(d["D8"].value - 0.275) < 1e-9        # 0.55x0.26 + 0.35x0.30 + 0.10x0.27
    glide = [d[f"B{11 + i}"].value for i in range(1, 6)]
    golden = [0.225, 0.2375, 0.25, 0.2625, 0.275]   # the value that used to be hardcoded
    assert all(abs(a - b) < 1e-9 for a, b in zip(glide, golden))
    # D8 depends on the statutory rates, so it is genuinely derived, not stored:
    assert [s.cell for s in d] == ["D5", "D6", "D7", "D8", "B12", "B13", "B14", "B15", "B16"]


def test_tax_glide_is_no_longer_stored_in_overlays():
    """SSOT: the tax glide is gone from the stored engine_overlays — it is derived."""
    from vcc_valuations.translator import engine_overlays_from_data
    ov = engine_overlays_from_data(_load()["company_raw"], "muddle_through")
    assert "tax_rate_glide" not in ov
    assert "stub_tax_rate" not in ov


def test_wacc_build_derivation_traces_v6_rows_at_ratified_inputs():
    """The WACC build exposes its six V6 derived rows (B8/B13/B18/B19/B20/B23).
    Values reflect the RATIFIED inputs (beta 1.10, tax 0.30), superseding the v6
    sheet's cached beta 0.95 / tax 0.275 — the row structure matches, the number
    is the production discount rate."""
    d = wacc_build_from_data(_load())
    assert [s.cell for s in d] == ["B8", "B13", "B18", "B19", "B20", "B23"]
    assert abs(d["B8"].value - 0.098) < 1e-9        # Re = 0.043 + 1.10 x 0.05
    assert abs(d["B13"].value - 0.042) < 1e-9       # Rd_at = 0.06 x (1 - 0.30)
    assert abs(d["B18"].value - 7650.8) < 1e-6      # V = 6390 + 1260.8
    assert abs(d["B19"].value - 0.8352) < 1e-3      # E/V
    assert abs(d.result - 0.088772) < 1e-4          # B23 WACC, ratified
    for s in d:
        assert s.formula and s.inputs


def test_equity_bridge_derivation_traces_walk_and_per_share():
    """The equity bridge exposes the Period-A walk (B6-B11) and the per-share
    chain (B27-B37); B11 ties the golden net-debt walk and B33 ties the engine."""
    d = equity_bridge_from_data(_load(), "muddle_through")
    assert [s.cell for s in d] == \
        ["B6", "B7", "B8", "B10", "B11", "B27", "B28", "B29", "B30", "B31", "B33", "B37"]
    assert abs(d["B11"].value - 1224.0329) < 1e-3   # net debt at valuation (golden)
    assert abs(d["B29"].value - (-151.65)) < 1e-2   # adjustments net (§4.2)
    assert round(d.result, 3) == 3.073              # B33 value per share
    # B33 must equal the engine's own value_per_share, not a re-derivation drift.
    inp = build_engine_inputs_from_data(_load(), "muddle_through")
    from vcc_valuations.dcf.fcf_engine import FcfEngine
    assert abs(d.result - FcfEngine().run(inp).value_per_share) < 1e-9


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
