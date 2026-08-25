"""A standalone replica of the industrial FCFF build, for structural experiments.

The production engine takes a single scalar revenue growth rate and a fixed
horizon. Several proposed methodology changes -- a longer explicit period, a
linear growth fade, a converging capex path, a terminal struck off a declared
capital base -- cannot be expressed through ``FcfEngineInputs`` without changing
the engine first. Sizing them before deciding whether to change the engine is
what this module is for.

The replica is not a second model of record. It earns its right to be trusted
one way only: :func:`plan_from_engine_inputs` builds a plan that must reproduce
``FcfEngine`` exactly, and ``tests/dcf/test_replica_ties_engine.py`` enforces
that tie to floating-point equality across every live scenario. A structural
variant is then a plan that differs from the tying plan in one declared way, so
the difference in the answer is attributable to the change and to nothing else.

Nothing here is imported by production code, and no company number is written
into this file: every plan is built from an ``FcfEngineInputs`` assembled by the
translator from the data files.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional


@dataclass
class Plan:
    """One explicit-period build, expressed as paths rather than scalars.

    Every field that the engine holds as a scalar and applies to every year --
    revenue growth, and the terminal capex rule -- is a per-year path or a
    declared rate here. Margin is carried as a single cumulative delta path
    rather than the engine's two overlay rows, because the replica never needs
    to display the industry baseline and the company offset separately; the
    workbook does that, and the sum is what reaches cash flow.
    """

    company_id: str
    scenario_id: str
    horizon_years: int
    stub_years: float

    base_year_revenue: float
    growth_path: List[float]          # len H, year-on-year

    base_ebit_margin: float
    margin_delta: List[float]         # len H, cumulative pp vs base

    stub_tax_rate: float
    tax_rate_glide: List[float]       # len H

    da_pct_revenue: float
    capex_pct_stub: float
    capex_pct: List[float]            # len H

    working_capital_intensity: float
    terminal_growth: float
    terminal_capex_pct_revenue: float

    wacc: float

    net_debt_at_valuation: float
    equity_bridge_adjustments_net: float
    lease_liabilities: float
    shares_outstanding: float
    fx_rate: float = 1.0
    market_reference_price: Optional[float] = None

    # Invested capital at the valuation date, on whatever construction the
    # caller has declared. Optional: the cash-flow build does not need it, and
    # only the return diagnostics do.
    invested_capital_opening: Optional[float] = None

    label: str = ""

    def __post_init__(self) -> None:
        H = self.horizon_years
        for name in ("growth_path", "margin_delta", "tax_rate_glide", "capex_pct"):
            vec = getattr(self, name)
            if len(vec) != H:
                raise ValueError(
                    f"{name} must have length horizon_years={H}, got {len(vec)}"
                )


@dataclass
class PlanResult:
    plan: Plan
    period_labels: List[str]
    revenue: List[float]
    ebit_margin: List[float]
    nopat: List[float]
    da: List[float]
    capex: List[float]              # negative
    delta_wc: List[float]           # negative
    fcff: List[float]
    pv_fcff: List[float]
    pv_explicit: float
    terminal_fcff: float
    terminal_value: float
    pv_terminal: float
    enterprise_value: float
    equity_value: float
    value_per_share: float
    value_per_share_reported: float
    terminal_share_of_ev: float
    diagnostics: Dict[str, float] = field(default_factory=dict)


def _run_rate(plan: Plan, t: float) -> float:
    """The annualised revenue run-rate ``t`` years past the base year.

    Whole years compound along the path. A fractional ``t`` -- the stub -- sits
    inside the first forecast year, so it compounds at that year's rate. With a
    flat path this is the engine's ``base * (1 + g) ** t`` for every ``t``.
    """
    whole = int(t)
    rate = plan.base_year_revenue
    # Compound a run of equal rates in one exponentiation rather than year by
    # year. On a flat path that is exactly the engine's ``base * (1 + g) ** k``,
    # bit for bit -- which is what lets the tie be asserted at floating-point
    # equality instead of at a tolerance chosen to hide the difference.
    k = 0
    while k < whole:
        j = k
        while j < whole and plan.growth_path[j] == plan.growth_path[k]:
            j += 1
        rate *= (1.0 + plan.growth_path[k]) ** (j - k)
        k = j
    frac = t - whole
    if frac:
        rate *= (1.0 + plan.growth_path[min(whole, plan.horizon_years - 1)]) ** frac
    return rate


def run(plan: Plan) -> PlanResult:
    """Value one plan. Mirrors ``FcfEngine.run`` line for line."""
    H = plan.horizon_years
    g = plan.terminal_growth
    wacc = plan.wacc
    if g >= wacc:
        raise ValueError(f"terminal growth {g} >= WACC {wacc}; Gordon terminal undefined.")

    revenue = [plan.base_year_revenue * plan.stub_years]
    for k in range(1, H + 1):
        revenue.append(_run_rate(plan, k))

    ebit_margin = [plan.base_ebit_margin]
    ebit_margin += [plan.base_ebit_margin + d for d in plan.margin_delta]
    ebit = [r * m for r, m in zip(revenue, ebit_margin)]

    applied_tax = [plan.stub_tax_rate] + list(plan.tax_rate_glide)
    tax = [-e * t for e, t in zip(ebit, applied_tax)]
    nopat = [e + t for e, t in zip(ebit, tax)]

    da = [r * plan.da_pct_revenue for r in revenue]
    capex_pct_all = [plan.capex_pct_stub] + list(plan.capex_pct)
    capex = [-r * c for r, c in zip(revenue, capex_pct_all)]

    wc = plan.working_capital_intensity
    dwc_stub = wc * (_run_rate(plan, plan.stub_years) - plan.base_year_revenue)
    dwc = [wc * (revenue[1] - _run_rate(plan, plan.stub_years))]
    dwc += [wc * (revenue[k] - revenue[k - 1]) for k in range(2, H + 1)]
    delta_wc = [-dwc_stub] + [-w for w in dwc]

    fcff = [n + d + c + w for n, d, c, w in zip(nopat, da, capex, delta_wc)]

    mid_times = [plan.stub_years / 2.0] + [plan.stub_years + k - 0.5 for k in range(1, H + 1)]
    dfs = [1.0 / (1.0 + wacc) ** t for t in mid_times]
    pv_fcff = [f * d for f, d in zip(fcff, dfs)]
    pv_explicit = sum(pv_fcff)

    terminal_fcff = revenue[-1] * (1.0 + g) * (
        ebit_margin[-1] * (1.0 - applied_tax[-1])
        + plan.da_pct_revenue
        - plan.terminal_capex_pct_revenue
        - g * wc
    )
    terminal_value = terminal_fcff / (wacc - g)
    terminal_end_time = plan.stub_years + H
    pv_terminal = terminal_value / (1.0 + wacc) ** terminal_end_time

    ev = pv_explicit + pv_terminal
    equity_value = (
        ev
        - plan.net_debt_at_valuation
        - plan.equity_bridge_adjustments_net
        - plan.lease_liabilities
    )
    vps = equity_value / plan.shares_outstanding

    return PlanResult(
        plan=plan,
        period_labels=["Stub"] + [f"Y{k}" for k in range(1, H + 1)],
        revenue=revenue,
        ebit_margin=ebit_margin,
        nopat=nopat,
        da=da,
        capex=capex,
        delta_wc=delta_wc,
        fcff=fcff,
        pv_fcff=pv_fcff,
        pv_explicit=pv_explicit,
        terminal_fcff=terminal_fcff,
        terminal_value=terminal_value,
        pv_terminal=pv_terminal,
        enterprise_value=ev,
        equity_value=equity_value,
        value_per_share=vps,
        value_per_share_reported=vps * plan.fx_rate,
        terminal_share_of_ev=pv_terminal / ev if ev else 0.0,
        diagnostics=_diagnostics(plan, revenue, ebit_margin, applied_tax, nopat, da, capex, delta_wc),
    )


def _diagnostics(plan, revenue, ebit_margin, applied_tax, nopat, da, capex, delta_wc) -> Dict[str, float]:
    """Terminal return, on both constructions, plus the capital roll-forward.

    Two readings of the same question, deliberately reported side by side.

    ``terminal_roic_implied`` inverts the growth identity: a perpetuity growing
    at ``g`` while reinvesting a fraction ``b`` of NOPAT is earning ``g / b`` on
    what it puts back. It needs no balance sheet, which is why it can be
    computed for any scenario today, and it says what the cash flows assert
    about the return on *new* capital.

    ``terminal_roic_on_capital`` divides terminal NOPAT by invested capital
    rolled forward from the valuation date through the explicit period. It needs
    a declared opening capital base and says what the build asserts about the
    return on the *whole* base. Where the two disagree the explicit period has
    moved capital intensity, and by how much.
    """
    g = plan.terminal_growth
    wc = plan.working_capital_intensity
    rev_T = revenue[-1] * (1.0 + g)
    nopat_T = rev_T * ebit_margin[-1] * (1.0 - applied_tax[-1])
    net_capex_T = rev_T * (plan.terminal_capex_pct_revenue - plan.da_pct_revenue)
    dwc_T = rev_T * g * wc
    reinvestment_T = net_capex_T + dwc_T

    out = {
        "terminal_revenue": rev_T,
        "terminal_nopat": nopat_T,
        "terminal_reinvestment": reinvestment_T,
        "terminal_reinvestment_rate": reinvestment_T / nopat_T if nopat_T else float("nan"),
        "terminal_nopat_margin": nopat_T / rev_T if rev_T else float("nan"),
    }
    out["terminal_roic_implied"] = (
        g / out["terminal_reinvestment_rate"]
        if out["terminal_reinvestment_rate"]
        else float("inf")
    )

    if plan.invested_capital_opening is not None:
        # Roll the base forward on the same flows the valuation uses: net capex
        # adds, depreciation removes, working capital moves with the run-rate.
        ic = plan.invested_capital_opening
        for i in range(len(revenue)):
            ic += -capex[i] - da[i] - delta_wc[i]
        out["invested_capital_final_explicit"] = ic
        out["invested_capital_over_revenue_final"] = ic / revenue[-1] if revenue[-1] else float("nan")
        out["terminal_roic_on_capital"] = nopat_T / ic if ic else float("nan")
        out["opening_roic"] = (
            revenue[0] / plan.stub_years * plan.base_ebit_margin * (1.0 - applied_tax[0])
            / plan.invested_capital_opening
        )
    return out


def plan_from_engine_inputs(inp, *, invested_capital_opening: Optional[float] = None,
                            label: str = "engine") -> Plan:
    """The plan that reproduces ``FcfEngine`` exactly for a given input.

    Only ``terminal_reinvestment='normalised'`` is replicated. The other mode
    capitalises the final explicit FCFF, which D-32 declared and D-13 took DNL
    off; reproducing a treatment nothing live uses would invite variants to be
    built on it.
    """
    if inp.terminal_reinvestment != "normalised":
        raise ValueError(
            "the replica covers the normalised terminal only; "
            f"got {inp.terminal_reinvestment!r}"
        )
    H = inp.horizon_years
    return Plan(
        company_id=inp.company_id,
        scenario_id=inp.scenario_id,
        horizon_years=H,
        stub_years=inp.stub_years,
        base_year_revenue=inp.base_year_revenue,
        growth_path=[inp.revenue_growth] * H,
        base_ebit_margin=inp.base_ebit_margin,
        margin_delta=[
            inp.margin_transformation[k] + inp.margin_gas_rolloff[k] for k in range(H)
        ],
        stub_tax_rate=inp.stub_tax_rate,
        tax_rate_glide=list(inp.tax_rate_glide),
        da_pct_revenue=inp.da_pct_revenue,
        capex_pct_stub=inp.capex_pct_stub,
        capex_pct=list(inp.capex_pct),
        working_capital_intensity=inp.working_capital_intensity,
        terminal_growth=inp.terminal_growth,
        terminal_capex_pct_revenue=inp.terminal_capex_pct_revenue,
        wacc=inp.wacc_scalar,
        net_debt_at_valuation=inp.equity_bridge.net_debt_at_valuation,
        equity_bridge_adjustments_net=inp.equity_bridge.equity_bridge_adjustments_net,
        lease_liabilities=inp.equity_bridge.lease_liabilities,
        shares_outstanding=inp.equity_bridge.shares_outstanding,
        fx_rate=inp.equity_bridge.fx_rate,
        market_reference_price=inp.equity_bridge.market_reference_price,
        invested_capital_opening=invested_capital_opening,
        label=label,
    )


# --------------------------------------------------------------------------
# Structural variants. Each takes a plan and returns a new one differing in
# exactly one declared way, so a table of variants reads as a decomposition.
# --------------------------------------------------------------------------


def extend(plan: Plan, horizon_years: int) -> Plan:
    """Lengthen the explicit period, holding every path flat past its last year."""
    if horizon_years < plan.horizon_years:
        raise ValueError("extend lengthens the horizon; it does not truncate it.")
    add = horizon_years - plan.horizon_years

    def _hold(vec: List[float]) -> List[float]:
        return list(vec) + [vec[-1]] * add

    return replace(
        plan,
        horizon_years=horizon_years,
        growth_path=_hold(plan.growth_path),
        margin_delta=_hold(plan.margin_delta),
        tax_rate_glide=_hold(plan.tax_rate_glide),
        capex_pct=_hold(plan.capex_pct),
        label=f"{plan.label}+H{horizon_years}",
    )


def fade_growth(plan: Plan, fade_period_length: int) -> Plan:
    """Hold the chain rate, then glide linearly to g, landing on g in the last year.

    D-36. The fade segment is the final ``fade_period_length`` years; the
    forecast segment ahead of it keeps the chain-derived rate.
    """
    H = plan.horizon_years
    if not 1 <= fade_period_length <= H:
        raise ValueError("fade_period_length must lie between 1 and the horizon.")
    chain = plan.growth_path[0]
    g = plan.terminal_growth
    hold = H - fade_period_length
    path = list(plan.growth_path[:hold]) if hold else []
    for i in range(1, fade_period_length + 1):
        path.append(chain + (g - chain) * i / fade_period_length)
    return replace(plan, growth_path=path, label=f"{plan.label}+fade{fade_period_length}")


def converge_capex(plan: Plan, steady_state_pct: float, converge_by_year: int) -> Plan:
    """Glide the capex path linearly to a declared steady-state rate (D-38)."""
    H = plan.horizon_years
    if not 1 <= converge_by_year <= H:
        raise ValueError("converge_by_year must lie between 1 and the horizon.")
    start = plan.capex_pct[0]
    path = [
        start + (steady_state_pct - start) * min(k, converge_by_year) / converge_by_year
        for k in range(1, H + 1)
    ]
    return replace(plan, capex_pct=path, label=f"{plan.label}+capex")


def reshape_margin(plan: Plan, total_delta_pp: float, cumulative_fractions: List[float],
                   keep: Optional[List[float]] = None) -> Plan:
    """Re-phase a cumulative margin overlay without changing its total (D-40).

    ``keep`` is any other overlay that should ride alongside unchanged -- for
    DNL, the transformation row, which the roll-off is added to.
    """
    H = plan.horizon_years
    fr = list(cumulative_fractions)
    fr += [fr[-1]] * (H - len(fr))
    base = keep if keep is not None else [0.0] * H
    return replace(
        plan,
        margin_delta=[base[k] + total_delta_pp * fr[k] for k in range(H)],
        label=f"{plan.label}+rolloff",
    )


def capex_arc(plan: Plan, baseline_capex: List[float], peak_pp: float, hold_to_year: int,
              decay_to_year: int, persistent_pp: float) -> Plan:
    """A scenario capex shift that decays to a persistent level (D-41)."""
    H = plan.horizon_years
    base = list(baseline_capex) + [baseline_capex[-1]] * (H - len(baseline_capex))
    path = []
    for k in range(1, H + 1):
        if k <= hold_to_year:
            shift = peak_pp
        elif k >= decay_to_year:
            shift = persistent_pp
        else:
            span = decay_to_year - hold_to_year
            shift = peak_pp + (persistent_pp - peak_pp) * (k - hold_to_year) / span
        path.append(base[k - 1] + shift)
    return replace(plan, capex_pct=path, label=f"{plan.label}+arc")


def terminal_capex_from_final_year(plan: Plan) -> Plan:
    """D-39: the terminal inherits the final explicit year's capex rate."""
    return replace(
        plan,
        terminal_capex_pct_revenue=plan.capex_pct[-1],
        label=f"{plan.label}+tcapex:final",
    )


