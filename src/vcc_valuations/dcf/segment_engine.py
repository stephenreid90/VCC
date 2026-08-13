"""Multi-segment FCFF engine ("M3") — CSL and other segment-level-valuation companies.

Methodology: value the firm bottom-up from its operating segments, then discount
unlevered free cash flow to the firm at the cost of equity (CSL discounts at Ke, not
WACC — it carries modest net debt and the framework prices the equity claim directly).

  * Per segment: revenue forecast (per-year growth path or flat CAGR) and an operating-
    result margin that glides linearly from the FY25 base by a cumulative peer-gap uplift.
  * Group EBIT = sum of segment operating results less a growing corporate/unallocated line.
  * Unlevered FCFF = EBIT x (1 - tax) + D&A - capex - working-capital change.
  * Terminal value normalises to a binding terminal EBIT margin with terminal capex = D&A
    (steady state), grown by g and capitalised at (Ke - g).
  * Enterprise value -> equity by deducting net debt and restructuring cash to come; per
    share in USD, then translated to AUD at the reporting-date FX rate.

Inputs carry ZERO derived values; every derived quantity is computed here and exposed via
``derivation()`` for audit, mirroring the industrial and bank engines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from vcc_valuations.derivation import DerivationBuilder


@dataclass
class SegmentSpec:
    name: str
    fy25_revenue: float
    fy25_or_margin: float
    growth_path: List[float]   # 6 per-year growth rates FY26..FY31 (flat CAGR -> repeated)
    margin_uplift_cum: float   # cumulative OR-margin uplift by FY31 (linear glide)


@dataclass
class SegmentInputs:
    company_id: str
    scenario_id: str
    horizon_years: int
    segments: List[SegmentSpec]
    corporate_fy25: float
    corporate_growth: float
    net_interest_fy25: float
    net_interest_decline: float
    capex_pct_revenue: float
    da_pct_revenue: float
    wc_change_pct_revenue_change: float
    terminal_capex_pct_revenue: float
    terminal_ebit_margin: float
    terminal_growth: float
    tax_rate: float
    cost_of_equity: float
    net_debt: float
    restructuring_cash_to_come: float
    shares_outstanding_m: float
    fx_aud_per_usd: float


@dataclass
class SegmentResult:
    company_id: str
    scenario_id: str
    year_labels: List[str]                 # FY25..FY31
    segment_revenue: Dict[str, List[float]]
    segment_or: Dict[str, List[float]]
    group_revenue: List[float]
    group_segment_or: List[float]
    corporate: List[float]
    group_ebit: List[float]
    nopat: List[float]                     # FY26..FY31
    da: List[float]
    capex: List[float]                     # negative
    wc_change: List[float]                 # negative
    fcff: List[float]                      # FY26..FY31
    mid_times: List[float]
    discount_factors: List[float]
    pv_fcff: List[float]                   # explicit FY27..FY31 (FY26 = 0)
    pv_explicit: float
    terminal_fcff: float
    terminal_value: float
    terminal_discount_factor: float
    pv_terminal: float
    enterprise_value: float
    net_debt: float
    restructuring_cash_to_come: float
    equity_value: float
    shares_outstanding_m: float
    value_per_share_usd: float
    value_per_share_aud: float
    terminal_share_of_ev: float


class SegmentEngine:
    """``run(SegmentInputs) -> SegmentResult``. Bottom-up multi-segment FCFF, Ke discount."""

    def run(self, inp: SegmentInputs) -> SegmentResult:
        H = inp.horizon_years           # 5 explicit forecast years beyond FY26 anchor
        n = H + 2                        # FY25 (anchor base) + FY26..FY31 => 7 points
        labels = ["FY25"] + [f"FY{26 + k}" for k in range(H + 1)]

        seg_rev: Dict[str, List[float]] = {}
        seg_or: Dict[str, List[float]] = {}
        for seg in inp.segments:
            rev = [seg.fy25_revenue]
            for y in range(1, n):
                rev.append(rev[-1] * (1.0 + seg.growth_path[y - 1]))
            # margin glides linearly from FY25 base by the cumulative uplift over 6 years
            marg = [seg.fy25_or_margin + seg.margin_uplift_cum * (y / (n - 1)) for y in range(n)]
            seg_rev[seg.name] = rev
            seg_or[seg.name] = [rev[y] * marg[y] for y in range(n)]

        group_rev = [sum(seg_rev[s.name][y] for s in inp.segments) for y in range(n)]
        group_or = [sum(seg_or[s.name][y] for s in inp.segments) for y in range(n)]
        corporate = [inp.corporate_fy25 * (1.0 + inp.corporate_growth) ** y for y in range(n)]
        group_ebit = [group_or[y] + corporate[y] for y in range(n)]

        # FCFF for FY26..FY31 (indices 1..n-1)
        nopat, da, capex, wc, fcff = [], [], [], [], []
        for y in range(1, n):
            np = group_ebit[y] * (1.0 - inp.tax_rate)
            da_y = group_rev[y] * inp.da_pct_revenue
            cx = -group_rev[y] * inp.capex_pct_revenue
            wc_y = -(group_rev[y] - group_rev[y - 1]) * inp.wc_change_pct_revenue_change
            nopat.append(np); da.append(da_y); capex.append(cx); wc.append(wc_y)
            fcff.append(np + da_y + cx + wc_y)

        # discounting: FY26 mid-time zero (anchor, excluded from explicit PV); FY27..FY31 mid-year
        ke = inp.cost_of_equity
        mid = [0.0] + [k - 0.5 for k in range(1, H + 1)]   # ssot-allow: structural mid-period offset
        dfs = [1.0 / (1.0 + ke) ** t for t in mid]
        pv = [0.0] + [fcff[i] * dfs[i] for i in range(1, H + 1)]
        pv_explicit = sum(pv)

        fy31_rev = group_rev[-1]
        terminal_fcff = fy31_rev * (
            inp.terminal_ebit_margin * (1.0 - inp.tax_rate)
            + inp.da_pct_revenue - inp.terminal_capex_pct_revenue
            - inp.terminal_growth * inp.wc_change_pct_revenue_change
        ) * (1.0 + inp.terminal_growth)
        tv = terminal_fcff / (ke - inp.terminal_growth)
        tdf = 1.0 / (1.0 + ke) ** H
        pv_terminal = tv * tdf

        ev = pv_explicit + pv_terminal
        equity = ev - inp.net_debt - inp.restructuring_cash_to_come
        vps_usd = equity / inp.shares_outstanding_m
        vps_aud = vps_usd * inp.fx_aud_per_usd

        return SegmentResult(
            company_id=inp.company_id, scenario_id=inp.scenario_id, year_labels=labels,
            segment_revenue=seg_rev, segment_or=seg_or, group_revenue=group_rev,
            group_segment_or=group_or, corporate=corporate, group_ebit=group_ebit,
            nopat=nopat, da=da, capex=capex, wc_change=wc, fcff=fcff,
            mid_times=mid, discount_factors=dfs, pv_fcff=pv, pv_explicit=pv_explicit,
            terminal_fcff=terminal_fcff, terminal_value=tv, terminal_discount_factor=tdf,
            pv_terminal=pv_terminal, enterprise_value=ev, net_debt=inp.net_debt,
            restructuring_cash_to_come=inp.restructuring_cash_to_come, equity_value=equity,
            shares_outstanding_m=inp.shares_outstanding_m, value_per_share_usd=vps_usd,
            value_per_share_aud=vps_aud,
            terminal_share_of_ev=(pv_terminal / ev if ev else 0.0),
        )

    def per_year_derivation(self, r: SegmentResult):
        """The per-year group build as an auditable Derivation (parity item).

        One step per forecast year for group revenue, group EBIT and FCFF, so the
        year-by-year build reads out of the engine (``.as_rows()`` for a workings view).
        Skips the FY25 anchor. Headline = the final year's FCFF.
        """
        b = DerivationBuilder(f"per_year_build[{r.scenario_id}]")
        for y in range(1, len(r.year_labels)):        # FY26..FY31
            lab = r.year_labels[y]
            b.step(f"{lab}_rev", f"{lab} group revenue", r.group_revenue[y],
                   "sum of segment revenue (revenue x growth path)", {}, units="USD m")
            b.step(f"{lab}_ebit", f"{lab} group EBIT", r.group_ebit[y],
                   "segment operating result - corporate/unallocated", {}, units="USD m")
            b.step(f"{lab}_fcff", f"{lab} FCFF", r.fcff[y - 1],
                   "EBIT x (1-tax) + D&A - capex - dWC", {}, units="USD m")
        return b.build(result_key=f"{r.year_labels[-1]}_fcff")

    def derivation(self, inp: SegmentInputs, r: SegmentResult):
        """The §4 FCFF->per-share bridge as an auditable trace (headline = value per share AUD)."""
        b = DerivationBuilder(f"segment_value[{inp.scenario_id}]")
        b.step("pv_exp", "Sum of explicit PV (FY27-FY31)", r.pv_explicit, "sum of discounted FCFF", {}, units="USD m")
        b.step("pv_tv", "PV of terminal value", r.pv_terminal,
               "terminal_value * discount_factor",
               {"terminal_value": r.terminal_value, "tdf": r.terminal_discount_factor}, units="USD m")
        b.step("ev", "Enterprise value", r.enterprise_value, "explicit PV + PV terminal", {}, units="USD m")
        b.step("nd", "Less: net debt", -inp.net_debt, "less net debt", {}, units="USD m")
        b.step("rc", "Less: restructuring cash to come", -inp.restructuring_cash_to_come, "less restructuring", {}, units="USD m")
        b.step("eq", "Equity value", r.equity_value, "EV - net debt - restructuring", {}, units="USD m")
        b.step("vps_usd", "Value per share (USD)", r.value_per_share_usd,
               "equity / shares", {"shares_m": inp.shares_outstanding_m}, units="USD")
        b.step("vps_aud", "Value per share (AUD)", r.value_per_share_aud,
               "USD per share * FX", {"fx_aud_per_usd": inp.fx_aud_per_usd}, units="AUD")
        return b.build(result_key="vps_aud")
