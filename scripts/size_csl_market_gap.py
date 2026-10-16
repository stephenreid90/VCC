"""Size CSL's gap to the 15 June 2026 market price (section 16.3, open item 10, D-92).

Regenerates ``design/methodology/csl_market_gap_set.yaml``. The gap is disclosed,
not reconciled (D-92): each scenario carries the model value, the market price
and date read from ``data/companies/csl.yaml``, the gap as value / price - 1, and
the fade band (15 / 20 / 25 years, D-63 band ends on the D-93 band) from rerunning
the segment engine. The discount rate parts and the earned starting returns are
read from the data and the terminal-return set, not typed.
``design/methodology/csl_market_gap_note_2026-10-16.md`` cites this set and
``tests/dcf/test_csl_market_gap_set.py`` asserts it.

    python scripts/size_csl_market_gap.py          # rewrite the set
    python scripts/size_csl_market_gap.py --check  # print only
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
from vcc_valuations.translator import (  # noqa: E402
    build_segment_inputs_from_data, load_inputs, resolve_normalised_baseline,
    segment_wacc_from_data,
)

SET_PATH = ROOT / "design" / "methodology" / "csl_market_gap_set.yaml"
RETURN_SET = ROOT / "design" / "methodology" / "csl_terminal_return_sets.yaml"

SCENARIOS = [
    "orderly_convergence", "muddle_through", "ai_productivity_lag",
    "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists",
]
FADES = (15.0, 20.0, 25.0)  # D-63 band ends and the D-93 midpoint


def earned_returns() -> dict:
    doc = yaml.safe_load(RETURN_SET.read_text(encoding="utf-8"))
    return {s["scenario"]: s["starting_return_ex_goodwill"] for s in doc["scenarios"]}


def size_scenario(scenario: str, earned: dict) -> dict:
    inp = load_inputs(ROOT, scenario, "biopharmaceuticals", "csl")
    si = build_segment_inputs_from_data(inp, scenario)
    base = SegmentEngine().run(si)
    stats = inp["company_raw"]["company_position"]["share_statistics"]
    price = float(stats["market_reference_price_aud"])
    value = round(base.value_per_share_aud, 2)
    band = {}
    for fade in FADES:
        r = SegmentEngine().run(dataclasses.replace(si, convergence_years=fade))
        band[f"fade_{int(fade)}"] = round(r.value_per_share_aud, 2)
    return {
        "scenario": scenario,
        "aud_per_share_model": value,
        "market_price_aud": price,
        "market_price_date": str(stats["market_reference_date"]),
        "gap_to_market": round(value / price - 1.0, 4),
        "fade_years_model": si.convergence_years,
        "terminal_growth": round(si.terminal_growth, 4),
        "earned_starting_return": earned[scenario],
        "fade_band_aud_per_share": band,
    }


def build() -> dict:
    earned = earned_returns()
    rows = [size_scenario(s, earned) for s in SCENARIOS]
    inp = load_inputs(ROOT, SCENARIOS[0], "biopharmaceuticals", "csl")
    coe = resolve_normalised_baseline(inp).get("cost_of_equity_build") or {}
    ke = coe["risk_free_rate"] + coe["beta"] * coe["equity_risk_premium"]
    w = segment_wacc_from_data(inp, ke)
    closest = min(rows, key=lambda r: abs(r["gap_to_market"]))
    return {
        "set": "csl_market_gap_current",
        "decision": "D-92",
        "discount_rate": {
            "risk_free_rate": round(coe["risk_free_rate"], 4),
            "beta": round(coe["beta"], 4),
            "equity_risk_premium": round(coe["equity_risk_premium"], 4),
            "cost_of_equity": round(w["ke"], 4),
            "cost_of_debt_pretax": round(w["kd"], 4),
            "tax_rate": round(w["tax"], 4),
            "cost_of_debt_after_tax": round(w["kd"] * (1.0 - w["tax"]), 4),
            "net_debt_ebitda": w["net_debt_ebitda"],
            "target_ev_ebitda": w["target_ev_ebitda"],
            "debt_weight": round(w["dv"], 4),
            "wacc": round(w["wacc"], 4),
        },
        "decay_band_years": {"low": 15, "high": 25, "midpoint": 20},
        "closest_to_market": closest["scenario"],
        "scenarios": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="print only, change nothing")
    args = ap.parse_args()
    doc = build()
    for s in doc["scenarios"]:
        print(f"{s['scenario']}: {s['aud_per_share_model']:.2f} vs "
              f"{s['market_price_aud']:.2f} gap {s['gap_to_market']:.4f}")  # ssot-allow: display format
    print("closest:", doc["closest_to_market"])
    if not args.check:
        SET_PATH.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True),
                            encoding="utf-8")
        print(f"wrote {SET_PATH}")


if __name__ == "__main__":
    main()
