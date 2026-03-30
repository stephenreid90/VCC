"""Three-statement financial model: P&L → Balance Sheet → Cash Flow → FCF."""
from pydantic import BaseModel, Field
from typing import List, Dict


class ThreeStatementAssumptions(BaseModel):
    revenue_base: float = Field(..., description="Base year revenue (USD)")
    revenue_growth: float = Field(..., description="Revenue growth rate (%)")
    ebitda_margin: float = Field(..., description="EBITDA margin (%)")
    da_pct_revenue: float = Field(5.0, description="D&A as % of revenue")
    tax_rate: float = Field(30.0, description="Tax rate (%)")
    capex_pct_revenue: float = Field(5.0, description="CapEx as % of revenue")
    nwc_pct_revenue: float = Field(2.0, description="NWC change as % of revenue change")
    explicit_periods: int = Field(5)

    model_config = {"extra": "allow"}


class ThreeStatementResult(BaseModel):
    income_statements: List[Dict]
    balance_sheets: List[Dict]
    cash_flows: List[Dict]
    fcf_projections: List[float]

    model_config = {"extra": "allow"}


class ThreeStatementModel:
    def __init__(self, assumptions: ThreeStatementAssumptions):
        self.a = assumptions

    def calculate(self) -> ThreeStatementResult:
        a = self.a
        income_statements, balance_sheets, cash_flows, fcf_projections = [], [], [], []

        prior_revenue = a.revenue_base
        cumulative_assets = a.revenue_base * 0.5  # simplified opening assets

        for yr in range(1, a.explicit_periods + 1):
            revenue = prior_revenue * (1 + a.revenue_growth / 100)
            ebitda = revenue * a.ebitda_margin / 100
            da = revenue * a.da_pct_revenue / 100
            ebit = ebitda - da
            tax = max(ebit * a.tax_rate / 100, 0)
            net_income = ebit - tax

            capex = revenue * a.capex_pct_revenue / 100
            delta_nwc = (revenue - prior_revenue) * a.nwc_pct_revenue / 100
            fcf = ebitda - tax - capex - delta_nwc

            income_statements.append({
                "year": yr, "revenue": round(revenue, 2),
                "ebitda": round(ebitda, 2), "ebit": round(ebit, 2),
                "net_income": round(net_income, 2),
            })
            cumulative_assets += capex - da
            balance_sheets.append({
                "year": yr, "total_assets": round(cumulative_assets, 2),
                "retained_earnings": round(net_income, 2),
            })
            cash_flows.append({
                "year": yr, "operating_cf": round(net_income + da, 2),
                "capex": round(-capex, 2), "fcf": round(fcf, 2),
            })
            fcf_projections.append(round(fcf, 2))
            prior_revenue = revenue

        return ThreeStatementResult(
            income_statements=income_statements,
            balance_sheets=balance_sheets,
            cash_flows=cash_flows,
            fcf_projections=fcf_projections,
        )
