"""Size every terminal-value basis on offer, for every valuation, on one axis.

Companion to ``design/methodology/terminal_value.md`` (D-62 to D-66, PROPOSED).
Regenerates ``design/methodology/terminal_option_sets.yaml`` and prints the table.
Standing rule 4: a number in that paper cites this set, this script regenerates it
from the production engines, and ``tests/dcf/test_terminal_option_sets.py`` asserts
it.

Nothing here changes a valuation. Each basis is struck on the engine's own year-T
figures and translated into value per share with the engine's own terminal discount
factor and share count, so the per-share figures differ from the engine's only by
the terminal value swapped in.

The two-stage form, with C the capital at the end of the forecast (invested capital
for FCFF, book equity for the bank), R the return earned on it, r the discount rate,
g nominal growth and N the years the excess return runs beyond the forecast:

    TV(N) = C * [ m * (1 - k**N) + k**N ],   m = (R - g) / (r - g),   k = (1 + g) / (1 + r)

m is the justified price-to-capital of a perpetual excess return; k**N is the weight
left on plain capital once the moat has expired. N = 0 gives TV = C (convergence at
the end of the forecast); N -> infinity gives C * m (Gordon on the earned return).

    python scripts/size_terminal_options.py            # print and rewrite the set
    python scripts/size_terminal_options.py --check     # print only, change nothing
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402

from vcc_valuations.dcf.terminal_value import (  # noqa: E402
    ImpliedMoat, engine_facts, implied_moat, implied_perpetual_return,
    perpetual_multiple, return_on_new_capital, two_stage,
)

SET_PATH = ROOT / "design" / "methodology" / "terminal_option_sets.yaml"

COMPANIES = [
    ("dnl", "industrial_explosives"),
    ("wbc", "australian_major_banks"),
    ("csl", "biopharmaceuticals"),
]

# Years the excess return is allowed to run beyond the explicit forecast. A grid for
# illustration, not a recommendation: the default is ruled per D-63.
EXTENSION_GRID = (0, 5, 10, 20)

# Forward EV/EBITDA multiples shown for the exit-multiple basis. Illustrative only,
# chosen to bracket what the option looks like, not a market view.
EXIT_MULTIPLE_GRID = (8, 10, 12)


# ------------------------------------------------------------ one valuation
@dataclass
class Basis:
    name: str
    terminal_value: float
    value_per_share: float
    share_of_value: float
    tv_over_capital: Optional[float] = None
    forward_ebit_multiple: Optional[float] = None
    forward_ebitda_multiple: Optional[float] = None
    forward_pe: Optional[float] = None
    implied_perpetual_return: Optional[float] = None
    implied_return_on_new_capital: Optional[float] = None
    implied_moat: Optional[ImpliedMoat] = None


@dataclass
class Valuation:
    company_id: str
    scenario_id: str
    construction: str
    horizon_years: int
    cost_of_capital: float
    terminal_growth: float
    capital: Optional[float]
    earned_return: Optional[float]
    bases: List[Basis] = field(default_factory=list)


def size_one(company_id: str, archetype_id: str, scenario_id: str) -> Valuation:
    f = engine_facts(ROOT, company_id, archetype_id, scenario_id)
    t = f["t"]
    r, g = t.cost_of_capital, t.terminal_growth
    grow = 1.0 + g
    e1 = f["earnings_T"] * grow
    cf1 = f["cash_flow_T"] * grow
    capital = f["capital"]
    earned = None if capital is None else e1 / capital

    v = Valuation(company_id, scenario_id, f["construction"], f["horizon"], r, g,
                  capital, earned)

    def basis(name: str, tv: float) -> Basis:
        delta_pv = (tv - f["tv"]) * f["tdf"]
        vps = f["vps"] + delta_pv / f["shares"] * f["per_share_scale"]
        total = f["value_total"] + delta_pv
        b = Basis(name=name, terminal_value=tv, value_per_share=vps,
                  share_of_value=tv * f["tdf"] / total)
        if f["ebit_T"] is not None:
            b.forward_ebit_multiple = tv / (f["ebit_T"] * grow)
            b.forward_ebitda_multiple = tv / (f["ebitda_T"] * grow)
        else:
            b.forward_pe = tv / e1
        if capital is not None:
            b.tv_over_capital = tv / capital
            b.implied_moat = implied_moat(tv, capital, earned, r, g)
            b.implied_perpetual_return = implied_perpetual_return(tv, capital, r, g)
        return b

    def gordon_basis(name: str, tv: float) -> Basis:
        # A single-stage perpetuity capitalises one cash flow, so the growth identity
        # says what it assumes about returns on the capital it adds to grow at g.
        b = basis(name, tv)
        b.implied_return_on_new_capital = return_on_new_capital(tv * (r - g), e1, g)
        return b

    v.bases.append(gordon_basis("engine_current", f["tv"]))
    v.bases.append(gordon_basis("simple", cf1 / (r - g)))
    if capital is not None:
        for n in EXTENSION_GRID:
            v.bases.append(basis(f"two_stage_plus_{n}", two_stage(capital, earned, r, g, n)))
        v.bases.append(basis("two_stage_perpetual", capital * perpetual_multiple(earned, r, g)))
    if f.get("market_price"):
        # Reverse-solve: the TV that, with this forecast, reproduces the market price.
        # Not a view that the forecast is right -- a statement of what the price needs
        # the terminal to carry if it is.
        gap_per_share = f["market_price"] / f["reported_per_engine"] - f["vps"]
        v.bases.append(basis("market_implied",
                             f["tv"] + gap_per_share * f["shares"] / f["tdf"]))
    if f["ebitda_T"] is not None:
        for mult in EXIT_MULTIPLE_GRID:
            v.bases.append(basis(f"exit_{mult}x_ebitda", mult * f["ebitda_T"] * grow))
    return v


def _scenarios() -> List[str]:
    return sorted(p.stem for p in (ROOT / "data" / "scenarios").glob("*.yaml"))


def collect() -> List[Valuation]:
    return [size_one(c, a, s) for c, a in COMPANIES for s in _scenarios()]


# ------------------------------------------------------------------- output
def _r(x, nd=6):
    return None if x is None else round(float(x), nd)


def as_set(rows: List[Valuation]) -> dict:
    return {
        "terminal_option_sets": {
            "current": {
                "name": "current",
                "basis": (
                    "Every terminal basis on offer, struck on production engine "
                    "year-T output and translated to value per share with the "
                    "engine's own terminal discount factor. Capital is invested "
                    "capital at T (D-44/D-49) for FCFF and closing book equity for "
                    "the bank; CSL has none until its capital base is built. The "
                    "earned return is next-year earnings over capital at T. The "
                    "two-stage form holds capital and runs the earned return N "
                    "years beyond the forecast, then converges. Implied moat "
                    "inverts that form. Forward multiples are on year T+1 "
                    "earnings. Implied return on new capital applies the growth "
                    "identity to the cash flow each TV capitalises."
                ),
                "regenerated_by": "scripts/size_terminal_options.py",
                "asserted_by": "tests/dcf/test_terminal_option_sets.py",
                "decisions": ["D-62 to D-66 (PROPOSED)", "D-44", "D-49", "M14"],
                "extension_grid_years": list(EXTENSION_GRID),
                "exit_multiple_grid": list(EXIT_MULTIPLE_GRID),
                "rows": [
                    {
                        "company": v.company_id,
                        "scenario": v.scenario_id,
                        "construction": v.construction,
                        "horizon_years": v.horizon_years,
                        "cost_of_capital": _r(v.cost_of_capital),
                        "terminal_growth": _r(v.terminal_growth),
                        "capital_at_T": _r(v.capital, 3),
                        "earned_return": _r(v.earned_return),
                        "bases": [
                            {
                                "basis": b.name,
                                "terminal_value": _r(b.terminal_value, 3),
                                "value_per_share": _r(b.value_per_share, 4),
                                "share_of_value": _r(b.share_of_value, 4),
                                "tv_over_capital": _r(b.tv_over_capital, 4),
                                "forward_ebit_multiple": _r(b.forward_ebit_multiple, 3),
                                "forward_ebitda_multiple": _r(b.forward_ebitda_multiple, 3),
                                "forward_pe": _r(b.forward_pe, 3),
                                "implied_perpetual_return":
                                    _r(b.implied_perpetual_return),
                                "implied_return_on_new_capital":
                                    _r(b.implied_return_on_new_capital),
                                "implied_moat_status":
                                    None if b.implied_moat is None else b.implied_moat.status,
                                "implied_moat_years_total": (
                                    None if b.implied_moat is None
                                    or b.implied_moat.extension_years is None
                                    else round(v.horizon_years
                                               + b.implied_moat.extension_years, 1)),
                            }
                            for b in v.bases
                        ],
                    }
                    for v in rows
                ],
            }
        }
    }


def _f(x, fmt):
    return "-" if x is None else format(x, fmt)


def print_table(rows: List[Valuation]) -> None:
    for v in rows:
        print(f"\n{v.company_id} / {v.scenario_id}   r {_f(v.cost_of_capital, '.2%')}  "  # ssot-allow: display format
              f"g {_f(v.terminal_growth, '.2%')}  capital {_f(v.capital, ',.0f')}  "  # ssot-allow: display format
              f"earned {_f(v.earned_return, '.2%')}")  # ssot-allow: display format
        print(f"  {'basis':22} {'TV':>10} {'$/sh':>8} {'TV%':>6} {'TV/C':>6} "
              f"{'EBIT x':>7} {'EBITDA x':>8} {'P/E':>6} {'R perp':>7} {'RONIC':>7} {'moat':>18}")
        for b in v.bases:
            if b.implied_moat is None:
                moat = "-"
            elif b.implied_moat.status == "finite":
                moat = f"{v.horizon_years + b.implied_moat.extension_years:.0f} yrs"  # ssot-allow: display format
            else:
                moat = b.implied_moat.status
            print(f"  {b.name:22} {b.terminal_value:>10,.0f} {b.value_per_share:>8.2f} "  # ssot-allow: display format
                  f"{b.share_of_value:>6.0%} {_f(b.tv_over_capital, '.2f'):>6} "  # ssot-allow: display format
                  f"{_f(b.forward_ebit_multiple, '.1f'):>7} {_f(b.forward_ebitda_multiple, '.1f'):>8} "  # ssot-allow: display format
                  f"{_f(b.forward_pe, '.1f'):>6} {_f(b.implied_perpetual_return, '.1%'):>7} "  # ssot-allow: display format
                  f"{_f(b.implied_return_on_new_capital, '.1%'):>7} "  # ssot-allow: display format
                  f"{moat:>18}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="print only; do not rewrite the committed set")
    args = ap.parse_args()
    rows = collect()
    print_table(rows)
    if args.check:
        return 0
    with open(SET_PATH, "w", encoding="utf-8") as fh:
        yaml.safe_dump(as_set(rows), fh, sort_keys=False, allow_unicode=True)
    print(f"\nwrote {SET_PATH.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
