"""DNL x Muddle Through — the RATIFIED production valuation (beta 1.10, data-driven).

The discount rate is built from the data files via
``translator.build_wacc_from_inputs`` rather than hardcoded: beta 1.10
(peer-triangulation, ratified 25 Jul 2026) with the methodology-§5.3-anchored E/V
weights (equity 6,390 / debt 1,260.8). This is the first end-to-end M2 wiring —
the discount-rate half of ``AssumptionSet -> FcfEngineInputs`` — driven from the
YAML rather than a hand-typed constant.

It SUPERSEDES the beta-0.95 workbook headline of 3.484 as the production per-share.
``test_e2e_dnl_mt.py`` retains 3.484 only as the engine-mechanics oracle: the engine
faithfully reproduces the audited v6 workbook when fed its (now beta-stale) inputs,
which validates the mechanics independently of any figure the engine itself emits.

The per-year structural overlays (margin glide, gas roll-off, tax glide, capex step,
the Fertilisers-separation equity bridge, the revenue-growth chain) still come from
the hand-typed ``dnl_mt_inputs`` stand-in; migrating those into the data files is the
remaining M2 work. This test wires the WACC half and pins the ratified result.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from vcc_valuations.translator import load_inputs, build_wacc_from_inputs
from vcc_valuations.dcf.fcf_engine import FcfEngine
from tests.dcf.golden.dnl_mt_inputs import dnl_muddle_through_inputs

ROOT = Path(__file__).resolve().parents[2]


def _load():
    return load_inputs(
        ROOT,
        scenario_id="muddle_through",
        archetype_id="industrial_explosives",
        company_id="dnl",
    )


def test_discount_rate_is_data_driven():
    """The WACC is assembled from the YAML, not hardcoded: ratified beta 1.10
    over the §5.3-anchored E/V weights."""
    w = build_wacc_from_inputs(_load())
    assert w.beta == 1.10                      # peer-triangulation, ratified 25 Jul 2026
    assert w.equity_market_value == 6390.0     # methodology §5.3 anchor
    assert w.debt_market_value == 1260.8
    assert abs(w.equity_weight - 0.8352) < 1e-3


def test_dnl_mt_ratified_per_share():
    """End-to-end: data-driven WACC into the engine over the hand-typed
    structural overlays.

    SUPERSEDED AS THE PRODUCTION HEADLINE, 23 Aug 2026. These inputs book no
    working capital and capitalise the grown final-year FCFF; the live valuation
    normalises both (D-13) and lands at 2.831. What survives here is the
    isolation: it holds reinvestment at the old settings so a movement in this
    number means the WACC or the overlays moved, not the reinvestment side.
    The live figure is pinned in test_dnl_mt_from_data.py."""
    inp = dataclasses.replace(dnl_muddle_through_inputs(), wacc=build_wacc_from_inputs(_load()))
    r = FcfEngine().run(inp)
    assert abs(r.wacc - 0.088772) < 1e-4
    assert round(r.value_per_share, 3) == 3.073     # pre-reinvestment oracle; live is 2.831
    assert round(r.enterprise_value, 1) == 7009.2
    # sanity: still a terminal-heavy DCF, below market
    assert r.value_per_share < r.market_reference_price


def test_equity_bridge_adjustments_are_data_driven():
    """The Fertilisers-separation equity-bridge adjustments are now a structured
    data block (methodology §4.2) that reproduces the hand-typed golden net."""
    import yaml
    from vcc_valuations.translator import equity_bridge_adjustments_net_from_data
    from tests.dcf.golden.dnl_mt_inputs import _equity_bridge_adjustments_net

    raw = yaml.safe_load((ROOT / "data" / "companies" / "dnl.yaml").read_text(encoding="utf-8"))
    net = equity_bridge_adjustments_net_from_data(raw)
    assert round(net, 2) == 151.65                                   # workbook Equity Bridge B24
    assert round(net, 4) == round(_equity_bridge_adjustments_net(), 4)   # ties the hand-typed golden


def test_equity_bridge_validator_requires_on_balance_sheet_flag():
    """Methodology §4.3: an adjustment missing on_balance_sheet_at_anchor is an error."""
    import pytest
    from vcc_valuations.translator import equity_bridge_adjustments_net_from_data

    bad = {"normalised_baseline": {"equity_bridge_adjustments": [
        {"id": "x", "amount_aud_m": 10.0, "direction": "subtract_from_equity",
         "treatment": "add_back_in_full"}]}}
    with pytest.raises(ValueError, match="on_balance_sheet_at_anchor"):
        equity_bridge_adjustments_net_from_data(bad)


def test_engine_overlays_data_driven_reproduce_headline():
    """Per-year overlays (margin/gas/tax/capex glides) now come from data; fed
    into the engine with the data-driven WACC they reproduce the ratified 3.073."""
    import yaml
    from vcc_valuations.translator import engine_overlays_from_data, tax_bridge_from_data

    raw = yaml.safe_load((ROOT / "data" / "companies" / "dnl.yaml").read_text(encoding="utf-8"))
    ov = engine_overlays_from_data(raw, "muddle_through")
    # Applied tax now comes from the derived Tax Bridge, not stored overlays.
    tax = tax_bridge_from_data(_load())
    glide = [tax[f"B{11 + i}"].value for i in range(1, 6)]
    inp = dataclasses.replace(
        dnl_muddle_through_inputs(),
        wacc=build_wacc_from_inputs(_load()),
        base_ebit_margin=ov["base_ebit_margin"],
        margin_transformation=ov["margin_transformation"],
        margin_gas_rolloff=ov["margin_gas_rolloff"],
        stub_tax_rate=raw["normalised_baseline"]["tax_bridge"]["effective_tax_rate"],
        tax_rate_glide=glide,
        capex_pct_stub=ov["capex_pct_stub"],
        capex_pct=ov["capex_pct"],
        da_pct_revenue=ov["da_pct_revenue"],
        terminal_growth=ov["terminal_growth"],
    )
    r = FcfEngine().run(inp)
    assert round(r.value_per_share, 3) == 3.073     # data overlays + data WACC, ratified β 1.10
