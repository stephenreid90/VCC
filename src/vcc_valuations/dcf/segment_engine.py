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
from typing import Dict, List, Optional

from vcc_valuations.derivation import DerivationBuilder
from vcc_valuations.dcf.fcf_engine import terminal_share_warning


@dataclass
class SegmentSpec:
    name: str
    fy25_revenue: float
    fy25_or_margin: float
    growth_path: List[float]   # H+1 per-year growth rates FY26..FY(26+H) (flat CAGR -> repeated)
    margin_uplift_cum: float   # cumulative OR-margin uplift reached by the end of margin_uplift_years
    # D-71 (14 Oct 2026): the uplift glides linearly from FY25 over this many years
    # and then HOLDS -- it is the company's stated FY31 steady state, not a trend
    # to run on to FY36. Declared in data (segment_fcff.timing.margin_uplift_years).
    margin_uplift_years: int = 6


@dataclass
class SegmentInputs:
    company_id: str
    scenario_id: str
    horizon_years: int
    segments: List[SegmentSpec]
    corporate_fy25: float
    corporate_growth: float
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
    # D-71 / D-62 (routed 14 Oct 2026): the headline terminal form. "gordon"
    # capitalises the normalised terminal FCFF. "excess_return_convergence" holds the
    # closing invested-capital base C (D-67, supplied as terminal_invested_capital),
    # sets next-year NOPAT = C x R with R the return the explicit period leaves it
    # earning, and converges R to Ke over convergence_years, then Gordon -- the same
    # two_stage algebra as the industrial and bank engines. The assembler picks
    # convergence where a decay horizon is declared and Gordon, saying so, where none is.
    terminal_form: str = "gordon"
    convergence_years: Optional[float] = None
    terminal_invested_capital: Optional[float] = None


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
    terminal_form: str = "gordon"
    convergence_years: Optional[float] = None
    terminal_earned_return: Optional[float] = None
    # §11.4.2 sensitivity-pass warning, shared with the industrial engine.
    warnings: List[str] = field(default_factory=list)


class SegmentEngine:
    """``run(SegmentInputs) -> SegmentResult``. Bottom-up multi-segment FCFF, Ke discount."""

    def run(self, inp: SegmentInputs) -> SegmentResult:
        H = inp.horizon_years           # explicit forecast years beyond the FY26 anchor (10 under D-71)
        n = H + 2                        # FY25 (anchor base) + FY26..FY(26+H)
        labels = ["FY25"] + [f"FY{26 + k}" for k in range(H + 1)]

        seg_rev: Dict[str, List[float]] = {}
        seg_or: Dict[str, List[float]] = {}
        for seg in inp.segments:
            if len(seg.growth_path) != H + 1:
                raise ValueError(f"{seg.name}: growth_path has {len(seg.growth_path)} entries; need {H + 1}")
            rev = [seg.fy25_revenue]
            for y in range(1, n):
                rev.append(rev[-1] * (1.0 + seg.growth_path[y - 1]))
            # margin glides linearly from the FY25 base to the cumulative uplift over
            # margin_uplift_years, then holds (D-71: the glide endpoint is the stated steady state)
            U = seg.margin_uplift_years
            marg = [seg.fy25_or_margin + seg.margin_uplift_cum * min(y / U, 1.0) for y in range(n)]
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

        fy31_rev = group_rev[-1]   # the final explicit year (name kept from the five-year build)
        terminal_fcff = fy31_rev * (
            inp.terminal_ebit_margin * (1.0 - inp.tax_rate)
            + inp.da_pct_revenue - inp.terminal_capex_pct_revenue
            - inp.terminal_growth * inp.wc_change_pct_revenue_change
        ) * (1.0 + inp.terminal_growth)
        terminal_earned_return = None
        if inp.terminal_form == "excess_return_convergence":
            if inp.convergence_years is None or inp.terminal_invested_capital is None:
                raise ValueError("terminal_form='excess_return_convergence' requires convergence_years "
                                 "and terminal_invested_capital (D-67)")
            from vcc_valuations.dcf.terminal_value import two_stage
            g = inp.terminal_growth
            # the return the explicit period leaves the capital base earning, on the
            # normalised terminal NOPAT (terminal margin, next year) -- mirrors fcf_engine
            terminal_nopat_next = fy31_rev * inp.terminal_ebit_margin * (1.0 - inp.tax_rate) * (1.0 + g)
            terminal_earned_return = terminal_nopat_next / inp.terminal_invested_capital
            tv = two_stage(inp.terminal_invested_capital, terminal_earned_return, ke, g, inp.convergence_years)
        elif inp.terminal_form == "gordon":
            tv = terminal_fcff / (ke - inp.terminal_growth)
        else:
            raise ValueError(f"terminal_form must be 'gordon' or 'excess_return_convergence', got {inp.terminal_form!r}")
        tdf = 1.0 / (1.0 + ke) ** H
        pv_terminal = tv * tdf

        ev = pv_explicit + pv_terminal
        equity = ev - inp.net_debt - inp.restructuring_cash_to_come
        vps_usd = equity / inp.shares_outstanding_m
        vps_aud = vps_usd * inp.fx_aud_per_usd

        terminal_share = pv_terminal / ev if ev else 0.0
        warnings: List[str] = []
        tv_warning = terminal_share_warning(terminal_share, "EV")
        if tv_warning:
            warnings.append(tv_warning)

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
            terminal_share_of_ev=terminal_share,
            terminal_form=inp.terminal_form, convergence_years=inp.convergence_years,
            terminal_earned_return=terminal_earned_return,
            warnings=warnings,
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
                   "sum of segment revenue (revenue x growth path)",
                   {name: rev[y] for name, rev in r.segment_revenue.items()}, units="USD m")
            b.step(f"{lab}_ebit", f"{lab} group EBIT", r.group_ebit[y],
                   "segment operating result - corporate/unallocated",
                   {"segment_operating_result": r.group_segment_or[y],
                    "corporate": r.corporate[y]}, units="USD m")
            b.step(f"{lab}_fcff", f"{lab} FCFF", r.fcff[y - 1],
                   "NOPAT + D&A + capex + dWC (capex and dWC are carried negative)",
                   {"nopat": r.nopat[y - 1], "da": r.da[y - 1],
                    "capex": r.capex[y - 1], "delta_wc": r.wc_change[y - 1]}, units="USD m")
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
