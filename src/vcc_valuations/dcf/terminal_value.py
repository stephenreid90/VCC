"""Two-stage excess-return terminal value (D-62 to D-66).

Promoted out of ``scripts/size_terminal_options.py`` per standing rule 4 and D-51:
this is production logic now, not a one-off sizing exercise, so it lives in
``src/`` and the script imports it rather than defining its own copy.

The two-stage form, with C the capital at the end of the forecast (invested
capital for FCFF, book equity for the bank), R the return earned on it, r the
discount rate, g nominal growth and N the years the excess return runs beyond
the forecast:

    TV(N) = C * [ m * (1 - k**N) + k**N ],   m = (R - g) / (r - g),   k = (1 + g) / (1 + r)

m is the justified price-to-capital of a perpetual excess return; k**N is the
weight left on plain capital once the moat has expired. N = 0 gives TV = C
(convergence at the end of the forecast); N -> infinity gives C * m (Gordon on
the earned return).

``two_stage_disclosure`` is build order item 3: it discloses, alongside each
engine's own headline terminal, what the two-stage form would show for a
company x scenario that has a declared moat length (D-63's
``ExcessReturnDefence.decay_horizon``). It does not move a golden or replace a
headline terminal value -- at this build only DNL carries any declared decay
horizon, so the other fifteen of eighteen valuations disclose "not available"
rather than a moat length nobody chose. Assigning the rest is a later,
dedicated pass.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from vcc_valuations.schemas.linkage import DecayHorizon


# ------------------------------------------------------------------ the maths
def perpetual_multiple(ret: float, r: float, g: float) -> float:
    """Justified price-to-capital of an excess return held forever."""
    return (ret - g) / (r - g)


def two_stage(capital: float, ret: float, r: float, g: float, n: float) -> float:
    """Terminal value when the return R runs n years beyond the forecast, then fades to r.

    Holds capital and sets next-year earnings = capital x R (D-64): a higher return
    therefore always means a higher value, which is the direction a user expects of
    the lever.
    """
    if n <= 0:
        return capital
    if math.isinf(n):
        return capital * perpetual_multiple(ret, r, g)
    k = (1.0 + g) / (1.0 + r)
    return capital * (perpetual_multiple(ret, r, g) * (1.0 - k ** n) + k ** n)


@dataclass(frozen=True)
class ImpliedMoat:
    # "finite"            the TV sits between convergence and the perpetual earned return
    # "perpetual_or_more" the TV holds the earned return forever, or moves further still
    # "other_side"        the TV sits on the far side of capital from where the earned
    #                     return points: a recovery above, or a fall below, the cost of
    #                     capital that the forecast itself does not show
    # "no_excess"         the earned return equals the cost of capital; moat is moot
    status: str
    extension_years: Optional[float]  # years beyond the forecast; None unless finite


_TOL = 1e-9


def implied_moat(tv: float, capital: float, ret: float, r: float, g: float) -> ImpliedMoat:
    """Invert the two-stage form: how long must R run to reproduce this TV?"""
    m = perpetual_multiple(ret, r, g)
    x = tv / capital
    if abs(m - 1.0) < _TOL:
        return ImpliedMoat("no_excess", None)
    # Position of the TV on the line from convergence (0) to perpetual (1).
    position = (x - 1.0) / (m - 1.0)
    if position >= 1.0 - _TOL:
        return ImpliedMoat("perpetual_or_more", None)
    if position < -_TOL:
        return ImpliedMoat("other_side", None)
    if position <= _TOL:
        return ImpliedMoat("finite", 0.0)
    k = (1.0 + g) / (1.0 + r)
    return ImpliedMoat("finite", math.log(1.0 - position) / math.log(k))


def implied_perpetual_return(tv: float, capital: float, r: float, g: float) -> float:
    """The single return on all capital, held forever, that reproduces this TV.

    Inverts TV = C x (R - g) / (r - g). Equal to r exactly when TV = C.
    """
    return g + (tv / capital) * (r - g)


def return_on_new_capital(cash_flow_1: float, earnings_1: float, g: float) -> Optional[float]:
    """Growth identity g = return x reinvestment, solved for the return."""
    reinvestment = 1.0 - cash_flow_1 / earnings_1
    if reinvestment <= 0:
        return None
    return g / reinvestment


# ------------------------------------------------------- moat length (D-63)
def moat_years_from_decay_horizon(horizon: Optional[DecayHorizon]) -> Optional[float]:
    """Years the excess return runs beyond the forecast, D-63's midpoint default.

    None where no decay horizon is declared for this company x scenario -- the
    common case at the September 2026 build. ``math.inf`` where the horizon is
    declared indefinite. Otherwise the band's midpoint: D-63 ratified the
    midpoint as the default single-number disclosure, with the band ends shown
    separately as a sensitivity rather than the midpoint standing as the only
    number offered.
    """
    if horizon is None:
        return None
    if horizon.indefinite:
        return math.inf
    return (horizon.years_low + horizon.years_high) / 2.0


# --------------------------------------------------------- engine facts (D-51)
def engine_facts(root: Path, company_id: str, archetype_id: str, scenario_id: str) -> Dict:
    """Year-T figures in one shape across the three engines.

    Shared by the sizing script and ``two_stage_disclosure`` so neither
    reimplements an engine call (D-51): this is the one place that runs
    ``FcfEngine`` / ``BankEngine`` / ``SegmentEngine`` and reads their year-T
    output for the terminal-value work.
    """
    from vcc_valuations.dcf import terminal_return as tr
    from vcc_valuations.dcf.bank_engine import BankEngine
    from vcc_valuations.dcf.fcf_engine import FcfEngine
    from vcc_valuations.dcf.segment_engine import SegmentEngine
    from vcc_valuations.translator import (
        build_bank_inputs_from_data, build_engine_inputs_from_data,
        build_segment_inputs_from_data, csl_terminal_invested_capital, load_inputs,
    )

    inputs = load_inputs(root, scenario_id, archetype_id, company_id)
    if company_id == "wbc":
        bi = build_bank_inputs_from_data(inputs, scenario_id)
        res = BankEngine().run(bi)
        t = tr.from_bank(res, bi)
        return dict(
            t=t, construction="bank_roe", horizon=len(res.period_labels) - 1,
            earnings_T=res.cash_npat[-1], cash_flow_T=res.dividends[-1],
            ebit_T=None, ebitda_T=None, capital=res.closing_book_equity,
            tv=res.terminal_value, tdf=res.terminal_discount_factor,
            value_total=res.total_equity_claim, vps=res.value_per_share,
            shares=res.shares_outstanding_m, per_share_scale=1.0,
            inputs=inputs,
        )
    if company_id == "csl":
        si = build_segment_inputs_from_data(inputs, scenario_id)
        res = SegmentEngine().run(si)
        t = tr.from_segment(res, si, company_id=company_id, scenario_id=scenario_id)
        return dict(
            t=t, construction="segment_roic", horizon=len(res.fcff) - 1,
            earnings_T=res.nopat[-1], cash_flow_T=res.fcff[-1],
            ebit_T=res.group_ebit[-1], ebitda_T=res.group_ebit[-1] + res.da[-1],
            capital=csl_terminal_invested_capital(inputs, scenario_id),  # D-44/D-62 item 2
            tv=res.terminal_value, tdf=res.terminal_discount_factor,
            value_total=res.enterprise_value, vps=res.value_per_share_aud,
            shares=res.shares_outstanding_m,
            per_share_scale=res.value_per_share_aud / res.value_per_share_usd,
            inputs=inputs,
        )
    ei = build_engine_inputs_from_data(inputs, scenario_id)
    res = FcfEngine().run(ei)
    t = tr.from_fcff(res, company_id=company_id, scenario_id=scenario_id,
                     declared_return=ei.declared_terminal_return)
    return dict(
        t=t, construction="fcff_roic", horizon=res.horizon_years,
        earnings_T=res.nopat[-1], cash_flow_T=res.fcff[-1],
        ebit_T=res.ebit[-1], ebitda_T=res.ebit[-1] + res.da[-1],
        capital=res.terminal_invested_capital,
        tv=res.terminal_value, tdf=res.terminal_discount_factor,
        value_total=res.enterprise_value, vps=res.value_per_share,
        shares=res.shares_outstanding, per_share_scale=1.0,
        market_price=res.market_reference_price,
        reported_per_engine=res.value_per_share_reported / res.value_per_share,
        inputs=inputs,
    )


# ------------------------------------------------------ the disclosure itself
@dataclass(frozen=True)
class TwoStageDisclosure:
    """What the two-stage form shows for one company x scenario, or why it can't yet.

    A disclosure, not a valuation: it never replaces the engine's own headline
    ``terminal_value`` / ``value_per_share`` and it moves nothing that a golden
    pins. ``available`` is False wherever the five-forces work has not yet
    declared a moat length for this company x scenario (or the engine path has
    no invested-capital base to hold one against) -- that is the honest state
    for fifteen of eighteen valuations at the September 2026 build, and it is
    reported as absence, not defaulted to a moat length nobody chose.
    """

    company_id: str
    scenario_id: str
    available: bool
    reason: Optional[str] = None
    cost_of_capital: Optional[float] = None
    terminal_growth: Optional[float] = None
    capital: Optional[float] = None
    earned_return: Optional[float] = None
    moat_years: Optional[float] = None
    moat_band: Optional[str] = None
    moat_basis: Optional[str] = None
    terminal_value: Optional[float] = None
    value_per_share: Optional[float] = None
    engine_terminal_value: Optional[float] = None
    engine_value_per_share: Optional[float] = None


def two_stage_disclosure(root: Path, company_id: str, archetype_id: str,
                          scenario_id: str) -> TwoStageDisclosure:
    """Build order item 3: the two-stage terminal, disclosed alongside the engine's own.

    Reads the moat length the five-forces work has declared for this company x
    scenario (D-63's ``ExcessReturnDefence.decay_horizon``, via the impact
    matrix) and, only where one is declared, computes what the two-stage form
    would show. Where none is declared, or the engine path has no
    invested-capital base (D-44), the disclosure says so rather than assuming a
    value.
    """
    from vcc_valuations.translator import decay_horizon_from_matrix

    f = engine_facts(root, company_id, archetype_id, scenario_id)
    t = f["t"]
    r, g = t.cost_of_capital, t.terminal_growth
    capital = f["capital"]

    if capital is None:
        return TwoStageDisclosure(
            company_id, scenario_id, available=False,
            reason="no invested-capital base for this engine path (D-44)",
            cost_of_capital=r, terminal_growth=g,
            engine_terminal_value=f["tv"], engine_value_per_share=f["vps"],
        )

    e1 = f["earnings_T"] * (1.0 + g)
    earned = e1 / capital

    horizon = decay_horizon_from_matrix(f["inputs"], scenario_id)
    moat_years = moat_years_from_decay_horizon(horizon)
    if moat_years is None:
        return TwoStageDisclosure(
            company_id, scenario_id, available=False,
            reason="no decay_horizon declared for this company x scenario yet "
                   "(five-forces moat-length assignment pending)",
            cost_of_capital=r, terminal_growth=g, capital=capital, earned_return=earned,
            engine_terminal_value=f["tv"], engine_value_per_share=f["vps"],
        )

    tv = two_stage(capital, earned, r, g, moat_years)
    if math.isinf(moat_years):
        band = "indefinite"
    else:
        band = f"{horizon.years_low}-{horizon.years_high}"
    delta_pv = (tv - f["tv"]) * f["tdf"]
    vps = f["vps"] + delta_pv / f["shares"] * f["per_share_scale"]

    return TwoStageDisclosure(
        company_id, scenario_id, available=True,
        cost_of_capital=r, terminal_growth=g, capital=capital, earned_return=earned,
        moat_years=moat_years, moat_band=band, moat_basis=horizon.basis,
        terminal_value=tv, value_per_share=vps,
        engine_terminal_value=f["tv"], engine_value_per_share=f["vps"],
    )
