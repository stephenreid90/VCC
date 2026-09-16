"""Size the terminal return against both its benchmarks, for every valuation.

D-42 (PROPOSED) and M14. Regenerates ``design/methodology/terminal_return_sets.yaml``
and prints the table. Follows the standing-rule-4 pattern set by
``size_horizon_variants.py``: the published table is a committed entry carrying the
figures it produced, this script regenerates it, and
``tests/dcf/test_terminal_return_sets.py`` asserts it — so a number in a document
cites a set name rather than a scratch run nobody can reproduce.

    python scripts/size_terminal_returns.py            # print and rewrite the set
    python scripts/size_terminal_returns.py --check     # print only, change nothing
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402

from vcc_valuations.dcf import terminal_return as tr  # noqa: E402
from vcc_valuations.dcf.bank_engine import BankEngine  # noqa: E402
from vcc_valuations.dcf.fcf_engine import FcfEngine  # noqa: E402
from vcc_valuations.dcf.segment_engine import SegmentEngine  # noqa: E402
from vcc_valuations.translator import (  # noqa: E402
    build_bank_inputs_from_data, build_engine_inputs_from_data,
    build_segment_inputs_from_data, load_inputs,
)

SET_PATH = ROOT / "design" / "methodology" / "terminal_return_sets.yaml"

COMPANIES = [
    ("dnl", "industrial_explosives"),
    ("wbc", "australian_major_banks"),
    ("csl", "biopharmaceuticals"),
]


def _scenarios() -> list[str]:
    return sorted(p.stem for p in (ROOT / "data" / "scenarios").glob("*.yaml"))


def _one(company_id: str, archetype_id: str, scenario_id: str) -> tr.TerminalReturn:
    inputs = load_inputs(ROOT, scenario_id, archetype_id, company_id)
    if company_id == "wbc":
        bi = build_bank_inputs_from_data(inputs, scenario_id)
        return tr.from_bank(BankEngine().run(bi), bi)
    if company_id == "csl":
        si = build_segment_inputs_from_data(inputs, scenario_id)
        return tr.from_segment(SegmentEngine().run(si), si,
                               company_id=company_id, scenario_id=scenario_id)
    ei = build_engine_inputs_from_data(inputs, scenario_id)
    return tr.from_fcff(FcfEngine().run(ei),
                        company_id=company_id, scenario_id=scenario_id)


def collect() -> list[tr.TerminalReturn]:
    out = []
    for company_id, archetype_id in COMPANIES:
        for scenario_id in _scenarios():
            out.append(_one(company_id, archetype_id, scenario_id))
    return out


def _pct(x) -> str:
    return "-" if x is None else f"{x:.2%}"  # ssot-allow: display format


def _bp(x) -> str:
    return "-" if x is None else f"{x * 10000:+,.0f}"  # ssot-allow: display format


def as_set(rows: list[tr.TerminalReturn]) -> dict:
    """The committed entry: one record per valuation, plus what it implies."""
    return {
        "terminal_return_sets": {
            "current": {
                "name": "current",
                "basis": (
                    "Terminal return on NEW capital, from the growth identity "
                    "g = return x reinvestment_rate, struck on production engine "
                    "output. For the bank fork the return is declared "
                    "(terminal_roe) and the identity derives the retention rate "
                    "instead, so the declared rate is reported. Return on the "
                    "WHOLE capital base is not reported: FcfEngine carries no "
                    "invested-capital roll-forward, so it cannot be struck from "
                    "engine output today."
                ),
                "regenerated_by": "scripts/size_terminal_returns.py",
                "asserted_by": "tests/dcf/test_terminal_return_sets.py",
                "decisions": ["D-42 (PROPOSED)", "M14", "D-07 non-blocking precedent"],
                "rows": [
                    {
                        "company": r.company_id,
                        "scenario": r.scenario_id,
                        "construction": r.construction,
                        "cost_of_capital_name": r.cost_of_capital_name,
                        "cost_of_capital": round(r.cost_of_capital, 6),
                        "terminal_growth": round(r.terminal_growth, 6),
                        "reinvestment_rate": (None if r.reinvestment_rate is None
                                              else round(r.reinvestment_rate, 6)),
                        "return_on_new_capital": (None if r.return_on_new_capital is None
                                                  else round(r.return_on_new_capital, 6)),
                        "excess_over_cost_of_capital": (
                            None if r.excess_over_cost_of_capital is None
                            else round(r.excess_over_cost_of_capital, 6)),
                        "earned_final_explicit": (None if r.earned_final_explicit is None
                                                  else round(r.earned_final_explicit, 6)),
                        "step_from_earned": (None if r.step_from_earned is None
                                             else round(r.step_from_earned, 6)),
                        "warning_count": len(r.warnings),
                    }
                    for r in rows
                ],
            }
        }
    }


def print_table(rows: list[tr.TerminalReturn]) -> None:
    print(f"{'company':5} {'scenario':34} {'ret_new':>8} {'cost':>7} "
          f"{'excess':>8} {'earned':>8} {'step':>8}")
    print("-" * 82)
    for r in rows:
        print(f"{r.company_id:5} {r.scenario_id:34} {_pct(r.return_on_new_capital):>8} "
              f"{_pct(r.cost_of_capital):>7} {_bp(r.excess_over_cost_of_capital):>8} "
              f"{_pct(r.earned_final_explicit):>8} {_bp(r.step_from_earned):>8}")

    warned = [w for r in rows for w in r.warnings]
    print(f"\n{len(warned)} warning(s) across {len(rows)} valuations:")
    for r in rows:
        for w in r.warnings:
            print(f"  - {w}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="print only; do not rewrite the committed set")
    args = ap.parse_args()

    rows = collect()
    print_table(rows)

    if args.check:
        return 0
    SET_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SET_PATH, "w", encoding="utf-8") as fh:
        yaml.safe_dump(as_set(rows), fh, sort_keys=False, allow_unicode=True)
    print(f"\nwrote {SET_PATH.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
