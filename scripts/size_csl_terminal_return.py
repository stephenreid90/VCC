"""Size CSL's terminal return for reporting, with and without goodwill (D-86).

Regenerates ``design/methodology/csl_terminal_return_sets.yaml``. Each scenario
carries three things a report must show beside the headline value:

1. The earned starting return on the capital base as the model measures it
   (goodwill excluded, D-44), and the same return with goodwill included.
2. The per-share value with goodwill included, to show it barely moves.
3. A sensitivity band over the starting return and the fade length.

Goodwill is read from ``data/financials/csl.yaml`` rather than typed here, and the
return comes from the general ``terminal_return.goodwill_inclusive_return`` (D-86a),
which ``scripts/size_terminal_returns.py`` applies to every company with a base.
Follows the standing-rule-4 pattern: the committed set is what the documents
cite, and ``tests/dcf/test_csl_terminal_return_sets.py`` asserts it.

    python scripts/size_csl_terminal_return.py          # rewrite the set
    python scripts/size_csl_terminal_return.py --check  # print only
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402

from vcc_valuations.dcf.segment_engine import SegmentEngine  # noqa: E402
from vcc_valuations.dcf.terminal_return import (  # noqa: E402
    goodwill_from_financials, goodwill_inclusive_return,
)
from vcc_valuations.translator import (  # noqa: E402
    build_segment_inputs_from_data, load_inputs,
)

SET_PATH = ROOT / "design" / "methodology" / "csl_terminal_return_sets.yaml"
FINANCIALS = ROOT / "data" / "financials" / "csl.yaml"

SCENARIOS = [
    "orderly_convergence", "muddle_through", "ai_productivity_lag",
    "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists",
]
# Fade lengths: the matrix midpoint (20, the model's own, D-93), the band ends
# (25 and 15, the D-63 sensitivity) and a shorter line.
FADES = (20.0, 25.0, 15.0, 10.0)
# Starting returns: None is the model's earned return; the rest are fixed lines.
STARTS = (None, 0.20, 0.15, 0.12)  # ssot-allow: sensitivity grid, not a register value


def goodwill() -> float:
    """Goodwill from the financials file, by the general reader (D-86a)."""
    gw = goodwill_from_financials(yaml.safe_load(FINANCIALS.read_text(encoding="utf-8")))
    if gw is None:
        raise ValueError("data/financials/csl.yaml has no goodwill figure (D-44).")
    return gw


def size_scenario(scenario: str, gw: float) -> dict:
    inp = load_inputs(ROOT, scenario, "biopharmaceuticals", "csl")
    si = build_segment_inputs_from_data(inp, scenario)
    base = SegmentEngine().run(si)
    gr = goodwill_inclusive_return(
        base.terminal_earned_return * si.terminal_invested_capital,
        si.terminal_invested_capital, gw)   # the general D-86a function
    with_gw = SegmentEngine().run(dataclasses.replace(
        si, terminal_invested_capital=si.terminal_invested_capital + gw))
    band = []
    for fade in FADES:
        for start in STARTS:
            if start is None and fade == si.convergence_years:
                continue  # that row is the model itself
            r = SegmentEngine().run(dataclasses.replace(
                si, convergence_years=fade, declared_terminal_return=start))
            band.append({
                "fade_years": fade,
                "starting_return": "earned" if start is None else start,
                "aud_per_share": round(r.value_per_share_aud, 2),
            })
    return {
        "scenario": scenario,
        "fade_years": si.convergence_years,
        "invested_capital_ex_goodwill": round(si.terminal_invested_capital, 0),
        "starting_return_ex_goodwill": round(gr.return_ex_goodwill, 4),
        "invested_capital_incl_goodwill": round(gr.capital_incl_goodwill, 0),
        "starting_return_incl_goodwill": round(gr.return_incl_goodwill, 4),
        "aud_per_share_model": round(base.value_per_share_aud, 2),
        "aud_per_share_incl_goodwill": round(with_gw.value_per_share_aud, 2),
        "sensitivity": band,
    }


def build() -> dict:
    gw = goodwill()
    return {
        "set": "csl_terminal_return_current",
        "decision": "D-86",
        "goodwill_aud_m": gw,
        "scenarios": [size_scenario(s, gw) for s in SCENARIOS],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="print only, change nothing")
    args = ap.parse_args()
    doc = build()
    for s in doc["scenarios"]:
        print(f"{s['scenario']}: return ex-GW {s['starting_return_ex_goodwill']:.4f} "
              f"incl-GW {s['starting_return_incl_goodwill']:.4f} | "
              f"AUD/sh {s['aud_per_share_model']:.2f} -> {s['aud_per_share_incl_goodwill']:.2f}")
    if not args.check:
        SET_PATH.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True),
                            encoding="utf-8")
        print(f"wrote {SET_PATH}")


if __name__ == "__main__":
    main()
