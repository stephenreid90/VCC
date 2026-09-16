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
    warnings: List[str] = field(default_factory=list)

    @property
    def excess_over_cost_of_capital(self) -> Optional[float]:
        if self.return_on_new_capital is None:
            return None
        return self.return_on_new_capital - self.cost_of_capital

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


def from_bank(result, inputs) -> TerminalReturn:
    """Bank fork: the declared terminal ROE, against Ke and against what is earned.

    The bank terminal is the justified price-to-book form, so the return is
    DECLARED rather than implied: ``terminal_roe`` is an input and the retention
    rate is what the identity derives. The reinvestment rate is therefore reported
    as the g/ROE the form implies, and the return on new capital simply is the
    declared ROE -- there is nothing to invert. Both benchmarks still apply.
    """
    roe = inputs.terminal_roe
    terminal_npat = result.closing_book_equity * roe
    rate = inputs.terminal_growth / roe if roe else None
    earned = (result.cash_npat[-1] / result.closing_book_equity
              if result.closing_book_equity else None)

    t = TerminalReturn(
        company_id=result.company_id,
        scenario_id=result.scenario_id,
        construction="bank_roe",
        cost_of_capital=result.cost_of_equity,
        cost_of_capital_name="Ke",
        terminal_growth=inputs.terminal_growth,
        terminal_earnings=terminal_npat,
        reinvestment_rate=rate,
        return_on_new_capital=roe,
        earned_final_explicit=earned,
    )
    t.warnings = _warnings_for(t)
    return t


def from_fcff(result, *, company_id: str, scenario_id: str) -> TerminalReturn:
    """Single-segment FCFF fork: the return the terminal cash flows assert.

    Terminal NOPAT is the final explicit year's NOPAT grown at g, which is exactly
    what the engine uses: it strikes the terminal on the final period's margin and
    tax rate applied to revenue grown at g, and NOPAT is their product.
    """
    g = result.terminal_growth
    terminal_nopat = result.nopat[-1] * (1.0 + g)
    rate, ret = _reinvestment_and_return(terminal_nopat, result.terminal_fcff, g)

    t = TerminalReturn(
        company_id=company_id,
        scenario_id=scenario_id,
        construction="fcff_roic",
        cost_of_capital=result.wacc,
        cost_of_capital_name="WACC",
        terminal_growth=g,
        terminal_earnings=terminal_nopat,
        reinvestment_rate=rate,
        return_on_new_capital=ret,
    )
    t.warnings = _warnings_for(t)
    return t


def from_segment(result, inputs, *, company_id: str, scenario_id: str) -> TerminalReturn:
    """Segment fork: same identity, but the terminal carries its OWN margin.

    Unlike the single-segment engine, the segment terminal is struck on a declared
    ``terminal_ebit_margin`` rather than the final explicit year's margin, so
    terminal NOPAT is not the last year's NOPAT grown at g and has to be rebuilt
    from the inputs the engine used.
    """
    g = inputs.terminal_growth
    final_revenue = result.group_revenue[-1]
    terminal_nopat = (final_revenue * inputs.terminal_ebit_margin
                      * (1.0 - inputs.tax_rate) * (1.0 + g))
    rate, ret = _reinvestment_and_return(terminal_nopat, result.terminal_fcff, g)

    t = TerminalReturn(
        company_id=company_id,
        scenario_id=scenario_id,
        construction="segment_roic",
        cost_of_capital=inputs.cost_of_equity,
        cost_of_capital_name="Ke",
        terminal_growth=g,
        terminal_earnings=terminal_nopat,
        reinvestment_rate=rate,
        return_on_new_capital=ret,
    )
    t.warnings = _warnings_for(t)
    return t
