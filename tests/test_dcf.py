import pytest
from models.dcf import DCFModel, DCFAssumptions


def test_dcf_basic(apple_dcf):
    model = DCFModel(apple_dcf)
    result = model.calculate()
    assert result.enterprise_value > 0
    assert result.equity_value > 0
    assert result.price_per_share > 0
    assert len(result.fcf_projections) == 5


def test_dcf_fcf_grows(apple_dcf):
    model = DCFModel(apple_dcf)
    result = model.calculate()
    for i in range(len(result.fcf_projections) - 1):
        ratio = result.fcf_projections[i + 1] / result.fcf_projections[i]
        assert 1.04 < ratio < 1.06


def test_dcf_pv_components(apple_dcf):
    model = DCFModel(apple_dcf)
    result = model.calculate()
    assert result.pv_explicit > 0
    assert result.pv_terminal > 0
    assert abs(result.enterprise_value - result.pv_explicit - result.pv_terminal) < 1


def test_dcf_sensitivity_keys(apple_dcf):
    model = DCFModel(apple_dcf)
    result = model.calculate()
    assert "base" in result.sensitivity_wacc_growth
    assert "wacc_up_1pct" in result.sensitivity_wacc_growth
    assert result.sensitivity_wacc_growth["base"] > result.sensitivity_wacc_growth["wacc_up_1pct"]


def test_dcf_wacc_exceeds_tg():
    with pytest.raises(ValueError):
        bad = DCFAssumptions(
            fcf_base=100e6, fcf_growth_rate=5.0, wacc=2.0, terminal_growth=3.0,
            shares_outstanding=100
        )
        DCFModel(bad).calculate()
