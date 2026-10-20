"""Size every figure the CSL cross-scenario thesis cites (analyses/csl/thesis.md).

Regenerates ``design/methodology/csl_thesis_set.yaml`` from the segment engine and
the data files, so that the thesis quotes committed code (standing rule 4). The
market-gap figures repeat ``csl_market_gap_set.yaml`` (D-92) and the terminal-return
figures repeat ``csl_terminal_return_sets.yaml`` (D-86); both are read, not retyped.
``tests/dcf/test_csl_thesis_set.py`` asserts the set against a fresh run and checks
the thesis text against the set.

    python scripts/size_csl_thesis.py          # rewrite the set
    python scripts/size_csl_thesis.py --check  # print only
"""

from __future__ import annotations

import argparse
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

SET_PATH = ROOT / "design" / "methodology" / "csl_thesis_set.yaml"
GAP_SET = ROOT / "design" / "methodology" / "csl_market_gap_set.yaml"
RETURN_SET = ROOT / "design" / "methodology" / "csl_terminal_return_sets.yaml"

SCENARIOS = [
    "orderly_convergence", "muddle_through", "ai_productivity_lag",
    "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists",
]
CENTRAL = "muddle_through"


def _yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def size_scenario(scenario: str, gap_row: dict, ret_row: dict) -> dict:
    inp = load_inputs(ROOT, scenario, "biopharmaceuticals", "csl")
    si = build_segment_inputs_from_data(inp, scenario)
    r = SegmentEngine().run(si)
    segs = {s.name: s for s in si.segments}
    first, last = r.year_labels[0], r.year_labels[-1]
    return {
        "scenario": scenario,
        "usd_per_share": round(r.value_per_share_usd, 2),
        "aud_per_share": round(r.value_per_share_aud, 2),
        "gap_to_market": gap_row["gap_to_market"],
        "enterprise_value_usdm": round(r.enterprise_value),
        "pv_explicit_usdm": round(r.pv_explicit),
        "pv_terminal_usdm": round(r.pv_terminal),
        "terminal_share_of_ev": round(r.terminal_share_of_ev, 4),
        "net_debt_usdm": round(r.net_debt),
        "equity_value_usdm": round(r.equity_value),
        "explicit_window": f"{first}-{last}",
        "revenue_first_usdm": round(r.group_revenue[0]),
        "revenue_last_usdm": round(r.group_revenue[-1]),
        "ebit_margin_first": round(r.group_ebit[0] / r.group_revenue[0], 4),
        "ebit_margin_last": round(r.group_ebit[-1] / r.group_revenue[-1], 4),
        "terminal_ebit_margin": round(si.terminal_ebit_margin, 4),
        "terminal_growth": round(si.terminal_growth, 4),
        "tax_rate": round(si.tax_rate, 4),
        "fade_years": si.convergence_years,
        "invested_capital_ex_goodwill_usdm": round(si.terminal_invested_capital),
        "earned_starting_return": round(r.terminal_earned_return, 4),
        "starting_return_incl_goodwill": ret_row["starting_return_incl_goodwill"],
        "aud_per_share_incl_goodwill": ret_row["aud_per_share_incl_goodwill"],
        "fade_band_aud_per_share": dict(gap_row["fade_band_aud_per_share"]),
        "behring_growth_first": round(segs["csl_behring"].growth_path[0], 4),
        "behring_growth_last": round(segs["csl_behring"].growth_path[-1], 4),
        "seqirus_growth_last": round(segs["csl_seqirus"].growth_path[-1], 4),
        "vifor_growth_last": round(segs["csl_vifor"].growth_path[-1], 4),
        "margin_uplift_bps": {n: round(segs[n].margin_uplift_cum * 1e4) for n in ("csl_behring", "csl_seqirus", "csl_vifor")},
    }


def build() -> dict:
    gap = _yaml(GAP_SET)
    ret = _yaml(RETURN_SET)
    gap_by = {s["scenario"]: s for s in gap["scenarios"]}
    ret_by = {s["scenario"]: s for s in ret["scenarios"]}
    rows = [size_scenario(s, gap_by[s], ret_by[s]) for s in SCENARIOS]
    by = {r["scenario"]: r for r in rows}
    mt = by[CENTRAL]
    for r in rows:
        r["vs_central"] = round(r["aud_per_share"] / mt["aud_per_share"] - 1.0, 4)
    up = by["orderly_convergence"]["aud_per_share"] - mt["aud_per_share"]
    down = mt["aud_per_share"] - by["stagflation_persists"]["aud_per_share"]

    inp = load_inputs(ROOT, CENTRAL, "biopharmaceuticals", "csl")
    si = build_segment_inputs_from_data(inp, CENTRAL)
    raw = inp["company_raw"]
    stats = raw["company_position"]["share_statistics"]
    fin = _yaml(ROOT / "data" / "financials" / "csl.yaml")
    coe = resolve_normalised_baseline(inp)["cost_of_equity_build"]
    ke = coe["risk_free_rate"] + coe["beta"] * coe["equity_risk_premium"]
    w = segment_wacc_from_data(inp, ke)
    broker_usd = float(fin["market_data"]["consensus_target_usd"])
    price = float(stats["market_reference_price_aud"])
    lowest_band = min(min(r["fade_band_aud_per_share"].values()) for r in rows)
    return {
        "set": "csl_thesis_current",
        "decisions": ["D-44", "D-62", "D-67", "D-71", "D-82", "D-84", "D-86", "D-87", "D-89", "D-92", "D-93"],
        "valuation": {
            "anchor_year": rows[0]["explicit_window"].split("-")[0],
            "explicit_years": si.horizon_years,
            "shares_m": round(si.shares_outstanding_m, 2),
            "restructuring_cash_usdm": round(si.restructuring_cash_to_come),
            "fx_aud_per_usd": round(si.fx_aud_per_usd, 4),
            "wc_change_pct_revenue_change": round(si.wc_change_pct_revenue_change, 4),
            "capex_pct_revenue": round(si.capex_pct_revenue, 4),
            "da_pct_revenue": round(si.da_pct_revenue, 4),
            "terminal_form": si.terminal_form,
        },
        "discount_rate": dict(gap["discount_rate"]),
        "market": {
            "price_aud": price,
            "price_date": str(stats["market_reference_date"]),
            "fifty_two_week_high_aud": float(stats["market_reference_52_week_high"]),
            "broker_target_usd": broker_usd,
            "broker_target_aud": round(broker_usd * si.fx_aud_per_usd, 2),
        },
        "distribution": {
            "upside_aud": round(up, 2),
            "downside_aud": round(down, 2),
            "asymmetry_down_over_up": round(down / up, 2),
            "closest_to_market": gap["closest_to_market"],
            "lowest_in_fade_band_aud": lowest_band,
            "decay_band_years": dict(gap["decay_band_years"]),
        },
        "scenarios": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="print only, change nothing")
    args = ap.parse_args()
    doc = build()
    for s in doc["scenarios"]:
        print(f"{s['scenario']}: USD {s['usd_per_share']:.2f} AUD {s['aud_per_share']:.2f} "
              f"vs MT {s['vs_central']:+.1%} terminal {s['terminal_share_of_ev']:.1%}")  # ssot-allow: display format
    print("asymmetry", doc["distribution"]["asymmetry_down_over_up"])
    if not args.check:
        SET_PATH.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
        print(f"wrote {SET_PATH}")


if __name__ == "__main__":
    main()
