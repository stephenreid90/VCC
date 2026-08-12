"""
Single-discipline WACC component build-up (architecture spec section 3.5).

Relocated here from ``dcf/fcf_stub.py`` per the engine implementation plan
(section 1.3): the *one* WACC for a valuation is derived in the assumptions
layer from valuation-date components and handed to the DCF as a single scalar.
The engine never recomputes it per scenario — scenario risk deltas (Rf, ERP,
country risk, beta) are retained for narrative interest but blocked from the
discount rate (section 3.5.6). Terminal growth is the one deliberate
scenario-conditional exception (section 3.5.5).

The build is exposed component-by-component (Rf, ERP, beta, Rd, tax, E, D)
rather than as an opaque scalar so an analyst can rebuild the number from named
inputs and flex any of them by hand — the same discipline the audited workbooks
use on their "WACC Build" sheet.

Convention (documented on the DNL workbook): the tax rate used for the debt tax
shield, the Hamada re-levering of beta, and the terminal operating tax is ONE
blended-statutory rate, for internal consistency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from vcc_valuations.derivation import Derivation


@dataclass(frozen=True)
class WaccBuild:
    """Component build-up of a single, constant-across-scenarios WACC.

    Mirrors the DNL ``WACC Build`` sheet:
        Re          = Rf + beta x ERP                         (CAPM)
        Rd_after    = Rd_pretax x (1 - tax)
        V           = E + D
        WACC        = (E/V) x Re + (D/V) x Rd_after
    """

    risk_free_rate: float          # decimal, e.g. 0.043 = 4.30%
    equity_risk_premium: float     # decimal, e.g. 0.050 = 5.00%
    beta: float                    # unitless, re-levered (Hamada)
    cost_of_debt_pretax: float     # decimal, e.g. 0.060 = 6.00%
    tax_rate: float                # decimal, blended statutory (e.g. 0.275)
    equity_market_value: float     # currency units (e.g. AUD m)
    debt_market_value: float       # currency units (e.g. AUD m)

    @property
    def cost_of_equity(self) -> float:
        """CAPM cost of equity, Re = Rf + beta x ERP."""
        return self.risk_free_rate + self.beta * self.equity_risk_premium

    @property
    def after_tax_cost_of_debt(self) -> float:
        return self.cost_of_debt_pretax * (1.0 - self.tax_rate)

    @property
    def total_capital(self) -> float:
        return self.equity_market_value + self.debt_market_value

    @property
    def equity_weight(self) -> float:
        return self.equity_market_value / self.total_capital

    @property
    def debt_weight(self) -> float:
        return self.debt_market_value / self.total_capital

    @property
    def wacc(self) -> float:
        return (
            self.equity_weight * self.cost_of_equity
            + self.debt_weight * self.after_tax_cost_of_debt
        )

    def derivation(self) -> "Derivation":
        """The WACC build as a fully-traceable derivation (workbook WACC Build sheet).

        Exposes the six derived rows at V6 granularity — B8 cost of equity, B13
        after-tax cost of debt, B18 enterprise value, B19 E/V, B20 D/V, B23 WACC
        — each with its formula and the inputs it consumed. The seven inputs (Rf,
        ERP, beta, Rd_pretax, tax, E, D) are the yellow cells; nothing derived is
        stored.

        NB for DNL: the values reflect the RATIFIED inputs (the owner-ratified
        beta and the normalised tax rate), which supersede the v6 WACC Build
        sheet's cached cells (the earlier beta and the Tax-Bridge blended rate).
        The row STRUCTURE matches V6; the numbers are the production discount
        rate, not the stale workbook cache.
        """
        from vcc_valuations.derivation import DerivationBuilder

        b = DerivationBuilder("wacc_build")
        b.step(
            "B8", "Cost of equity (Re)", self.cost_of_equity,
            "Rf + beta * ERP",
            {"Rf": self.risk_free_rate, "beta": self.beta,
             "ERP": self.equity_risk_premium}, cell="B8", units="%",
        )
        b.step(
            "B13", "Cost of debt, after-tax", self.after_tax_cost_of_debt,
            "Rd_pretax * (1 - tax)",
            {"Rd_pretax": self.cost_of_debt_pretax, "tax": self.tax_rate},
            cell="B13", units="%",
        )
        b.step(
            "B18", "Enterprise value (V = E + D)", self.total_capital,
            "E + D",
            {"E": self.equity_market_value, "D": self.debt_market_value},
            cell="B18", units="AUD m",
        )
        b.step(
            "B19", "E/V", self.equity_weight, "E / V",
            {"E": self.equity_market_value, "V": self.total_capital},
            cell="B19", units="%",
        )
        b.step(
            "B20", "D/V", self.debt_weight, "D / V",
            {"D": self.debt_market_value, "V": self.total_capital},
            cell="B20", units="%",
        )
        b.step(
            "B23", "Baseline WACC", self.wacc,
            "(E/V) * Re + (D/V) * Rd_after_tax",
            {"E/V": self.equity_weight, "Re": self.cost_of_equity,
             "D/V": self.debt_weight, "Rd_after_tax": self.after_tax_cost_of_debt},
            cell="B23", units="%",
        )
        return b.build(result_key="B23")

    def describe(self) -> List[str]:
        """One-line-per-component description for printable headers / traces."""
        return [
            f"Rf={self.risk_free_rate:.2%}, ERP={self.equity_risk_premium:.2%}, beta={self.beta:.2f}",
            f"Re = Rf + beta x ERP = {self.cost_of_equity:.2%}",
            f"Rd_pretax={self.cost_of_debt_pretax:.2%}, tax={self.tax_rate:.1%}, "
            f"Rd_after_tax={self.after_tax_cost_of_debt:.2%}",
            f"E={self.equity_market_value:,.1f}, D={self.debt_market_value:,.1f}, "
            f"E/V={self.equity_weight:.1%}, D/V={self.debt_weight:.1%}",
            f"WACC = {self.equity_weight:.4f} x {self.cost_of_equity:.2%} + "
            f"{self.debt_weight:.4f} x {self.after_tax_cost_of_debt:.2%} = {self.wacc:.4%}",
        ]
