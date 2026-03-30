from models.comps import CompsModel, ComparableCompany


def test_comps_medians(peer_companies):
    target = ComparableCompany(name="Target", ev=60e9, ebitda=6e9, revenue=22e9)
    model = CompsModel(peer_companies, target)
    result = model.calculate()
    assert result.medians["ev_ebitda"] is not None
    assert result.medians["ev_revenue"] is not None
    assert len(result.multiples) == 3


def test_comps_implied_value(peer_companies):
    target = ComparableCompany(name="Target", ev=60e9, ebitda=6e9, revenue=22e9)
    model = CompsModel(peer_companies, target)
    result = model.calculate()
    assert result.implied_value["ev_ebitda"] > 0
