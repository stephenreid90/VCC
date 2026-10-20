"""Resource (depletion) engine mechanics, on hand-built inputs (D-96 proposed, 20 Oct 2026).

Each case is small enough to compute by hand; the arithmetic is in the comments. These pin
the engine, not EVN: EVN's levels are in test_scenario_goldens.py and its sized
alternatives in test_resource_valuation_sets.py.
"""

from __future__ import annotations

import pytest

from vcc_valuations.dcf.fcf_engine import EquityBridge
from vcc_valuations.dcf.resource_engine import MineInputs, ResourceEngine, ResourceEngineInputs


def _inputs(mines, *, gold=2000.0, copper=10000.0, H=1, stub=0.5, wacc=0.10, wci=0.0,
            royalty=0.0, tax=0.0, guidance_gold=2000.0, guidance_copper=10000.0):
    return ResourceEngineInputs(
        company_id="test", scenario_id="flat", functional_currency="AUD", horizon_years=H,
        stub_years=stub, mines=mines, gold_aud_oz=[gold], copper_aud_t=[copper], cost_index=[1.0],
        guidance_gold_aud_oz=guidance_gold, guidance_copper_aud_t=guidance_copper,
        royalty_rate=royalty, tax_rate=tax, corporate_cost_aud_oz=0.0, greenfields_exploration=0.0,
        working_capital_intensity=wci, wacc=wacc,
        equity_bridge=EquityBridge(net_debt_at_valuation=10.0, equity_bridge_adjustments_net=5.0,
                                   lease_liabilities=0.0, shares_outstanding=100.0),
    )


def _gold_mine(**kw):
    base = dict(name="m", gold_koz_pa=100.0, copper_kt_pa=0.0, inventory_gold_koz=250.0,
                inventory_copper_kt=0.0, aisc_aud_oz=1000.0, sustaining_capex=10.0,
                mine_development=5.0, exploration=0.0, da_aud_oz=0.0)
    base.update(kw)
    return MineInputs(**base)


def test_one_mine_depletes_and_discounts_by_hand():
    # 250koz at 100kozpa with a half-year stub: 50 / 100 / 100, then the ore is gone.
    # Revenue 100 / 200 / 200; opex (AISC 100 less sustaining 10) x scale = 45 / 90 / 90;
    # capex 15 x scale = 7.5 / 15 / 15; FCFF 47.5 / 95 / 95 at mid-times 0.25 / 1 / 2.
    r = ResourceEngine().run(_inputs([_gold_mine()]))
    assert r.gold_koz == pytest.approx([50.0, 100.0, 100.0])
    assert r.fcff == pytest.approx([47.5, 95.0, 95.0])
    assert r.mid_times == pytest.approx([0.25, 1.0, 2.0])
    pv_explicit = 47.5 / 1.1 ** 0.25 + 95.0 / 1.1
    pv_terminal = 95.0 / 1.1 ** 2
    assert r.pv_explicit == pytest.approx(pv_explicit)
    assert r.pv_terminal == pytest.approx(pv_terminal)
    assert r.terminal_value == pytest.approx(pv_terminal * 1.1 ** 1.5)  # at the end of Y1
    assert r.value_per_share == pytest.approx((pv_explicit + pv_terminal - 15.0) / 100.0)
    assert r.terminal_form == "depletion_run_off"
    assert r.mine_last_period == {"m": 2}


def test_ore_driven_stop_takes_the_first_metal_to_run_out():
    # Copper runs out first (20kt at 10ktpa: 0.5 + 1.0 + 0.5 years); gold stops with it.
    m = _gold_mine(copper_kt_pa=10.0, inventory_copper_kt=20.0, inventory_gold_koz=1000.0)
    r = ResourceEngine().run(_inputs([m]))
    assert r.copper_kt == pytest.approx([5.0, 10.0, 5.0])
    assert r.gold_koz == pytest.approx([50.0, 100.0, 50.0])


def test_by_product_credit_is_added_back_so_copper_moves_with_its_own_price():
    # At guidance prices the AISC basis holds. A copper price A$2,000/t higher adds
    # 10kt x 2,000 = A$20m of revenue a full year and nothing to cost.
    m = _gold_mine(copper_kt_pa=10.0, inventory_copper_kt=100.0, inventory_gold_koz=1000.0)
    at_guidance = ResourceEngine().run(_inputs([m]))
    higher = ResourceEngine().run(_inputs([_gold_mine(copper_kt_pa=10.0, inventory_copper_kt=100.0,
                                                      inventory_gold_koz=1000.0)], copper=12000.0))
    assert higher.revenue[1] - at_guidance.revenue[1] == pytest.approx(20.0)
    assert higher.operating_cost[1] == pytest.approx(at_guidance.operating_cost[1])
    # gross cost = AISC x oz + copper credit = 100 + 100; less sustaining 10 = 190
    assert at_guidance.operating_cost[1] == pytest.approx(190.0)


def test_royalty_is_stripped_from_aisc_and_charged_on_actual_revenue():
    # Royalty 5%: guidance royalty 0.05 x 200 = 10 leaves opex 100 - 10 - 10 = 80; at a
    # price of 3,000 the royalty charged is 0.05 x 300 = 15.
    r = ResourceEngine().run(_inputs([_gold_mine(inventory_gold_koz=1000.0)], gold=3000.0, royalty=0.05))
    assert r.operating_cost[1] == pytest.approx(80.0)
    assert r.royalty[1] == pytest.approx(15.0)


def test_stream_sells_the_delivered_share_at_a_fraction_of_spot():
    # Half delivered at 10% of spot: revenue x (1 - 0.5 x 0.9) = 200 x 0.55 = 110.
    m = _gold_mine(inventory_gold_koz=1000.0, stream_delivered_fraction=0.5,
                   stream_cash_fraction_of_spot=0.1)
    assert ResourceEngine().run(_inputs([m])).revenue[1] == pytest.approx(110.0)


def test_a_late_starting_uplift_produces_only_from_its_start_period():
    host = _gold_mine(inventory_gold_koz=1000.0)
    uplift = _gold_mine(name="u", gold_koz_pa=10.0, inventory_gold_koz=20.0, start_period=2,
                        sustaining_capex=0.0, mine_development=0.0)
    r = ResourceEngine().run(_inputs([host, uplift], H=3))
    assert r.mine_last_period["u"] == 3
    assert r.gold_koz[1] == pytest.approx(100.0)
    assert r.gold_koz[2] == pytest.approx(110.0)


def test_negative_working_capital_unwinds_at_closure():
    # wci -5%: revenue 100 (stub, 200 annualised) then 200 twice; no change after the
    # stub, then at closure 200 x 5% = 10 leaves the business.
    r = ResourceEngine().run(_inputs([_gold_mine()], wci=-0.05))
    assert r.delta_wc == pytest.approx([0.0, 0.0, 10.0])
    assert r.fcff[-1] == pytest.approx(85.0)


def test_tax_is_charged_on_ebitda_less_book_depreciation():
    # EBITDA 110 a full year; D&A 100koz x A$300 = 30; tax 30% x 80 = 24.
    r = ResourceEngine().run(_inputs([_gold_mine(inventory_gold_koz=1000.0, da_aud_oz=300.0)], tax=0.30))
    assert r.tax[1] == pytest.approx(24.0)
