"""
Unit tests for the implied-EMRP model.

No network here — the FMP client is exercised separately. These tests pin
the maths of the cash-flow solve against a closed-form Gordon-growth case
and check the round-trip and the EMRP arithmetic.
"""

from __future__ import annotations

import math

import pytest

from vcc_valuations.market.implied_emrp import (
    build_forecast_cash_flows,
    estimate_emrp,
    implied_market_return,
)


def test_gordon_closed_form():
    """
    With a single consensus year and terminal growth equal to that year's
    growth, the two-stage model collapses to the Gordon model:

        P = D_1 / (r - g)   =>   r = D_1 / P + g

    so the solved IRR must match the closed-form value.
    """
    base_cf, g, price = 2.0, 0.02, 100.0
    cfs = build_forecast_cash_flows(base_cf, [g])  # CF_1 = 2.04
    r = implied_market_return(price, cfs, terminal_growth=g)
    expected = cfs[0] / price + g  # 2.04/100 + 0.02 = 0.0404
    assert math.isclose(r, expected, rel_tol=1e-6)


def test_present_value_roundtrip_multistage():
    """The solved IRR must discount the cash-flow stream back to the price."""
    from vcc_valuations.market.implied_emrp import _present_value

    price = 4500.0
    base_cf = 0.045 * price
    growth = [0.11, 0.09, 0.08, 0.07, 0.06]
    terminal = 0.04
    cfs = build_forecast_cash_flows(base_cf, growth)
    r = implied_market_return(price, cfs, terminal_growth=terminal)
    assert math.isclose(_present_value(r, cfs, terminal), price, rel_tol=1e-8)


def test_emrp_is_return_minus_riskfree():
    rf = 0.04
    res = estimate_emrp(
        index_level=4500.0,
        base_cash_flow=0.045 * 4500.0,
        consensus_growth=[0.11, 0.09, 0.08, 0.07, 0.06],
        terminal_growth=rf,
        risk_free_rate=rf,
    )
    assert math.isclose(res.emrp, res.implied_return - rf, rel_tol=1e-12)
    # Sanity: equities should out-yield the risk-free rate here.
    assert res.emrp > 0


def test_unbracketable_inputs_raise():
    """Cash flows far too small for the price cannot bracket a root."""
    with pytest.raises(ValueError):
        implied_market_return(1_000_000.0, [1.0], terminal_growth=0.04)
