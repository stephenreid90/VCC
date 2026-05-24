"""
Minimal FCF DCF stub for Phase 3.5 smoke test.

~70-line discounted-cash-flow engine: explicit 5-year forecast +
Gordon-growth terminal. Consumes a SmokeAssumptionSet (from
translator.py); produces EnterpriseValue, EquityValue, ValuePerShare.

Deliberately simple. Things this DOESN'T do (left for production
Step 7):
- No working-capital dynamics (assumed neutral).
- No segment aggregation (DNL single-segment so fine).
- No FX translation (operates in single reporting currency).
- No tax-rate jurisdictional mix.
- No mid-period discounting.
- No fade period or two-stage growth.
- No section 11.4.2 consistency checks (operating leverage,
  terminal convergence enforcement).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union

from vcc_valuations.translator import SmokeAssumptionSet


@dataclass
class WaccBuild:
    """Component build-up of WACC.

    Exposed component-by-component (rather than as an opaque baseline
    scalar) so analysts or reviewers can rebuild the number from named
    inputs and substitute their own. Design principle adopted during
    Phase 3.5 calibration pass (24 May 2026).
    """

    risk_free_rate: float          # decimal, e.g. 0.043 = 4.30%
    equity_risk_premium: float     # decimal, e.g. 0.050 = 5.00%
    beta: float                    # unitless, e.g. 1.15
    cost_of_debt_pretax: float     # decimal, e.g. 0.060 = 6.00%
    tax_rate: float                # decimal, e.g. 0.30 = 30%
    equity_market_value: float     # currency units (e.g. AUD m)
    debt_market_value: float       # currency units (e.g. AUD m)

    @property
    def cost_of_equity(self) -> float:
        """CAPM cost of equity."""
        return self.risk_free_rate + self.beta * self.equity_risk_premium

    @property
    def after_tax_cost_of_debt(self) -> float:
        return self.cost_of_debt_pretax * (1.0 - self.tax_rate)

    @property
    def enterprise_value(self) -> float:
        return self.equity_market_value + self.debt_market_value

    @property
    def equity_weight(self) -> float:
        return self.equity_market_value / self.enterprise_value

    @property
    def debt_weight(self) -> float:
        return self.debt_market_value / self.enterprise_value

    @property
    def wacc(self) -> float:
        return (
            self.equity_weight * self.cost_of_equity
            + self.debt_weight * self.after_tax_cost_of_debt
        )

    def describe(self) -> List[str]:
        """One-line-per-component description for printable headers."""
        return [
            f"Rf={self.risk_free_rate:.2%}, ERP={self.equity_risk_premium:.2%}, beta={self.beta:.2f}",
            f"Re = Rf + beta x ERP = {self.cost_of_equity:.2%}",
            f"Rd_pretax={self.cost_of_debt_pretax:.2%}, tax={self.tax_rate:.0%}, Rd_after_tax={self.after_tax_cost_of_debt:.2%}",
            f"E={self.equity_market_value:,.0f}, D={self.debt_market_value:,.0f}, "
            f"E/V={self.equity_weight:.1%}, D/V={self.debt_weight:.1%}",
            f"WACC = {self.equity_weight:.3f} x {self.cost_of_equity:.2%} + "
            f"{self.debt_weight:.3f} x {self.after_tax_cost_of_debt:.2%} = {self.wacc:.2%}",
        ]


@dataclass
class FcfDcfResult:
    company_id: str
    scenario_id: str
    horizon_years: int

    # Year-by-year forecast (units: AUD millions)
    revenue: List[float]
    ebit_margin: List[float]
    ebit: List[float]
    tax: List[float]
    nopat: List[float]
    capex: List[float]
    da: List[float]
    delta_wc: List[float]
    free_cash_flow: List[float]

    # Terminal-state assumptions
    terminal_growth: float
    terminal_fcf: float
    terminal_value: float

    # Discount and valuation
    wacc: float
    pv_explicit: float
    pv_terminal: float
    enterprise_value: float
    net_debt: float
    equity_value: float
    shares_outstanding: float
    value_per_share: float

    # Diagnostics
    terminal_share_of_ev: float
    notes: List[str]


def _ensure_horizon(values: List[float], horizon: int, default: float = 0.0) -> List[float]:
    if not values:
        return [default] * horizon
    if len(values) >= horizon:
        return values[:horizon]
    return values + [values[-1]] * (horizon - len(values))


def run_fcf_dcf(
    aset: SmokeAssumptionSet,
    *,
    nominal_baseline_growth_pct: float = 2.0,
    baseline_wacc: Union[float, WaccBuild] = 0.085,
    baseline_terminal_growth: float = 0.025,
    da_pct_revenue: float = 0.073,
) -> FcfDcfResult:
    """Run the smoke-test FCF DCF.

    Args:
        aset: Output of translator.translate_to_assumption_set()
        nominal_baseline_growth_pct: GDP-adjacent nominal growth before
            scenario delta applied (%)
        baseline_wacc: Either a scalar baseline WACC (decimal) or a
            WaccBuild object that exposes the component build-up.
            Scenario deltas to risk-free rate and ERP applied on top.
        baseline_terminal_growth: Terminal growth before scenario delta
            (decimal)
        da_pct_revenue: Depreciation & amortisation as fraction of revenue
    """
    notes: List[str] = []
    H = aset.horizon_years
    baseline_wacc_scalar = (
        baseline_wacc.wacc if isinstance(baseline_wacc, WaccBuild) else baseline_wacc
    )

    # ---- Revenue trajectory ----
    # Apply volume_growth + price_mix deltas on top of baseline.
    volume_delta = aset.assumptions.get("volume_growth")
    price_delta = aset.assumptions.get("price_mix")
    vol_pct = volume_delta.annual_delta if volume_delta else 0.0
    px_pct = price_delta.annual_delta if price_delta else 0.0
    annual_revenue_growth = (nominal_baseline_growth_pct + vol_pct + px_pct) / 100.0

    revenue = []
    prev = aset.base_year_revenue
    for _ in range(H):
        prev = prev * (1 + annual_revenue_growth)
        revenue.append(prev)

    # ---- EBIT margin trajectory ----
    # Apply gross_margin / sga_pct_revenue / input_cost_pass_through deltas
    # additively as percentage-point changes to base-year margin.
    gm_delta = aset.assumptions.get("gross_margin")
    sga_delta = aset.assumptions.get("sga_pct_revenue")
    pass_through_delta = aset.assumptions.get("input_cost_pass_through")
    margin_delta_pp = sum(
        d.annual_delta for d in [gm_delta, pass_through_delta] if d is not None
    )
    margin_delta_pp -= sum(d.annual_delta for d in [sga_delta] if d is not None)
    margin_delta = margin_delta_pp / 100.0

    ebit_margin = [aset.base_year_ebit_margin + margin_delta] * H
    ebit = [r * m for r, m in zip(revenue, ebit_margin)]

    # ---- Tax (statutory rate, primary driver; effective_tax_rate derived) ----
    tax = [e * aset.base_year_tax_rate for e in ebit]
    nopat = [e - t for e, t in zip(ebit, tax)]

    # ---- Capex trajectory ----
    maintenance_delta = aset.assumptions.get("maintenance_capex_pct_revenue")
    growth_delta = aset.assumptions.get("growth_capex_pct_revenue")
    capex_pct_delta_pp = sum(
        d.annual_delta for d in [maintenance_delta, growth_delta] if d is not None
    )
    capex_pct = aset.base_year_capex_pct_revenue + capex_pct_delta_pp / 100.0
    capex = [r * capex_pct for r in revenue]

    # ---- D&A ----
    da = [r * da_pct_revenue for r in revenue]

    # ---- Working capital change (neutral for smoke test) ----
    delta_wc = [0.0] * H

    # ---- Free cash flow ----
    # FCFF = NOPAT + D&A - Capex - delta WC
    fcf = [n + d - c - w for n, d, c, w in zip(nopat, da, capex, delta_wc)]

    # ---- Discount rate ----
    rf_delta = aset.assumptions.get("risk_free_rate")
    erp_delta = aset.assumptions.get("equity_risk_premium")
    country_delta = aset.assumptions.get("country_risk_premium")
    rate_bps = sum(
        d.annual_delta for d in [rf_delta, erp_delta, country_delta] if d is not None
    )
    wacc = baseline_wacc_scalar + rate_bps / 10_000

    # ---- Terminal value ----
    tg_delta = aset.assumptions.get("terminal_growth_rate")
    terminal_growth = baseline_terminal_growth + (
        tg_delta.annual_delta / 10_000 if tg_delta else 0.0
    )
    if terminal_growth >= wacc:
        notes.append(
            f"Terminal growth {terminal_growth:.4f} >= WACC {wacc:.4f}; "
            "capping terminal_growth = WACC - 50bps to avoid blow-up."
        )
        terminal_growth = wacc - 0.005

    terminal_fcf = fcf[-1] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (wacc - terminal_growth)

    # ---- Discount to present value ----
    pv_explicit = sum(
        f / (1 + wacc) ** (t + 1) for t, f in enumerate(fcf)
    )
    pv_terminal = terminal_value / (1 + wacc) ** H
    enterprise_value = pv_explicit + pv_terminal

    # ---- Equity value ----
    equity_value = enterprise_value - aset.base_year_net_debt
    value_per_share = equity_value / aset.base_year_shares_outstanding

    # ---- Diagnostics ----
    terminal_share = pv_terminal / enterprise_value if enterprise_value else 0.0
    if terminal_share > 0.70:
        notes.append(
            f"Terminal value contributes {terminal_share:.1%} of EV; "
            "exceeds the section 11.4.2 / section 15.2 70% threshold -- "
            "force a sensitivity pass on terminal assumptions."
        )

    return FcfDcfResult(
        company_id=aset.company_id,
        scenario_id=aset.scenario_id,
        horizon_years=H,
        revenue=revenue,
        ebit_margin=ebit_margin,
        ebit=ebit,
        tax=tax,
        nopat=nopat,
        capex=capex,
        da=da,
        delta_wc=delta_wc,
        free_cash_flow=fcf,
        terminal_growth=terminal_growth,
        terminal_fcf=terminal_fcf,
        terminal_value=terminal_value,
        wacc=wacc,
        pv_explicit=pv_explicit,
        pv_terminal=pv_terminal,
        enterprise_value=enterprise_value,
        net_debt=aset.base_year_net_debt,
        equity_value=equity_value,
        shares_outstanding=aset.base_year_shares_outstanding,
        value_per_share=value_per_share,
        terminal_share_of_ev=terminal_share,
        notes=notes,
    )
