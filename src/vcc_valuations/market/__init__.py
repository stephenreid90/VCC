"""
Market-level inputs and models.

Currently houses the implied Equity Market Risk Premium (EMRP) toolchain:

  * fmp_client    — thin Financial Modeling Prep API wrapper for live inputs
  * implied_emrp  — multi-stage cash-flow model that backs out the EMRP
                    implied by the current index level and consensus growth
"""

from vcc_valuations.market.implied_emrp import (
    EMRPResult,
    build_forecast_cash_flows,
    estimate_emrp,
    implied_market_return,
)

__all__ = [
    "EMRPResult",
    "build_forecast_cash_flows",
    "estimate_emrp",
    "implied_market_return",
]
