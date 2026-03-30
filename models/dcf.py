"""DCF valuation engine — corporates, miners, banks."""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import numpy as np


class DCFAssumptions(BaseModel):
    """DCF model assumptions — sector-agnostic."""
    fcf_base: float = Field(..., description="Base year FCF (USD)")
    fcf_growth_rate: float = Field(..., description="Explicit period growth rate (%)")
    wacc: float = Field(..., description="Weighted average cost of capital (%)")
    terminal_growth: float = Field(..., description="Terminal value growth rate (%)")
    explicit_periods: int = Field(5, description="Number of explicit forecast years")
    net_debt: float = Field(0.0, description="Net debt (negative = net cash)")
    shares_outstanding: float = Field(..., description="Shares outstanding (absolute count, e.g. 15.5e9 for 15.5 billion)")

    model_config = {"extra": "allow"}


class DCFResult(BaseModel):
    """DCF valuation output."""
    enterprise_value: float
    equity_value: float
    price_per_share: float
    pv_explicit: float
    pv_terminal: float
    fcf_projections: List[float]
    sensitivity_wacc_growth: Dict[str, float]

    model_config = {"extra": "allow"}


class DCFModel:
    def __init__(self, assumptions: DCFAssumptions):
        self.assumptions = assumptions

    def calculate(self) -> DCFResult:
        """Run DCF calculation."""
        a = self.assumptions
        growth = a.fcf_growth_rate / 100
        wacc = a.wacc / 100
        tg = a.terminal_growth / 100

        if wacc <= tg:
            raise ValueError("WACC must exceed terminal growth rate.")

        fcf_projections = [
            a.fcf_base * (1 + growth) ** (yr + 1)
            for yr in range(a.explicit_periods)
        ]

        pv_explicit = sum(
            fcf / (1 + wacc) ** (yr + 1)
            for yr, fcf in enumerate(fcf_projections)
        )

        terminal_fcf = fcf_projections[-1] * (1 + tg)
        terminal_value = terminal_fcf / (wacc - tg)
        pv_terminal = terminal_value / (1 + wacc) ** a.explicit_periods

        enterprise_value = pv_explicit + pv_terminal
        equity_value = enterprise_value - a.net_debt
        price_per_share = equity_value / a.shares_outstanding

        return DCFResult(
            enterprise_value=enterprise_value,
            equity_value=equity_value,
            price_per_share=price_per_share,
            pv_explicit=pv_explicit,
            pv_terminal=pv_terminal,
            fcf_projections=fcf_projections,
            sensitivity_wacc_growth=self._sensitivity_table(wacc, tg),
        )

    def _sensitivity_table(self, wacc: float, tg: float) -> Dict[str, float]:
        """Sensitivity: WACC ± 1%, terminal growth ± 0.5%."""
        results = {}
        a = self.assumptions
        for dw, dg, label in [
            (0, 0, "base"),
            (0.01, 0, "wacc_up_1pct"),
            (-0.01, 0, "wacc_dn_1pct"),
            (0, 0.005, "growth_up_0.5pct"),
            (0, -0.005, "growth_dn_0.5pct"),
        ]:
            adj_wacc = wacc + dw
            adj_tg = tg + dg
            if adj_wacc <= adj_tg:
                results[label] = float("nan")
                continue
            fcf_projs = [
                a.fcf_base * (1 + a.fcf_growth_rate / 100) ** (yr + 1)
                for yr in range(a.explicit_periods)
            ]
            pv_e = sum(f / (1 + adj_wacc) ** (yr + 1) for yr, f in enumerate(fcf_projs))
            tv = fcf_projs[-1] * (1 + adj_tg) / (adj_wacc - adj_tg)
            pv_t = tv / (1 + adj_wacc) ** a.explicit_periods
            results[label] = round(pv_e + pv_t, 2)
        return results
