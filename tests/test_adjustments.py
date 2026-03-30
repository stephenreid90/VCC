from models.adjustments.mining import MiningAdjustments
from models.adjustments.banking import BankingAdjustments
from models.adjustments.corporate import CorporateAdjustments


# --- Mining ---
def test_commodity_price_blend():
    price = MiningAdjustments.commodity_price_adjustment("gold", spot_price=2000, long_term_price=1800)
    assert price == pytest.approx(1860.0, rel=1e-3)


def test_reserve_life():
    life = MiningAdjustments.reserve_life_adjustment(annual_production=100, proven_reserves=1000)
    assert life == pytest.approx(9.5, rel=1e-3)


def test_fcf_conversion_high_risk():
    fcf = MiningAdjustments.fcf_conversion_adjustment(ebitda=100, commodity="lithium", risk_tier="high")
    # base 0.50 - 0.08 = 0.42
    assert fcf == pytest.approx(42.0, rel=1e-3)


# --- Banking ---
def test_nim_adjustment():
    assert BankingAdjustments.net_interest_margin_adjustment(2.0, "rising") == pytest.approx(2.1)
    assert BankingAdjustments.net_interest_margin_adjustment(2.0, "falling") == pytest.approx(1.9)


def test_cet1_check():
    result = BankingAdjustments.cet1_ratio_check(0.13)
    assert result["adequate"] is True
    result2 = BankingAdjustments.cet1_ratio_check(0.07)
    assert result2["adequate"] is False


# --- Corporate ---
def test_leverage():
    result = CorporateAdjustments.leverage_adjustment(net_debt=300e6, ebitda=100e6)
    assert result["net_debt_ebitda"] == 3.0
    assert result["risk_tier"] == "medium"


def test_wacc_estimate():
    wacc = CorporateAdjustments.wacc_estimate(0.7, 10.0, 0.3, 5.0, 30.0)
    assert wacc == pytest.approx(8.05, rel=1e-2)


import pytest
