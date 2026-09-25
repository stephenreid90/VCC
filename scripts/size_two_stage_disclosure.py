"""Regenerate the two-stage terminal disclosure set (D-62 to D-66, build order item 3).

Companion to ``src/vcc_valuations/dcf/terminal_value.two_stage_disclosure``.
Standing rule 4: any number quoting this disclosure in a write-up cites the
committed set this script writes, ``design/methodology/terminal_disclosure_set.yaml``,
and ``tests/dcf/test_two_stage_disclosure.py`` asserts it regenerates.

This disclosure sits ALONGSIDE each engine's headline terminal value -- it does
not replace it, and no golden moves because of it. It is available only where
the five-forces work has declared a moat length (D-63's
``ExcessReturnDefence.decay_horizon``) for that company x scenario. At this
build that is three of eighteen valuations, all DNL; the other fifteen report
"not available" honestly rather than a moat length nobody chose. Assigning the
rest is a later, dedicated pass.

    python scripts/size_two_stage_disclosure.py            # print and rewrite the set
    python scripts/size_two_stage_disclosure.py --check     # print only, change nothing
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402

from vcc_valuations.dcf.terminal_value import TwoStageDisclosure, two_stage_disclosure  # noqa: E402

SET_PATH = ROOT / "design" / "methodology" / "terminal_disclosure_set.yaml"

COMPANIES = [
    ("dnl", "industrial_explosives"),
    ("wbc", "australian_major_banks"),
    ("csl", "biopharmaceuticals"),
]


def _scenarios() -> List[str]:
    return sorted(p.stem for p in (ROOT / "data" / "scenarios").glob("*.yaml"))


def collect() -> List[TwoStageDisclosure]:
    return [two_stage_disclosure(ROOT, c, a, s)
            for c, a in COMPANIES for s in _scenarios()]


def _r(x, nd=6):
    return None if x is None else round(float(x), nd)


def as_set(rows: List[TwoStageDisclosure]) -> dict:
    return {
        "terminal_disclosure_set": {
            "name": "current",
            "basis": (
                "The two-stage terminal (D-62 to D-66), disclosed alongside each "
                "engine's own headline terminal value, wherever a moat length has "
                "been declared for that company x scenario (D-63's "
                "excess_return_defence.decay_horizon). N is the band midpoint "
                "(D-63's default); the band ends are a sensitivity, not shown "
                "here. Not available means no decay_horizon is declared yet -- "
                "assigning the rest is a later, dedicated pass, not a default."
            ),
            "regenerated_by": "scripts/size_two_stage_disclosure.py",
            "asserted_by": "tests/dcf/test_two_stage_disclosure.py",
            "decisions": ["D-62", "D-63", "D-64", "D-65", "D-66"],
            "rows": [
                {
                    "company": v.company_id,
                    "scenario": v.scenario_id,
                    "available": v.available,
                    "reason": v.reason,
                    "cost_of_capital": _r(v.cost_of_capital),
                    "terminal_growth": _r(v.terminal_growth),
                    "capital": _r(v.capital, 3),
                    "earned_return": _r(v.earned_return),
                    "moat_years": _r(v.moat_years, 2),
                    "moat_band": v.moat_band,
                    "moat_basis": v.moat_basis,
                    "terminal_value": _r(v.terminal_value, 3),
                    "value_per_share": _r(v.value_per_share, 4),
                    "engine_terminal_value": _r(v.engine_terminal_value, 3),
                    "engine_value_per_share": _r(v.engine_value_per_share, 4),
                }
                for v in rows
            ],
        }
    }


def print_table(rows: List[TwoStageDisclosure]) -> None:
    for v in rows:
        if not v.available:
            print(f"{v.company_id:4} {v.scenario_id:32} not available -- {v.reason}")
            continue
        print(f"{v.company_id:4} {v.scenario_id:32} moat {v.moat_band:>8} "
              f"({v.moat_years:.1f}y)  two-stage ${v.value_per_share:,.2f}/sh  "  # ssot-allow: display format
              f"vs engine ${v.engine_value_per_share:,.2f}/sh")  # ssot-allow: display format


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
