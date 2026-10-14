"""Size the DERIVED terminal growth against its cap and against the typed rate it replaced.

D-72 (DNL) and D-79 (WBC, CSL). Regenerates ``design/methodology/terminal_growth_sets.yaml``
and prints the table. Standing rule 4: the published figures come from this script and
``tests/dcf/test_terminal_growth_sets.py`` asserts them, so a number in a note cites the
set rather than a scratch run.

For every company x scenario: the chain in equilibrium at the end of the explicit period
(``g_chain``), the scenario's nominal GDP there (``g_cap``), the terminal growth the engine
uses (``g`` = min of the two), and the live value per share. Where a typed rate was
retired by D-79 the set also carries that rate and the level it gave, so the disclosure
("most of the movement is the typed 3% giving way to the nominal GDP the scenarios
already assert") is a figure that regenerates, not a sentence in a note.

    python scripts/size_terminal_growth.py            # print and rewrite the set
    python scripts/size_terminal_growth.py --check     # print only, change nothing
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402

from vcc_valuations.dcf.bank_engine import BankEngine  # noqa: E402
from vcc_valuations.dcf.fcf_engine import FcfEngine  # noqa: E402
from vcc_valuations.dcf.segment_engine import SegmentEngine  # noqa: E402
from vcc_valuations.translator import (  # noqa: E402
    bank_terminal_growth_from_data, build_bank_inputs_from_data,
    build_engine_inputs_from_data, build_segment_inputs_from_data, load_inputs,
    segment_terminal_growth_from_data, terminal_growth_from_data,
)

SET_PATH = ROOT / "design" / "methodology" / "terminal_growth_sets.yaml"

COMPANIES = [
    ("dnl", "industrial_explosives"),
    ("wbc", "australian_major_banks"),
    ("csl", "biopharmaceuticals"),
]

# The per-scenario terminal growth each company file TYPED until D-79 retired it
# (commit e146c12 and earlier). Kept here as the historical record the disclosure
# is struck against; nothing in the live model reads it. DNL's typed rate left
# dnl.yaml under D-72 (2 Oct 2026) and its before/after is in DECISIONS.md D-72.
RETIRED_TYPED_GROWTH = {
    "wbc": {
        "orderly_convergence": 0.0375, "muddle_through": 0.035, "ai_productivity_lag": 0.0325,  # ssot-allow: retired typed rates, historical record (D-79)
        "fragmentation": 0.0325, "disorderly_climate_crystallisation": 0.0325,  # ssot-allow: retired typed rates, historical record (D-79)
        "stagflation_persists": 0.0325,  # ssot-allow: retired typed rates, historical record (D-79)
    },
    "csl": {
        "orderly_convergence": 0.0325, "muddle_through": 0.03, "ai_productivity_lag": 0.0288,  # ssot-allow: retired typed rates, historical record (D-79)
        "fragmentation": 0.0275, "disorderly_climate_crystallisation": 0.0275,  # ssot-allow: retired typed rates, historical record (D-79)
        "stagflation_persists": 0.03,  # ssot-allow: retired typed rates, historical record (D-79)
    },
}


@dataclass(frozen=True)
class TerminalGrowthRow:
    company_id: str
    scenario_id: str
    horizon_years: int
    g_chain: float
    g_cap: float
    g: float
    capped: bool
    value_per_share: float
    retired_typed_growth: Optional[float]
    value_per_share_at_typed: Optional[float]

    @property
    def level_change(self) -> Optional[float]:
        if self.value_per_share_at_typed is None:
            return None
        return self.value_per_share / self.value_per_share_at_typed - 1.0


def _scenarios() -> list[str]:
    return sorted(p.stem for p in (ROOT / "data" / "scenarios").glob("*.yaml"))


def _one(company_id: str, archetype_id: str, scenario_id: str) -> TerminalGrowthRow:
    inputs = load_inputs(ROOT, scenario_id, archetype_id, company_id)
    typed = RETIRED_TYPED_GROWTH.get(company_id, {}).get(scenario_id)
    if company_id == "wbc":
        bi = build_bank_inputs_from_data(inputs, scenario_id)
        d = bank_terminal_growth_from_data(inputs, scenario_id, bi.horizon_years)
        live = BankEngine().run(bi).value_per_share
        at_typed = None if typed is None else BankEngine().run(replace(bi, terminal_growth=typed)).value_per_share
        H = bi.horizon_years
    elif company_id == "csl":
        si = build_segment_inputs_from_data(inputs, scenario_id)
        d = segment_terminal_growth_from_data(inputs, scenario_id, si.horizon_years)
        live = SegmentEngine().run(si).value_per_share_aud
        at_typed = None if typed is None else SegmentEngine().run(replace(si, terminal_growth=typed)).value_per_share_aud
        H = si.horizon_years
    else:
        ei = build_engine_inputs_from_data(inputs, scenario_id)
        d = terminal_growth_from_data(inputs, scenario_id, ei.horizon_years)
        live = FcfEngine().run(ei).value_per_share
        at_typed = None
        H = ei.horizon_years
    g_chain = d["g_chain"].value
    g_cap = d["g_cap"].value
    return TerminalGrowthRow(
        company_id=company_id, scenario_id=scenario_id, horizon_years=H,
        g_chain=g_chain, g_cap=g_cap, g=d.result, capped=g_cap < g_chain,
        value_per_share=live, retired_typed_growth=typed, value_per_share_at_typed=at_typed,
    )


def collect() -> list[TerminalGrowthRow]:
    return [_one(c, a, s) for c, a in COMPANIES for s in _scenarios()]


def _r(x, n=6):
    return None if x is None else round(x, n)


def as_set(rows: list[TerminalGrowthRow]) -> dict:
    """The committed entry: one record per valuation."""
    return {
        "terminal_growth_sets": {
            "current": {
                "name": "current",
                "basis": (
                    "Terminal growth DERIVED for every company (D-72 for the industrial "
                    "chain, D-79 for the bank and segment chains): the growth chain read at "
                    "the end of the explicit period with the archetype's current-cycle terms "
                    "at their equilibrium reading (D-78), capped at the scenario's nominal "
                    "GDP there, (1 + world real GDP)(1 + advanced CPI) - 1. g_chain is the "
                    "uncapped reading, g_cap the cap, g what the engine uses. Where D-79 "
                    "retired a typed rate, retired_typed_growth and value_per_share_at_typed "
                    "are the rate and the level the same engine gives on it today, so the "
                    "disclosed movement regenerates. Values per share are AUD."
                ),
                "regenerated_by": "scripts/size_terminal_growth.py",
                "asserted_by": "tests/dcf/test_terminal_growth_sets.py",
                "decisions": ["D-72", "D-78", "D-79"],
                "rows": [
                    {
                        "company": r.company_id,
                        "scenario": r.scenario_id,
                        "horizon_years": r.horizon_years,
                        "g_chain": _r(r.g_chain),
                        "g_cap": _r(r.g_cap),
                        "g": _r(r.g),
                        "capped": r.capped,
                        "value_per_share": _r(r.value_per_share, 4),
                        "retired_typed_growth": _r(r.retired_typed_growth),
                        "value_per_share_at_typed": _r(r.value_per_share_at_typed, 4),
                        "level_change": _r(r.level_change, 4),
                    }
                    for r in rows
                ],
            }
        }
    }


def _pct(x) -> str:
    return "-" if x is None else f"{x:.2%}"  # ssot-allow: display format


def print_table(rows: list[TerminalGrowthRow]) -> None:
    print(f"{'company':5} {'scenario':34} {'g_chain':>8} {'g_cap':>7} {'g':>7} {'cap?':>5} "
          f"{'level':>9} {'typed g':>8} {'at typed':>9} {'change':>7}")
    print("-" * 108)
    for r in rows:
        lvl_t = "-" if r.value_per_share_at_typed is None else f"{r.value_per_share_at_typed:.2f}"  # ssot-allow: display format
        print(f"{r.company_id:5} {r.scenario_id:34} {_pct(r.g_chain):>8} {_pct(r.g_cap):>7} {_pct(r.g):>7} "
              f"{'yes' if r.capped else '':>5} {r.value_per_share:9.2f} {_pct(r.retired_typed_growth):>8} "  # ssot-allow: display format
              f"{lvl_t:>9} {_pct(r.level_change):>7}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="print only; do not rewrite the committed set")
    args = ap.parse_args()
    rows = collect()
    print_table(rows)
    if args.check:
        return 0
    SET_PATH.write_text(yaml.safe_dump(as_set(rows), sort_keys=False, allow_unicode=True),
                        encoding="utf-8")
    print(f"\nwrote {SET_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
