"""Bank valuation engine — residual-income / dividend-discount on equity (methodology §15).

Banks are not valued by FCFF/WACC: there is no enterprise-value-to-equity bridge and no
single blended WACC. Instead (methodology §15):

  * Net interest income = average interest-earning assets (AIEA) x net interest margin (NIM),
    accrued over the period length; plus non-interest income.
  * Operating expenses via a cost-to-income ratio; credit impairment as a scenario driver
    (loss rate x average loans, where loans are a share of AIEA).
  * Cash NPAT after tax; dividends = NPAT x payout.
  * Discount the dividend stream at the cost of equity Ke (no WACC).
  * Terminal value by the justified price-to-book / ROE-fade form: closing book equity x
    (terminal ROE - g) / (Ke - g), discounted at the horizon end.
  * Equity-side deductions (AT1 hybrids, non-controlling interests, treasury shares) give
    the ordinary-equity claim; divide by shares for value per share.

The engine is single-entity (whole-bank). Inputs carry ZERO derived values; every derived
quantity is computed here and (via ``derivation()``) exposed as an auditable trace, mirroring
the industrial ``FcfEngine`` / ``Derivation`` pattern.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from vcc_valuations.derivation import DerivationBuilder
from vcc_valuations.dcf.bank_capital import Cet1Trajectory, project_cet1
from vcc_valuations.dcf.fcf_engine import terminal_share_warning


@dataclass
class BankInputs:
    company_id: str
    scenario_id: str
    # timing
    stub_years: float
    horizon_years: int
    aiea_y1_time_factor: float
    # balance-sheet & income anchors (AUD m)
    aiea_anchor: float
    book_equity: float
    at1_hybrid: float
    non_controlling_interests: float
    treasury_shares: float
    shares_outstanding_m: float
    non_interest_income_1h: float          # half-year anchor
    # forecast drivers
    aiea_growth: float                     # derived industry+offset(+scenario), passed in
    non_interest_income_growth: float
    avg_loans_pct_aiea: float
    effective_tax_rate: float
    dividend_payout_ratio: float
    # per-period glides (length = horizon+1; index 0 = stub)
    nim_applied: List[float]
    cost_to_income: List[float]
    credit_loss_rate: List[float]
    # discount rate & terminal
    cost_of_equity: float
    terminal_roe: float
    terminal_growth: float
    # §15.5 capital diagnostic (open item 8). Optional, and warn-only: supply all
    # four and the engine projects the CET1 path and warns; omit any and it is
    # skipped. Optional rather than required so that the diagnostic can never be
    # the reason a scenario fails to build -- a check that breaks the valuation it
    # is checking is worse than no check.
    cet1_anchor_ratio: Optional[float] = None
    rwa_anchor: Optional[float] = None
    rwa_density: Optional[float] = None
    cet1_floor: Optional[float] = None
    cet1_operating_target: Optional[float] = None
    # D-60, ON. The payout is cut by just enough to hold CET1 at the operating
    # target once the ratio reaches it. It raises the valuation, and that is
    # correct rather than an artefact: the justified price-to-book terminal is
    # derived from g = ROE x b, so the terminal stream IS the dividend the
    # retained equity supports, growing at the rate retention funds. A lower
    # dividend now is traded for a higher one later and the form already says so.
    # Switchable because the audited v4 workbook has no capital constraint, so the
    # independent tie is struck on the unconstrained path (tests/dcf/test_wbc_bank).
    constrain_payout_to_capital: bool = True


@dataclass
class BankResult:
    company_id: str
    scenario_id: str
    period_labels: List[str]
    period_length: List[float]
    aiea: List[float]
    nim: List[float]
    nii: List[float]
    non_interest_income: List[float]
    total_operating_income: List[float]
    operating_expenses: List[float]        # negative
    pre_provision_profit: List[float]
    credit_impairment: List[float]         # negative
    pre_tax_profit: List[float]
    tax: List[float]                       # negative
    cash_npat: List[float]
    dividends: List[float]
    mid_times: List[float]
    discount_factors: List[float]
    pv_dividends: List[float]
    cost_of_equity: float
    pv_explicit_dividends: float
    opening_book_equity: float
    retained_earnings: float
    closing_book_equity: float
    terminal_value: float
    terminal_discount_factor: float
    pv_terminal_value: float
    total_equity_claim: float
    at1_hybrid: float
    non_controlling_interests: float
    treasury_shares: float
    ordinary_equity_value: float
    shares_outstanding_m: float
    value_per_share: float
    # §11.4.2 diagnostics. The bank terminal is a share of the *equity claim*
    # (PV dividends + PV terminal), there being no EV bridge in the §15 fork.
    terminal_share_of_claim: float = 0.0
    warnings: List[str] = field(default_factory=list)
    # Per-period equity roll-forward. The engine has always computed retained
    # earnings as one lump over the horizon, which is all the terminal value
    # needs; the capital diagnostic needs the year-by-year path. It sums to the
    # same closing figure by construction -- see the invariant asserted in
    # tests/test_bank_capital.py -- because equity does not feed NPAT in the §15
    # build, so exposing it moves nothing.
    retained_by_period: List[float] = field(default_factory=list)
    book_equity_path: List[float] = field(default_factory=list)
    rwa_by_period: List[float] = field(default_factory=list)
    cet1_trajectory: Optional[Cet1Trajectory] = None
    # D-60 disclosure. payout_applied is the payout the engine actually paid in
    # each period; it equals the stated ratio until the capital constraint binds.
    # dividends_forgone is what the constraint withheld, which is the whole of the
    # difference between this valuation and the unconstrained one, and belongs on
    # screen rather than inferred from a level that moved.
    payout_applied: List[float] = field(default_factory=list)
    capital_constraint_binds_from: Optional[str] = None
    dividends_forgone: float = 0.0


class BankEngine:
    """``run(BankInputs) -> BankResult``. Residual-income / DDM on equity (§15)."""

    def run(self, inp: BankInputs) -> BankResult:
        H = inp.horizon_years
        n = H + 1
        labels = ["Stub"] + [f"Y{k}" for k in range(1, H + 1)]
        period_length = [inp.stub_years] + [1.0] * H

        # AIEA: anchor x (1 + g x time_factor); stub factor = stub/2, Y1 given, Y2+ compound.
        aiea: List[float] = [0.0] * n
        aiea[0] = inp.aiea_anchor * (1.0 + inp.aiea_growth * (inp.stub_years / 2.0))
        if H >= 1:
            aiea[1] = inp.aiea_anchor * (1.0 + inp.aiea_growth * inp.aiea_y1_time_factor)
        for p in range(2, n):
            aiea[p] = aiea[p - 1] * (1.0 + inp.aiea_growth)

        nim = list(inp.nim_applied)
        nii = [aiea[p] * nim[p] * period_length[p] for p in range(n)]

        non_int = [0.0] * n
        non_int[0] = inp.non_interest_income_1h * (inp.stub_years * 2.0)  # half-year -> stub
        if H >= 1:
            non_int[1] = 2.0 * inp.non_interest_income_1h * (1.0 + inp.non_interest_income_growth)
        for p in range(2, n):
            non_int[p] = non_int[p - 1] * (1.0 + inp.non_interest_income_growth)

        toi = [nii[p] + non_int[p] for p in range(n)]
        opex = [-toi[p] * inp.cost_to_income[p] for p in range(n)]
        pre_prov = [toi[p] + opex[p] for p in range(n)]
        loans = [aiea[p] * inp.avg_loans_pct_aiea for p in range(n)]
        impair = [-loans[p] * inp.credit_loss_rate[p] * period_length[p] for p in range(n)]
        pre_tax = [pre_prov[p] + impair[p] for p in range(n)]
        tax = [-pre_tax[p] * inp.effective_tax_rate for p in range(n)]
        npat = [pre_tax[p] + tax[p] for p in range(n)]

        # --- dividends, subject to the §15.5 capital constraint (D-60)
        #
        # The ratio is allowed to drift down; once it reaches the operating
        # target the payout is cut by just enough to hold it there, and never
        # raised above the stated payout when the ratio is comfortably above.
        # One-sided by construction: when the required retention is negative the
        # stated payout simply wins, so a bank running above its target does not
        # mechanically distribute the surplus. Distributing it is a capital-action
        # decision (buyback, special dividend) with its own timing, not an
        # arithmetic consequence of being above target.
        #
        # Path-dependent, so it cannot be computed after the fact: each period's
        # opening equity and opening ratio depend on every cut before it.
        rwa_by_period: List[float] = []
        if inp.rwa_density is not None:
            rwa_by_period = [aiea[p] * inp.rwa_density for p in range(n)]

        constrained = (
            inp.constrain_payout_to_capital
            and inp.cet1_anchor_ratio is not None
            and inp.rwa_anchor is not None
            and inp.cet1_operating_target is not None
            and bool(rwa_by_period)
        )

        dividends: List[float] = []
        payout_applied: List[float] = []
        binds_from: Optional[str] = None
        forgone = 0.0

        if constrained:
            _eq = inp.book_equity
            _ratio = inp.cet1_anchor_ratio
            _prev_rwa = inp.rwa_anchor
            _target = inp.cet1_operating_target
            for p in range(n):
                rwa_growth = (rwa_by_period[p] / _prev_rwa) - 1.0
                # Retention that lands the closing ratio exactly on the target.
                required = _eq * (_target * (1.0 + rwa_growth) / _ratio - 1.0)
                stated = npat[p] * inp.dividend_payout_ratio
                div = min(stated, npat[p] - required)
                if div < 0.0:
                    # A bank cannot pay a negative dividend. The shortfall is a
                    # capital-raising question, not a distribution one, and the
                    # ratio is allowed to fall through the target here rather
                    # than the engine inventing equity issuance.
                    div = 0.0
                if div < stated - 1e-9:
                    forgone += stated - div
                    if binds_from is None:
                        binds_from = labels[p]
                dividends.append(div)
                payout_applied.append(div / npat[p] if npat[p] else 0.0)
                _retained = npat[p] - div
                _ratio = _ratio * (1.0 + _retained / _eq) / (1.0 + rwa_growth)
                _eq += _retained
                _prev_rwa = rwa_by_period[p]
        else:
            dividends = [npat[p] * inp.dividend_payout_ratio for p in range(n)]
            payout_applied = [inp.dividend_payout_ratio] * n

        ke = inp.cost_of_equity
        mid_times = [inp.stub_years / 2.0] + [inp.stub_years + (k - 0.5) for k in range(1, H + 1)]  # ssot-allow: structural mid-period offset
        dfs = [1.0 / (1.0 + ke) ** t for t in mid_times]
        pv_div = [dividends[p] * dfs[p] for p in range(n)]
        pv_explicit = sum(pv_div)

        retained_by_period = [npat[p] - dividends[p] for p in range(n)]
        book_equity_path: List[float] = []
        _eq = inp.book_equity
        for r in retained_by_period:
            _eq += r
            book_equity_path.append(_eq)
        retained = sum(npat) - sum(dividends)
        closing_equity = inp.book_equity + retained
        g = inp.terminal_growth
        tv = closing_equity * (inp.terminal_roe - g) / (ke - g)
        terminal_end = inp.stub_years + H
        tdf = 1.0 / (1.0 + ke) ** terminal_end
        pv_terminal = tv * tdf

        total_claim = pv_explicit + pv_terminal
        ordinary = total_claim - inp.at1_hybrid - inp.non_controlling_interests - inp.treasury_shares
        vps = ordinary / inp.shares_outstanding_m

        terminal_share = pv_terminal / total_claim if total_claim else 0.0
        warnings: List[str] = []
        tv_warning = terminal_share_warning(terminal_share, "the equity claim")
        if tv_warning:
            warnings.append(tv_warning)

        # D-42: surface the terminal return against the cost of capital on
        # every valuation. Non-blocking (D-07): it warns and obliges, it never
        # adjusts. The obligation itself is the ratchet in
        # tests/dcf/test_terminal_defence.py.
        from vcc_valuations.dcf.terminal_return import from_bank_parts
        warnings.extend(from_bank_parts(
            company_id=inp.company_id, scenario_id=inp.scenario_id,
            closing_book_equity=closing_equity, final_npat=npat[-1],
            terminal_roe=inp.terminal_roe, terminal_growth=g,
            cost_of_equity=ke,
        ).warnings)

        # §15.5 capital trajectory. Still reported even when the constraint is
        # active, because it is then the evidence that the rule did its job: the
        # ratio should sit exactly on the target from the binding period onward.
        trajectory: Optional[Cet1Trajectory] = None
        if (inp.cet1_anchor_ratio is not None and inp.rwa_anchor is not None
                and inp.cet1_floor is not None and inp.cet1_operating_target is not None
                and rwa_by_period):
            trajectory = project_cet1(
                labels=labels,
                opening_book_equity=inp.book_equity,
                retained_by_period=retained_by_period,
                rwa_by_period=rwa_by_period,
                rwa_anchor=inp.rwa_anchor,
                anchor_ratio=inp.cet1_anchor_ratio,
                floor=inp.cet1_floor,
                operating_target=inp.cet1_operating_target,
            )
            warnings.extend(trajectory.warnings)

        return BankResult(
            company_id=inp.company_id, scenario_id=inp.scenario_id,
            period_labels=labels, period_length=period_length,
            aiea=aiea, nim=nim, nii=nii, non_interest_income=non_int,
            total_operating_income=toi, operating_expenses=opex,
            pre_provision_profit=pre_prov, credit_impairment=impair,
            pre_tax_profit=pre_tax, tax=tax, cash_npat=npat, dividends=dividends,
            mid_times=mid_times, discount_factors=dfs, pv_dividends=pv_div,
            cost_of_equity=ke, pv_explicit_dividends=pv_explicit,
            opening_book_equity=inp.book_equity, retained_earnings=retained,
            closing_book_equity=closing_equity, terminal_value=tv,
            terminal_discount_factor=tdf, pv_terminal_value=pv_terminal,
            total_equity_claim=total_claim, at1_hybrid=inp.at1_hybrid,
            non_controlling_interests=inp.non_controlling_interests,
            treasury_shares=inp.treasury_shares, ordinary_equity_value=ordinary,
            shares_outstanding_m=inp.shares_outstanding_m, value_per_share=vps,
            terminal_share_of_claim=terminal_share, warnings=warnings,
            retained_by_period=retained_by_period, book_equity_path=book_equity_path,
            rwa_by_period=rwa_by_period, cet1_trajectory=trajectory,
            payout_applied=payout_applied,
            capital_constraint_binds_from=binds_from,
            dividends_forgone=forgone,
        )

    def per_year_derivation(self, result: BankResult):
        """The per-year operating build as an auditable Derivation (parity item, §11).

        One step per period for the income, earnings and dividend lines, so the whole
        year-by-year build reads out of the engine's own output (``.as_rows()`` for a
        workings view). Headline = the final year's dividend.
        """
        b = DerivationBuilder(f"per_year_build[{result.scenario_id}]")
        n = len(result.period_labels)
        for i in range(n):
            lab = result.period_labels[i]
            b.step(f"{lab}_toi", f"{lab} total operating income", result.total_operating_income[i],
                   "NII (AIEA x NIM x period) + non-interest income",
                   {"aiea": result.aiea[i], "nim": result.nim[i]}, units="AUD m")
            b.step(f"{lab}_npat", f"{lab} cash NPAT", result.cash_npat[i],
                   "(pre-provision profit - impairment) x (1 - tax)", {}, units="AUD m")
            b.step(f"{lab}_div", f"{lab} dividend", result.dividends[i],
                   "NPAT x payout ratio", {}, units="AUD m")
        return b.build(result_key=f"{result.period_labels[-1]}_div")

    def derivation(self, inp: BankInputs, result: BankResult):
        """The §15.7/§15.8 equity bridge as an auditable Derivation (headline = value per share)."""
        b = DerivationBuilder(f"bank_value[{inp.scenario_id}]")
        b.step("pv_div", "PV of explicit dividends", result.pv_explicit_dividends,
               "sum of discounted dividends", {}, units="AUD m")
        b.step("close_eq", "Closing book equity (end Y{})".format(inp.horizon_years),
               result.closing_book_equity, "opening equity + retained earnings",
               {"opening": result.opening_book_equity, "retained": result.retained_earnings},
               units="AUD m")
        b.step("tv", "Terminal value", result.terminal_value,
               "closing_equity * (terminal_ROE - g) / (Ke - g)",
               {"terminal_ROE": inp.terminal_roe, "g": inp.terminal_growth, "Ke": inp.cost_of_equity},
               units="AUD m")
        b.step("pv_tv", "PV of terminal value", result.pv_terminal_value,
               "terminal_value * discount_factor", {"tdf": result.terminal_discount_factor},
               units="AUD m")
        b.step("claim", "Total value of equity claim", result.total_equity_claim,
               "PV dividends + PV terminal", {}, units="AUD m")
        b.step("at1", "Less: AT1 hybrid", -inp.at1_hybrid, "less AT1", {}, units="AUD m")
        b.step("nci", "Less: non-controlling interests", -inp.non_controlling_interests,
               "less NCI", {}, units="AUD m")
        b.step("treas", "Less: treasury shares", -inp.treasury_shares, "less treasury", {},
               units="AUD m")
        b.step("ord", "Ordinary equity value", result.ordinary_equity_value,
               "claim - AT1 - NCI - treasury", {}, units="AUD m")
        b.step("vps", "Value per share", result.value_per_share,
               "ordinary_equity / shares", {"shares_m": inp.shares_outstanding_m}, units="AUD")
        return b.build(result_key="vps")
