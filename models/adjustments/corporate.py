"""Corporate-specific valuation adjustments."""


class CorporateAdjustments:
    """Leverage and FCF adjustments for industrial/corporate issuers."""

    @staticmethod
    def leverage_adjustment(
        net_debt: float,
        ebitda: float,
    ) -> dict:
        """Compute leverage metrics and flag risk tier."""
        leverage = round(net_debt / ebitda, 2) if ebitda else float("inf")
        if leverage < 1.5:
            tier = "low"
        elif leverage < 3.5:
            tier = "medium"
        else:
            tier = "high"
        return {"net_debt_ebitda": leverage, "risk_tier": tier}

    @staticmethod
    def fcf_conversion(
        ebitda: float,
        capex: float,
        tax: float,
        delta_nwc: float = 0.0,
    ) -> float:
        """Unlevered FCF conversion from EBITDA."""
        return round(ebitda - capex - tax - delta_nwc, 2)

    @staticmethod
    def wacc_estimate(
        equity_weight: float,
        cost_of_equity: float,
        debt_weight: float,
        cost_of_debt: float,
        tax_rate: float,
    ) -> float:
        """Simple WACC estimate."""
        after_tax_debt = cost_of_debt * (1 - tax_rate / 100)
        return round(equity_weight * cost_of_equity + debt_weight * after_tax_debt, 4)
