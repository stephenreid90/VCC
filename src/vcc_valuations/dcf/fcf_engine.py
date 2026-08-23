"""
Production single-segment industrial FCFF engine (engine implementation plan,
step 10 / milestone M1).

This replaces the Phase-3.5 ``fcf_stub`` for the industrial archetype. Unlike the
stub it reproduces the *audited workbook* mechanics line-for-line, so it ties to
the regression oracle to the cent rather than merely proving pipeline shape:

    - a fractional STUB period from the valuation date to the first fiscal
      year-end (revenue = base-year revenue x stub-fraction);
    - MID-PERIOD discounting measured from the valuation date (stub sits in
      front of the explicit years);
    - a per-year EBIT-margin GLIDE built as base margin + a transformation
      overlay + a (negative) input-cost roll-off overlay, shown as separate
      rows (methodology section 11: industry baseline + company offset explicit);
    - a per-year applied-tax GLIDE (effective -> blended statutory);
    - a capex step (transition % -> steady-state %);
    - a Gordon-growth terminal capitalising the last explicit FCFF grown at g,
      discounted at the end of the final explicit year;
    - a granular equity bridge (EV -> net debt at the valuation date -> net
      separation/one-off adjustments -> AASB 16 leases -> equity; ÷ shares; x FX
      only at the per-share line).

Scope note (M1): the engine consumes a resolved :class:`FcfEngineInputs` that
mirrors a company's audited-workbook Assumptions sheet. Populating that object
from the full driver-keyed ``AssumptionSet`` (the ``linkage/`` + ``assumptions/``
layers) is milestone M2; the mapping is deliberately left as a seam here.

Segment-level forecasting, the binding-terminal-margin fix (terminal capex =
D&A) and FX-by-segment are CSL/M3 concerns and are flagged, not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union

from vcc_valuations.assumptions.wacc import WaccBuild

# Terminal share of EV above which a sensitivity pass is required (methodology
# section 11.4.2 / 15.2). Non-blocking by owner decision R3 (25 June 2026):
# emit a warning that triggers a sensitivity pass; never auto-suppress.
#
# Single definition for all three engines: ``bank_engine`` and ``segment_engine``
# import this constant and :func:`terminal_share_warning` rather than restating
# the threshold, so there is one number and one message across the archetypes.
TERMINAL_SHARE_THRESHOLD = 0.70

# How the terminal FCFF is struck. Declared per valuation, never defaulted —
# see FcfEngineInputs.terminal_reinvestment.
TERMINAL_REINVESTMENT_MODES = ("capitalise_last_fcff", "normalised")


def terminal_share_warning(terminal_share: float, denominator: str = "EV") -> Optional[str]:
    """The §11.4.2 sensitivity-pass warning, or ``None`` when under threshold.

    ``denominator`` names what the terminal is a share *of*, so the bank engine
    can say "the equity claim" where the FCFF engines say "EV". Non-blocking:
    callers append the string to their ``warnings`` list and carry on.
    """
    if terminal_share <= TERMINAL_SHARE_THRESHOLD:
        return None
    return (
        f"Terminal value is {terminal_share:.1%} of {denominator} (> "
        f"{TERMINAL_SHARE_THRESHOLD:.0%}); methodology section 11.4.2 "
        "requires a sensitivity pass on terminal assumptions "
        "(non-blocking, per owner decision R3)."
    )


@dataclass
class EquityBridge:
    """EV -> equity bridge components, all in the reporting currency (AUD m).

    Sign convention matches the workbook Equity Bridge sheet: every component is
    a claim *ahead of* ordinary equity and is therefore subtracted from EV.
    """

    net_debt_at_valuation: float
    equity_bridge_adjustments_net: float  # net separation / one-off obligations
    lease_liabilities: float              # AASB 16, Approach A (leases = debt)
    shares_outstanding: float
    fx_rate: float = 1.0                  # per-share FX; applied ONLY at the per-share line
    market_reference_price: Optional[float] = None

    # Period-A walk inputs, retained so the bridge can trace itself (workbook
    # Equity Bridge B6-B11). None when the bridge was built without a walk.
    net_debt_anchor: Optional[float] = None
    period_a_years: Optional[float] = None
    operating_cash_flow_run_rate: Optional[float] = None
    capex_run_rate: Optional[float] = None

    @classmethod
    def from_anchor(
        cls,
        *,
        net_debt_anchor: float,
        period_a_years: float,
        operating_cash_flow_run_rate: float,
        capex_run_rate: float,
        equity_bridge_adjustments_net: float,
        lease_liabilities: float,
        shares_outstanding: float,
        fx_rate: float = 1.0,
        market_reference_price: Optional[float] = None,
    ) -> "EquityBridge":
        """Roll net debt from the financials anchor date to the valuation date.

        Period-A walk (methodology section 7): net debt falls by operating cash
        generated and rises by capex paid over the anchor->valuation gap.
        """
        net_debt_at_valuation = (
            net_debt_anchor
            - operating_cash_flow_run_rate * period_a_years
            + capex_run_rate * period_a_years
        )
        return cls(
            net_debt_at_valuation=net_debt_at_valuation,
            equity_bridge_adjustments_net=equity_bridge_adjustments_net,
            lease_liabilities=lease_liabilities,
            shares_outstanding=shares_outstanding,
            fx_rate=fx_rate,
            market_reference_price=market_reference_price,
            net_debt_anchor=net_debt_anchor,
            period_a_years=period_a_years,
            operating_cash_flow_run_rate=operating_cash_flow_run_rate,
            capex_run_rate=capex_run_rate,
        )

    def derivation(self, enterprise_value: float):
        """The equity bridge as a fully-traceable derivation (workbook Equity Bridge).

        Given the DCF enterprise value, exposes the Period-A net-debt walk
        (B6-B11, when the walk inputs are present) and the per-share bridge
        (B27 EV -> B28 net debt -> B29 adjustments -> B30 leases -> B31 equity
        -> B33 value per share, plus B37 discount to market). Every row is a
        named step with its formula; nothing derived is stored.
        """
        from vcc_valuations.derivation import DerivationBuilder

        b = DerivationBuilder("equity_bridge")

        if self.period_a_years is not None:
            anchor = b.step(
                "B6", "Net debt at anchor", self.net_debt_anchor, "from financials (§5.3 anchor)",
                {"net_debt_anchor": self.net_debt_anchor}, cell="B6", units="AUD m",
            )
            less_ocf = b.step(
                "B7", "less: operating cash flow in Period A",
                -self.operating_cash_flow_run_rate * self.period_a_years,
                "-OCF_run_rate * period_a_years",
                {"OCF_run_rate": self.operating_cash_flow_run_rate,
                 "period_a_years": self.period_a_years}, cell="B7", units="AUD m",
            )
            plus_capex = b.step(
                "B8", "plus: capex paid in Period A",
                self.capex_run_rate * self.period_a_years,
                "capex_run_rate * period_a_years",
                {"capex_run_rate": self.capex_run_rate,
                 "period_a_years": self.period_a_years}, cell="B8", units="AUD m",
            )
            subtotal = b.step(
                "B10", "Net debt walk subtotal", less_ocf + plus_capex,
                "B7 + B8", {"B7": less_ocf, "B8": plus_capex}, cell="B10", units="AUD m",
            )
            b.step(
                "B11", "Net debt at valuation date", anchor + subtotal,
                "B6 + B10", {"B6": anchor, "B10": subtotal}, cell="B11", units="AUD m",
            )

        ev = b.step(
            "B27", "Enterprise value (from DCF)", enterprise_value, "from DCF Worksheet",
            {"enterprise_value": enterprise_value}, cell="B27", units="AUD m",
        )
        less_nd = b.step(
            "B28", "less: net debt at valuation", -self.net_debt_at_valuation,
            "-net_debt_at_valuation", {"net_debt_at_valuation": self.net_debt_at_valuation},
            cell="B28", units="AUD m",
        )
        less_adj = b.step(
            "B29", "less: equity-bridge adjustments (net)", -self.equity_bridge_adjustments_net,
            "-equity_bridge_adjustments_net",
            {"equity_bridge_adjustments_net": self.equity_bridge_adjustments_net},
            cell="B29", units="AUD m",
        )
        less_leases = b.step(
            "B30", "less: AASB 16 lease liabilities", -self.lease_liabilities,
            "-lease_liabilities", {"lease_liabilities": self.lease_liabilities},
            cell="B30", units="AUD m",
        )
        equity_value = b.step(
            "B31", "Equity value", ev + less_nd + less_adj + less_leases,
            "B27 + B28 + B29 + B30",
            {"B27": ev, "B28": less_nd, "B29": less_adj, "B30": less_leases},
            cell="B31", units="AUD m",
        )
        vps = b.step(
            "B33", "Value per share", equity_value / self.shares_outstanding,
            "equity_value / shares_outstanding",
            {"equity_value": equity_value, "shares_outstanding": self.shares_outstanding},
            cell="B33", units="AUD/sh",
        )
        if self.market_reference_price:
            b.step(
                "B37", "Discount / (premium) vs market",
                vps * self.fx_rate / self.market_reference_price - 1.0,
                "value_per_share / market_reference_price - 1",
                {"value_per_share": vps * self.fx_rate,
                 "market_reference_price": self.market_reference_price}, cell="B37", units="%",
            )
        return b.build(result_key="B33")


@dataclass
class FcfEngineInputs:
    """Resolved, single-segment industrial FCFF inputs (one company x scenario).

    Mirrors the audited-workbook Assumptions sheet. All rate/margin fields are
    decimals (0.141 = 14.1%). The transformation and gas-roll-off overlays are
    per-year CUMULATIVE deltas versus the base margin, length == horizon_years.
    The tax glide and capex list are also length == horizon_years (year 1..H);
    the stub takes its own explicit scalars.
    """

    company_id: str
    scenario_id: str
    functional_currency: str

    horizon_years: int
    stub_years: float                     # valuation date -> first FY-end, in years

    # Revenue
    base_year_revenue: float
    revenue_growth: float                 # constant compound rate (chain-derived)

    # EBIT margin glide (base + overlays), shown as separate rows
    base_ebit_margin: float
    margin_transformation: List[float]    # per-year cumulative pp delta (len H)
    margin_gas_rolloff: List[float]       # per-year cumulative pp delta (len H, <= 0)

    # Tax
    stub_tax_rate: float
    tax_rate_glide: List[float]           # year 1..H applied rates (len H)

    # Cash-flow bridge
    da_pct_revenue: float
    capex_pct_stub: float
    capex_pct: List[float]                # year 1..H capex/revenue (len H)
    # Terminal reinvestment mode. Declared, never defaulted: an engine that
    # silently capitalises the last explicit FCFF looks identical, from the
    # outside, to one that has normalised reinvestment properly — the same
    # failure the bank working-capital exemption is written to avoid
    # (working_capital_treatment.md section 3).
    #   "capitalise_last_fcff" — grow the final explicit FCFF at g. Carries the
    #       explicit period's capex and working-capital drag into perpetuity.
    #   "normalised" — rebuild terminal FCFF from the final margin, with capex
    #       set to terminal_capex_pct_revenue and the working-capital drag at
    #       g x working_capital_intensity (working_capital_treatment.md
    #       section 1; the same shape the segment engine already uses).
    terminal_reinvestment: str

    delta_wc: List[float] = field(default_factory=list)   # year 1..H (len H); [] -> zeros
    delta_wc_stub: float = 0.0

    # Required when terminal_reinvestment == "normalised", forbidden otherwise.
    working_capital_intensity: Optional[float] = None
    terminal_capex_pct_revenue: Optional[float] = None

    # Discounting
    wacc: Union[WaccBuild, float] = 0.085

    # Terminal
    terminal_growth: float = 0.025

    # Equity bridge
    equity_bridge: Optional[EquityBridge] = None

    def __post_init__(self) -> None:
        H = self.horizon_years
        for name, vec in (
            ("margin_transformation", self.margin_transformation),
            ("margin_gas_rolloff", self.margin_gas_rolloff),
            ("tax_rate_glide", self.tax_rate_glide),
            ("capex_pct", self.capex_pct),
        ):
            if len(vec) != H:
                raise ValueError(f"{name} must have length horizon_years={H}, got {len(vec)}")
        if not self.delta_wc:
            self.delta_wc = [0.0] * H
        elif len(self.delta_wc) != H:
            raise ValueError(f"delta_wc must have length {H}, got {len(self.delta_wc)}")

        if self.terminal_reinvestment not in TERMINAL_REINVESTMENT_MODES:
            raise ValueError(
                f"terminal_reinvestment must be one of {TERMINAL_REINVESTMENT_MODES}, "
                f"got {self.terminal_reinvestment!r}"
            )
        needed = (self.working_capital_intensity, self.terminal_capex_pct_revenue)
        if self.terminal_reinvestment == "normalised":
            if any(x is None for x in needed):
                raise ValueError(
                    "terminal_reinvestment='normalised' requires both "
                    "working_capital_intensity and terminal_capex_pct_revenue."
                )
        elif any(x is not None for x in needed):
            raise ValueError(
                "working_capital_intensity / terminal_capex_pct_revenue are only "
                "read when terminal_reinvestment='normalised'; passing them with "
                "'capitalise_last_fcff' would silently do nothing."
            )

    @property
    def wacc_scalar(self) -> float:
        return self.wacc.wacc if isinstance(self.wacc, WaccBuild) else float(self.wacc)


@dataclass
class FcfDcfResult:
    company_id: str
    scenario_id: str
    horizon_years: int
    functional_currency: str

    # Period labels: "Stub", "Y1", ... "YH"
    period_labels: List[str]

    # Year-by-year forecast (stub first), units: reporting currency millions
    revenue: List[float]
    ebit_margin: List[float]
    ebit: List[float]
    applied_tax_rate: List[float]
    tax: List[float]              # negative
    nopat: List[float]
    da: List[float]
    capex: List[float]            # negative
    delta_wc: List[float]         # negative (a use of cash) or zero
    fcff: List[float]

    # Discounting
    wacc: float
    mid_times: List[float]
    discount_factors: List[float]
    pv_fcff: List[float]

    # Terminal
    terminal_growth: float
    terminal_fcff: float
    terminal_reinvestment: str
    terminal_capex_pct_revenue: Optional[float]
    terminal_working_capital_intensity: Optional[float]
    terminal_value: float
    terminal_end_time: float
    terminal_discount_factor: float

    # Enterprise value
    pv_explicit: float
    pv_terminal: float
    enterprise_value: float

    # Equity bridge
    net_debt_at_valuation: float
    equity_bridge_adjustments_net: float
    lease_liabilities: float
    equity_value: float
    shares_outstanding: float
    value_per_share: float               # in functional currency
    value_per_share_reported: float      # after FX (== value_per_share when fx==1)

    # Diagnostics
    terminal_share_of_ev: float
    market_reference_price: Optional[float]
    discount_to_market: Optional[float]
    warnings: List[str]
    notes: List[str]


class FcfEngine:
    """Single-segment industrial FCFF DCF. ``run(inputs) -> FcfDcfResult``."""

    def run(self, inp: FcfEngineInputs) -> FcfDcfResult:
        H = inp.horizon_years
        wacc = inp.wacc_scalar
        g = inp.terminal_growth
        notes: List[str] = []
        warnings: List[str] = []

        if g >= wacc:
            raise ValueError(
                f"terminal growth {g:.4f} >= WACC {wacc:.4f}; Gordon terminal undefined."
            )

        # ---- Revenue (stub = base x stub-fraction; years compound from base) ----
        revenue = [inp.base_year_revenue * inp.stub_years]
        for k in range(1, H + 1):
            revenue.append(inp.base_year_revenue * (1.0 + inp.revenue_growth) ** k)

        # ---- EBIT margin glide (stub at base; years = base + overlays) ----
        ebit_margin = [inp.base_ebit_margin]
        for k in range(H):
            ebit_margin.append(
                inp.base_ebit_margin
                + inp.margin_transformation[k]
                + inp.margin_gas_rolloff[k]
            )
        ebit = [r * m for r, m in zip(revenue, ebit_margin)]

        # ---- Tax (per-year applied rate; stub at effective) ----
        applied_tax_rate = [inp.stub_tax_rate] + list(inp.tax_rate_glide)
        tax = [-e * t for e, t in zip(ebit, applied_tax_rate)]
        nopat = [e + t for e, t in zip(ebit, tax)]

        # ---- D&A and capex ----
        da = [r * inp.da_pct_revenue for r in revenue]
        capex_pct_all = [inp.capex_pct_stub] + list(inp.capex_pct)
        capex = [-r * c for r, c in zip(revenue, capex_pct_all)]

        # ---- Working-capital change ----
        delta_wc = [-inp.delta_wc_stub] + [-w for w in inp.delta_wc]

        # ---- Unlevered FCFF ----
        fcff = [n + d + c + w for n, d, c, w in zip(nopat, da, capex, delta_wc)]

        # ---- Mid-period discounting from the valuation date ----
        # stub occupies [0, stub_years]; explicit year k occupies
        # [stub + k-1, stub + k]; mid-points as below.
        mid_times = [inp.stub_years / 2.0]
        for k in range(1, H + 1):
            mid_times.append(inp.stub_years + k - 0.5)
        discount_factors = [1.0 / (1.0 + wacc) ** t for t in mid_times]
        pv_fcff = [f * df for f, df in zip(fcff, discount_factors)]

        # ---- Terminal value (Gordon) ----
        # Two declared modes (no default — see FcfEngineInputs).
        #
        # "capitalise_last_fcff" grows the final explicit FCFF at g. It is the
        # original DNL workbook's treatment, and it silently carries the final
        # explicit year's capex/revenue and working-capital build into
        # perpetuity — which is wrong whenever explicit growth differs from g.
        #
        # "normalised" rebuilds the terminal from its components: the final
        # margin and tax rate, D&A, a stated terminal capex, and a
        # working-capital drag of g x intensity (working_capital_treatment.md
        # section 1). Same algebra the segment engine uses for CSL, so the two
        # FCFF engines strike the terminal the same way.
        if inp.terminal_reinvestment == "normalised":
            terminal_fcff = revenue[-1] * (1.0 + g) * (
                ebit_margin[-1] * (1.0 - applied_tax_rate[-1])
                + inp.da_pct_revenue
                - inp.terminal_capex_pct_revenue
                - g * inp.working_capital_intensity
            )
        else:
            terminal_fcff = fcff[-1] * (1.0 + g)
        terminal_value = terminal_fcff / (wacc - g)
        terminal_end_time = inp.stub_years + H
        terminal_discount_factor = 1.0 / (1.0 + wacc) ** terminal_end_time
        pv_terminal = terminal_value * terminal_discount_factor

        pv_explicit = sum(pv_fcff)
        enterprise_value = pv_explicit + pv_terminal
        terminal_share = pv_terminal / enterprise_value if enterprise_value else 0.0

        tv_warning = terminal_share_warning(terminal_share, "EV")
        if tv_warning:
            warnings.append(tv_warning)

        # ---- Equity bridge ----
        eb = inp.equity_bridge
        if eb is None:
            raise ValueError("FcfEngineInputs.equity_bridge is required to value equity.")
        equity_value = (
            enterprise_value
            - eb.net_debt_at_valuation
            - eb.equity_bridge_adjustments_net
            - eb.lease_liabilities
        )
        value_per_share = equity_value / eb.shares_outstanding
        value_per_share_reported = value_per_share * eb.fx_rate

        discount_to_market: Optional[float] = None
        if eb.market_reference_price:
            discount_to_market = value_per_share_reported / eb.market_reference_price - 1.0

        # single-WACC discipline is structural: one scalar used for every period
        # and the terminal. Recorded for the trace.
        notes.append(
            f"Single WACC {wacc:.4%} applied to all {H} explicit years, the stub, "
            "and the terminal (section 3.5 single-discount-rate discipline)."
        )
        if inp.terminal_reinvestment == "normalised":
            # Components are carried on the result (terminal_capex_pct_revenue,
            # terminal_working_capital_intensity) rather than restated here.
            notes.append(
                "Terminal reinvestment normalised: terminal capex set to the "
                "declared terminal rate and the working-capital drag struck at "
                "g x intensity, not carried over from the final explicit year."
            )
        else:
            notes.append(
                "Terminal FCFF capitalises the final explicit year's FCFF grown "
                "at g; the explicit period's capex and working-capital rates "
                "carry into perpetuity."
            )

        return FcfDcfResult(
            company_id=inp.company_id,
            scenario_id=inp.scenario_id,
            horizon_years=H,
            functional_currency=inp.functional_currency,
            period_labels=["Stub"] + [f"Y{k}" for k in range(1, H + 1)],
            revenue=revenue,
            ebit_margin=ebit_margin,
            ebit=ebit,
            applied_tax_rate=applied_tax_rate,
            tax=tax,
            nopat=nopat,
            da=da,
            capex=capex,
            delta_wc=delta_wc,
            fcff=fcff,
            wacc=wacc,
            mid_times=mid_times,
            discount_factors=discount_factors,
            pv_fcff=pv_fcff,
            terminal_growth=g,
            terminal_fcff=terminal_fcff,
            terminal_reinvestment=inp.terminal_reinvestment,
            terminal_capex_pct_revenue=inp.terminal_capex_pct_revenue,
            terminal_working_capital_intensity=inp.working_capital_intensity,
            terminal_value=terminal_value,
            terminal_end_time=terminal_end_time,
            terminal_discount_factor=terminal_discount_factor,
            pv_explicit=pv_explicit,
            pv_terminal=pv_terminal,
            enterprise_value=enterprise_value,
            net_debt_at_valuation=eb.net_debt_at_valuation,
            equity_bridge_adjustments_net=eb.equity_bridge_adjustments_net,
            lease_liabilities=eb.lease_liabilities,
            equity_value=equity_value,
            shares_outstanding=eb.shares_outstanding,
            value_per_share=value_per_share,
            value_per_share_reported=value_per_share_reported,
            terminal_share_of_ev=terminal_share,
            market_reference_price=eb.market_reference_price,
            discount_to_market=discount_to_market,
            warnings=warnings,
            notes=notes,
        )

    def per_year_derivation(self, result: "FcfDcfResult"):
        """The per-year operating build as an auditable Derivation (parity item, §11).

        One step per period for revenue, EBIT and FCFF, so the year-by-year build reads
        out of the engine's own output (``.as_rows()`` for a workings view). Headline =
        the final year's FCFF.
        """
        from vcc_valuations.derivation import DerivationBuilder

        b = DerivationBuilder(f"per_year_build[{result.scenario_id}]")
        for i, lab in enumerate(result.period_labels):
            b.step(f"{lab}_rev", f"{lab} revenue", result.revenue[i],
                   "base-year revenue grown at the chain rate (stub is a part-year)", {}, units="AUD m")
            b.step(f"{lab}_ebit", f"{lab} EBIT", result.ebit[i],
                   "revenue x EBIT margin (base + transformation - gas roll-off)",
                   {"margin": result.ebit_margin[i]}, units="AUD m")
            b.step(f"{lab}_fcff", f"{lab} FCFF", result.fcff[i],
                   "NOPAT + D&A - capex - dWC", {}, units="AUD m")
        return b.build(result_key=f"{result.period_labels[-1]}_fcff")
