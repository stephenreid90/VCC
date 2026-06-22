"""
Implied Equity Market Risk Premium (EMRP) via a multi-stage cash-flow model.

Approach (after Damodaran's implied ERP)
----------------------------------------
The current index level is treated as the present value of the expected
future cash flows that the market returns to shareholders — dividends
plus net buybacks. We project that cash-flow stream in two stages:

  Stage 1 — consensus:  grow the base-year cash flow by *consensus analyst
            growth forecasts*, one rate per year, for as many years as
            those forecasts run (the list can be any length).
  Stage 2 — terminal:   apply a single constant terminal growth rate in
            perpetuity. Conventionally this is set to the risk-free rate,
            so long-run market growth never exceeds the risk-free economy.

We then solve for the internal rate of return ``r`` that equates the
present value of the stream to today's index level. ``r`` is the expected
return on equities implied by the current price and consensus
expectations. The implied EMRP is::

        EMRP = r - risk_free_rate

Everything here is plain numbers; live data (index level, risk-free rate,
dividend yield) comes from :mod:`vcc_valuations.market.fmp_client`, and the
consensus growth path and buyback yield are supplied by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from scipy.optimize import brentq


@dataclass(frozen=True)
class EMRPResult:
    """Outcome of an implied-EMRP solve."""

    index_level: float
    base_cash_flow: float
    forecast_cash_flows: tuple[float, ...]
    terminal_growth: float
    risk_free_rate: float
    implied_return: float  # the solved IRR r

    @property
    def emrp(self) -> float:
        """Implied equity market risk premium: r - risk_free_rate."""
        return self.implied_return - self.risk_free_rate

    def summary(self) -> str:
        return (
            f"Index level        : {self.index_level:,.2f}\n"
            f"Base cash flow      : {self.base_cash_flow:,.2f}\n"
            f"Forecast years      : {len(self.forecast_cash_flows)} "
            f"(consensus stage)\n"
            f"Terminal growth     : {self.terminal_growth:6.2%}\n"
            f"Risk-free rate      : {self.risk_free_rate:6.2%}\n"
            f"Implied equity return (IRR): {self.implied_return:6.2%}\n"
            f"Implied EMRP        : {self.emrp:6.2%}"
        )


def build_forecast_cash_flows(
    base_cash_flow: float,
    consensus_growth: Sequence[float],
) -> list[float]:
    """
    Grow ``base_cash_flow`` by each rate in ``consensus_growth`` in turn.

    Returns the explicit Stage-1 cash flows CF_1..CF_n, where
    CF_t = CF_{t-1} * (1 + g_t) and CF_0 = base_cash_flow.
    """
    cash_flows: list[float] = []
    cf = base_cash_flow
    for g in consensus_growth:
        cf *= 1.0 + g
        cash_flows.append(cf)
    return cash_flows


def _present_value(
    r: float,
    forecast_cash_flows: Sequence[float],
    terminal_growth: float,
) -> float:
    """PV of the Stage-1 cash flows plus a Gordon terminal value at year n."""
    n = len(forecast_cash_flows)
    pv = sum(cf / (1.0 + r) ** t for t, cf in enumerate(forecast_cash_flows, 1))
    cf_n = forecast_cash_flows[-1]
    terminal_value = cf_n * (1.0 + terminal_growth) / (r - terminal_growth)
    pv += terminal_value / (1.0 + r) ** n
    return pv


def implied_market_return(
    index_level: float,
    forecast_cash_flows: Sequence[float],
    terminal_growth: float,
    *,
    r_low: float | None = None,
    r_high: float = 1.0,
) -> float:
    """
    Solve for the IRR ``r`` such that PV(cash flows) == index_level.

    The terminal value requires r > terminal_growth, so the search is
    bracketed just above ``terminal_growth``. Raises ``ValueError`` if the
    inputs do not bracket a root (e.g. cash flows too small for the price).
    """
    if not forecast_cash_flows:
        raise ValueError("Need at least one forecast cash flow.")
    if index_level <= 0:
        raise ValueError("index_level must be positive.")
    if r_low is None:
        r_low = terminal_growth + 1e-6

    def f(r: float) -> float:
        return _present_value(r, forecast_cash_flows, terminal_growth) - index_level

    f_low, f_high = f(r_low), f(r_high)
    if f_low * f_high > 0:
        raise ValueError(
            "Could not bracket a solution for the implied return between "
            f"{r_low:.4%} and {r_high:.4%}. Check that cash flows, growth "
            "and index level are mutually consistent."
        )
    return brentq(f, r_low, r_high, xtol=1e-10)


def estimate_emrp(
    index_level: float,
    base_cash_flow: float,
    consensus_growth: Sequence[float],
    terminal_growth: float,
    risk_free_rate: float,
) -> EMRPResult:
    """
    End-to-end: build the consensus cash-flow path, solve for the implied
    equity return, and return an :class:`EMRPResult` (``.emrp`` is the
    implied premium).
    """
    cash_flows = build_forecast_cash_flows(base_cash_flow, consensus_growth)
    r = implied_market_return(index_level, cash_flows, terminal_growth)
    return EMRPResult(
        index_level=index_level,
        base_cash_flow=base_cash_flow,
        forecast_cash_flows=tuple(cash_flows),
        terminal_growth=terminal_growth,
        risk_free_rate=risk_free_rate,
        implied_return=r,
    )
