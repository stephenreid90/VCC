"""What the terminal asserts about returns, and whether anything defends it.

D-42 (PROPOSED) and M14. Two questions about the same number, deliberately
answered side by side because they have different benchmarks and different
consequences:

**D-42 — is there a terminal excess return, and is it defended?** The benchmark is
the cost of capital. A perpetuity growing at ``g`` while reinvesting a fraction
``b`` of its earnings is asserting a return of ``g / b`` on what it puts back. Where
that exceeds the discount rate, the valuation is claiming the company reinvests
above its cost of capital forever, and §11.4.2 check 2 requires a §10.6-compliant
defended exception: the moat source, the decay horizon, the threat and a
sensitivity test. Non-blocking, on the D-07 precedent — it warns and obliges, it
never silently adjusts.

**M14 — is the terminal continuous with the model that precedes it?** The benchmark
is the return the explicit period actually earns in its final year. A terminal rate
materially above it is a recovery assumption, and a recovery assumption is a
forecast that ought to be declared as one. This was found on 16 September 2026
while checking whether D-60's retention uplift conjured a return the model had not
already assumed. It mostly does not — the declared rates are conservative — but on
WBC's Stagflation the declared terminal ROE sits four percentage points above what
the final explicit year earns, on the scenario whose terminal is the highest share
of value in the project.

Why this lives here rather than in the replica
----------------------------------------------
Both constructions already existed in ``tests/dcf/harness/replica.py`` and were
used by ``scripts/size_horizon_variants.py``. They are lifted here unchanged in
substance, because D-42 asks for the diagnostic "on every valuation" and a number
that reaches a document has to come from the production path, not from a harness
that reproduces it (standing rule 4, D-51). The replica's own docstring is the
source for the two readings and is worth reading alongside this.

What is NOT computed here, and why
----------------------------------
The replica also reports ``terminal_roic_on_capital`` — terminal NOPAT over
invested capital rolled forward — which says what the build asserts about the
return on the *whole* base rather than on new capital. ``FcfEngine`` carries no
invested-capital roll-forward, so that reading cannot be struck from engine output
today. It is the better of the two readings where a declared opening capital base
exists (D-44 defines one for DNL), and wiring it is the natural next step. Until
then this module reports the return on new capital and says so in the field name,
rather than reporting one and letting a reader assume the other.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# A step from the final explicit year's earned return to the terminal rate small
# enough to be glide rather than assumption. One percentage point.
_MATERIAL_STEP = 0.01


@dataclass
class TerminalReturn:
    """The terminal return on new capital, its benchmarks, and what they imply."""

    company_id: str
    scenario_id: str
    construction: str                  # "fcff_roic" | "segment_roic" | "bank_roe"
    cost_of_capital: float
    cost_of_capital_name: str          # "WACC" | "Ke"
    terminal_growth: float
    terminal_earnings: float           # NOPAT_T or NPAT_T
    reinvestment_rate: Optional[float]
    return_on_new_capital: Optional[float]
    earned_final_explicit: Optional[float] = None
    # D-42 step 2. Terminal earnings over invested capital at the end of the
    # explicit period -- the return on the WHOLE base, not on new capital. This
    # is the reading D-45 asks the moat work to declare, and the one the two
    # decisions have to agree on.
    terminal_invested_capital: Optional[float] = None
    declared_return: Optional[float] = None
    warnings: List[str] = field(default_factory=list)

    @property
    def excess_over_cost_of_capital(self) -> Optional[float]:
        if self.return_on_new_capital is None:
            return None
        return self.return_on_new_capital - self.cost_of_capital

    @property
    def return_on_whole_capital(self) -> Optional[float]:
        """Terminal earnings over the rolled-forward invested capital base."""
        if not self.terminal_invested_capital:
            return None
        return self.terminal_earnings / self.terminal_invested_capital

    @property
    def governing_return(self) -> Optional[float]:
        """The reading the obligation is judged on: whole capital where it exists.

        D-45's ROIC is a return on capital, not a return on new capital, so where
        a rolled-forward base exists that is the reading that governs. It is not
        a rounding difference in which one is used: DNL Fragmentation sits BELOW
        its WACC on new capital and ABOVE it on the whole base, so the two
        readings disagree about whether a defence is owed at all.
        """
        return self.return_on_whole_capital or self.return_on_new_capital

    @property
    def excess_on_governing_return(self) -> Optional[float]:
        if self.governing_return is None:
            return None
        return self.governing_return - self.cost_of_capital

    @property
    def declared_versus_whole_capital(self) -> Optional[float]:
        """Declared terminal return less the one the capital build produces."""
        whole = self.return_on_whole_capital
        if whole is None or self.declared_return is None:
            return None
        return self.declared_return - whole

    @property
    def step_from_earned(self) -> Optional[float]:
        """Terminal return less the return the final explicit year earned."""
        if self.return_on_new_capital is None or self.earned_final_explicit is None:
            return None
        return self.return_on_new_capital - self.earned_final_explicit


def _reinvestment_and_return(terminal_earnings: float, terminal_free_cash: float,
                             g: float):
    """Reinvestment rate and the implied return on new capital.

    Inverts the growth identity g = return x reinvestment_rate. A terminal that
    reinvests nothing while growing is asserting an infinite return on new
    capital, which is reported as None rather than as a number, because a
    formatted infinity in a table reads as data.
    """
    if not terminal_earnings:
        return None, None
    rate = (terminal_earnings - terminal_free_cash) / terminal_earnings
    if rate <= 0:
        # Growing while releasing cash: no new capital is being put in, so the
        # identity has no return to report. Worth warning about separately.
        return rate, None
    return rate, g / rate


def _pct(x) -> str:
    return "-" if x is None else f"{x:.2%}"  # ssot-allow: display format


def _bp(x) -> str:
    return "-" if x is None else f"{x * 10000:.0f}bp"  # ssot-allow: display format


def _warnings_for(t: TerminalReturn) -> List[str]:
    out: List[str] = []

    if t.reinvestment_rate is not None and t.reinvestment_rate <= 0:
        out.append(
            f"{t.company_id}/{t.scenario_id}: the terminal grows at "
            f"{t.terminal_growth:.2%} while releasing cash rather than reinvesting "  # ssot-allow: display format
            f"(reinvestment rate {t.reinvestment_rate:.1%}). Growth with no "  # ssot-allow: display format
            f"reinvestment is a free perpetuity; the growth identity has no return "
            f"to report and the terminal cannot be defended on a moat."
        )

    excess = t.excess_over_cost_of_capital
    if excess is not None and excess > 0:
        out.append(
            f"{t.company_id}/{t.scenario_id}: terminal return on new capital "
            f"{t.return_on_new_capital:.2%} exceeds {t.cost_of_capital_name} "  # ssot-allow: display format
            f"{t.cost_of_capital:.2%} by {excess * 10000:.0f}bp. The valuation is "  # ssot-allow: display format
            f"claiming reinvestment above the cost of capital in perpetuity, which "
            f"§11.4.2 check 2 requires be defended under §10.6: name the moat "
            f"source, the decay horizon, the threat and the sensitivity (D-42)."
        )

    gap = t.declared_versus_whole_capital
    if gap is not None and abs(gap) > _MATERIAL_STEP:
        out.append(
            f"{t.company_id}/{t.scenario_id}: the defence declares a terminal "
            f"return of {_pct(t.declared_return)} and the capital build produces "
            f"{_pct(t.return_on_whole_capital)} on the whole base -- a gap of "
            f"{_bp(abs(gap))}. D-45 and D-49 both derive reinvestment, one from "
            f"the declared return and one from the balance sheet, and they only "
            f"agree when these two do. One of them is wrong here, and which is a "
            f"judgement rather than a rounding."
        )

    step = t.step_from_earned
    if step is not None and step > _MATERIAL_STEP:
        out.append(
            f"{t.company_id}/{t.scenario_id}: the terminal return "
            f"{t.return_on_new_capital:.2%} sits {step * 10000:.0f}bp ABOVE the "  # ssot-allow: display format
            f"{t.earned_final_explicit:.2%} the final explicit year earns. That is a "  # ssot-allow: display format
            f"recovery assumption, and a recovery assumption is a forecast: it "
            f"should be declared with a basis rather than inherited from the "
            f"terminal rate (M14)."
        )

    return out



# --- "parts" constructors -------------------------------------------------------
# The engines strike the diagnostic inside run(), before a result object exists, so
# they call these with primitives. The result-object constructors below are thin
# wrappers over them, which keeps one definition rather than two that can drift.


def from_bank_parts(*, company_id: str, scenario_id: str, closing_book_equity: float,
                    final_npat: float, terminal_roe: float, terminal_growth: float,
                    cost_of_equity: float) -> TerminalReturn:
    """Bank fork from primitives. See :func:`from_bank` for the reasoning."""
    rate = terminal_growth / terminal_roe if terminal_roe else None
    earned = final_npat / closing_book_equity if closing_book_equity else None
    t = TerminalReturn(
        company_id=company_id, scenario_id=scenario_id, construction="bank_roe",
        cost_of_capital=cost_of_equity, cost_of_capital_name="Ke",
        terminal_growth=terminal_growth,
        terminal_earnings=closing_book_equity * terminal_roe,
        reinvestment_rate=rate, return_on_new_capital=terminal_roe,
        earned_final_explicit=earned,
    )
    t.warnings = _warnings_for(t)
    return t


def from_fcff_parts(*, company_id: str, scenario_id: str, final_nopat: float,
                    terminal_fcff: float, terminal_growth: float,
                    cost_of_capital: float,
                    terminal_invested_capital: Optional[float] = None,
                    declared_return: Optional[float] = None) -> TerminalReturn:
    """Single-segment FCFF fork from primitives. See :func:`from_fcff`."""
    terminal_nopat = final_nopat * (1.0 + terminal_growth)
    rate, ret = _reinvestment_and_return(terminal_nopat, terminal_fcff, terminal_growth)
    t = TerminalReturn(
        company_id=company_id, scenario_id=scenario_id, construction="fcff_roic",
        cost_of_capital=cost_of_capital, cost_of_capital_name="WACC",
        terminal_growth=terminal_growth, terminal_earnings=terminal_nopat,
        reinvestment_rate=rate, return_on_new_capital=ret,
        terminal_invested_capital=terminal_invested_capital,
        declared_return=declared_return,
    )
    t.warnings = _warnings_for(t)
    return t


def from_segment_parts(*, company_id: str, scenario_id: str, final_revenue: float,
                       terminal_ebit_margin: float, tax_rate: float,
                       terminal_fcff: float, terminal_growth: float,
                       cost_of_capital: float) -> TerminalReturn:
    """Segment fork from primitives. See :func:`from_segment`."""
    terminal_nopat = (final_revenue * terminal_ebit_margin * (1.0 - tax_rate)
                      * (1.0 + terminal_growth))
    rate, ret = _reinvestment_and_return(terminal_nopat, terminal_fcff, terminal_growth)
    t = TerminalReturn(
        company_id=company_id, scenario_id=scenario_id, construction="segment_roic",
        cost_of_capital=cost_of_capital, cost_of_capital_name="Ke",
        terminal_growth=terminal_growth, terminal_earnings=terminal_nopat,
        reinvestment_rate=rate, return_on_new_capital=ret,
    )
    t.warnings = _warnings_for(t)
    return t

def from_bank(result, inputs) -> TerminalReturn:
    """Bank fork: the declared terminal ROE, against Ke and against what is earned.

    The bank terminal is the justified price-to-book form, so the return is
    DECLARED rather than implied: ``terminal_roe`` is an input and the retention
    rate is what the identity derives. The reinvestment rate is therefore reported
    as the g/ROE the form implies, and the return on new capital simply is the
    declared ROE -- there is nothing to invert. Both benchmarks still apply.
    """
    return from_bank_parts(
        company_id=result.company_id, scenario_id=result.scenario_id,
        closing_book_equity=result.closing_book_equity, final_npat=result.cash_npat[-1],
        terminal_roe=inputs.terminal_roe, terminal_growth=inputs.terminal_growth,
        cost_of_equity=result.cost_of_equity,
    )


def from_fcff(result, *, company_id: str, scenario_id: str,
              declared_return: Optional[float] = None) -> TerminalReturn:
    """Single-segment FCFF fork: the return the terminal cash flows assert.

    Terminal NOPAT is the final explicit year's NOPAT grown at g, which is exactly
    what the engine uses: it strikes the terminal on the final period's margin and
    tax rate applied to revenue grown at g, and NOPAT is their product.
    """
    return from_fcff_parts(
        company_id=company_id, scenario_id=scenario_id,
        final_nopat=result.nopat[-1], terminal_fcff=result.terminal_fcff,
        terminal_growth=result.terminal_growth, cost_of_capital=result.wacc,
        terminal_invested_capital=result.terminal_invested_capital,
        declared_return=declared_return,
    )


def from_segment(result, inputs, *, company_id: str, scenario_id: str) -> TerminalReturn:
    """Segment fork: same identity, but the terminal carries its OWN margin.

    Unlike the single-segment engine, the segment terminal is struck on a declared
    ``terminal_ebit_margin`` rather than the final explicit year's margin, so
    terminal NOPAT is not the last year's NOPAT grown at g and has to be rebuilt
    from the inputs the engine used.
    """
    return from_segment_parts(
        company_id=company_id, scenario_id=scenario_id,
        final_revenue=result.group_revenue[-1],
        terminal_ebit_margin=inputs.terminal_ebit_margin, tax_rate=inputs.tax_rate,
        terminal_fcff=result.terminal_fcff, terminal_growth=inputs.terminal_growth,
        cost_of_capital=inputs.cost_of_equity,
    )