def terminal_capex_growing_capital_base(plan: Plan) -> Plan:
    """Set terminal capex so the fixed-capital base compounds at g.

    The steady state a growing perpetuity requires: assets ``A``, depreciation
    ``dA`` and capex ``(d + g)A``, all compounding at ``g``. Working capital is
    handled separately in the terminal formula at ``g x intensity``, so only the
    fixed base is priced here. The base is the one rolled forward through the
    explicit period, which is why this variant needs a declared opening capital.
    """
    if plan.invested_capital_opening is None:
        raise ValueError(
            "growing the capital base at g needs a declared opening invested capital."
        )
    res = run(replace(plan, label=plan.label))
    ic_final = res.diagnostics["invested_capital_final_explicit"]
    wc_stock = plan.working_capital_intensity * res.revenue[-1]
    fixed = ic_final - wc_stock
    rate = plan.da_pct_revenue + plan.terminal_growth * fixed / res.revenue[-1]
    return replace(
        plan,
        terminal_capex_pct_revenue=rate,
        label=f"{plan.label}+tcapex:grow",
    )


def hold_capital_intensity(plan: Plan) -> Plan:
    """Set the explicit capex path so fixed capital keeps pace with revenue.

    The alternative reading of the explicit period: a business whose revenue
    compounds and whose capital intensity is unchanged has to fund the growth in
    its asset base, not merely replace what depreciates. Each year's capex is
    then whatever restores the opening ratio of fixed capital to revenue.

    This is the variant that makes the explicit period and a terminal struck off
    a growing capital base speak the same language. Whether it is right is a
    domain question about the business, not an arithmetic one -- which is why it
    is offered as a variant rather than applied as a correction.
    """
    if plan.invested_capital_opening is None:
        raise ValueError("holding capital intensity needs a declared opening invested capital.")
    fixed_open = (
        plan.invested_capital_opening
        - plan.working_capital_intensity * plan.base_year_revenue
    )
    ratio = fixed_open / plan.base_year_revenue

    # The stub keeps its declared rate; the roll-forward starts from what it leaves.
    stub_revenue = plan.base_year_revenue * plan.stub_years
    fixed = fixed_open + stub_revenue * (plan.capex_pct_stub - plan.da_pct_revenue)

    path = []
    for k in range(1, plan.horizon_years + 1):
        rev = _run_rate(plan, k)
        target = ratio * rev
        capex = target - fixed + rev * plan.da_pct_revenue
        path.append(capex / rev)
        fixed = target
    return replace(plan, capex_pct=path, label=f"{plan.label}+intensity")


def terminal_capex_for_target_roic(plan: Plan, target_roic: float) -> Plan:
    """Set terminal capex so the implied return on new capital equals a target.

    D-45 in its operative form: pin ``g`` and the return, derive the
    reinvestment requirement. ``b = g / ROIC`` fixes reinvestment as a share of
    terminal NOPAT; net capex is what is left after the working-capital call.
    """
    g = plan.terminal_growth
    res = run(plan)
    rev_T = res.diagnostics["terminal_revenue"]
    nopat_T = res.diagnostics["terminal_nopat"]
    reinvestment = nopat_T * g / target_roic
    net_capex = reinvestment - rev_T * g * plan.working_capital_intensity
    return replace(
        plan,
        terminal_capex_pct_revenue=plan.da_pct_revenue + net_capex / rev_T,
        label=f"{plan.label}+tcapex:roic",
    )
