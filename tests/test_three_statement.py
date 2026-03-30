from models.three_statement import ThreeStatementModel


def test_three_statement_returns_periods(corp_3s):
    model = ThreeStatementModel(corp_3s)
    result = model.calculate()
    assert len(result.income_statements) == 5
    assert len(result.fcf_projections) == 5


def test_revenue_grows(corp_3s):
    model = ThreeStatementModel(corp_3s)
    result = model.calculate()
    revs = [r["revenue"] for r in result.income_statements]
    for i in range(len(revs) - 1):
        assert revs[i + 1] > revs[i]


def test_ebitda_positive(corp_3s):
    model = ThreeStatementModel(corp_3s)
    result = model.calculate()
    for stmt in result.income_statements:
        assert stmt["ebitda"] > 0
