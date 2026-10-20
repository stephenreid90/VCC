"""Size the resource-engine valuation sets (standing rule 4).

Writes ``design/methodology/resource_valuation_sets.yaml``: for each resource company,
the six scenario levels on the declared inventory basis, the sized alternatives the
method paper cites (reserves-only life, a declared life extension, WACC +/- 1pp, spot
prices held flat in real terms) and the market-implied gold price. Every figure in
``design/methodology/resource_lifecycle_and_mining_drivers.md`` cites a set from this
file; ``tests/dcf/test_resource_valuation_sets.py`` regenerates and asserts it.

Usage: ``python scripts/size_resource_valuation.py [--write]``. Names no company: the
companies are those whose ``normalised_baseline.engine`` is ``resource``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vcc_valuations.dcf.resource_engine import ResourceEngine  # noqa: E402
from vcc_valuations.resource_translator import build_resource_inputs_from_data  # noqa: E402
from vcc_valuations.translator import load_inputs  # noqa: E402

OUT = ROOT / "design" / "methodology" / "resource_valuation_sets.yaml"
SCENARIOS = [
    "orderly_convergence", "muddle_through", "ai_productivity_lag", "fragmentation",
    "disorderly_climate_crystallisation", "stagflation_persists",
]
BASELINE_SCENARIO = "muddle_through"
WACC_STEP = 0.01  # ssot-allow: the +/-1pp sensitivity step


def resource_companies() -> list:
    out = []
    for p in sorted((ROOT / "data" / "companies").glob("*.yaml")):
        if p.stem.endswith("_documents"):
            continue
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if (d.get("normalised_baseline") or {}).get("engine") == "resource":
            out.append((p.stem, d["company_position"]["industry_archetype"]))
    return out


def run(cid, arch, scenario, **kw):
    inp = load_inputs(ROOT, scenario, arch, cid)
    return ResourceEngine().run(build_resource_inputs_from_data(inp, scenario, **kw)), inp


def market_implied_gold_scale(cid, arch, scenario, target, lo=0.2, hi=5.0, tol=1e-6):  # ssot-allow: search bounds
    """The multiple of the scenario's whole gold path that reproduces ``target``."""
    for _ in range(200):
        mid = (lo + hi) / 2.0
        v = run(cid, arch, scenario, gold_scale=mid)[0].value_per_share
        if v < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2.0


def size() -> dict:
    sets = {}
    for cid, arch in resource_companies():
        levels, shares, life = {}, {}, {}
        for s in SCENARIOS:
            r, inp = run(cid, arch, s)
            levels[s] = round(r.value_per_share, 4)
            shares[s] = round(r.terminal_share_of_ev, 4)
        base, inp = run(cid, arch, BASELINE_SCENARIO)
        fin = inp["financials"]
        nb = inp["company_raw"]["normalised_baseline"]
        spot = fin["spot_reference"]
        flat = {"gold_usd_oz": spot["gold_usd_oz"], "aud_usd": spot["aud_usd"],
                "copper_usd_t": spot["copper_usd_lb_sep_qtr_achieved"] * 2204.62262}  # ssot-allow: lb per tonne
        sens = {}
        for basis in nb["inventory"]["sensitivity_bases"]:
            sens[f"inventory_{basis}"] = {s: round(run(cid, arch, s, basis=basis)[0].value_per_share, 4)
                                          for s in SCENARIOS}
        w = base.wacc
        sens["wacc_minus_1pp"] = round(run(cid, arch, BASELINE_SCENARIO, wacc_override=w - WACC_STEP)[0].value_per_share, 4)
        sens["wacc_plus_1pp"] = round(run(cid, arch, BASELINE_SCENARIO, wacc_override=w + WACC_STEP)[0].value_per_share, 4)
        sens["spot_flat_real"] = round(run(cid, arch, BASELINE_SCENARIO, flat_real=flat)[0].value_per_share, 4)
        sens["spot_flat_real_life_extension"] = round(
            run(cid, arch, BASELINE_SCENARIO, flat_real=flat, basis="life_extension")[0].value_per_share, 4)
        price = fin["market_data"]["price_aud"]
        k = market_implied_gold_scale(cid, arch, BASELINE_SCENARIO, price)
        ref = inp["scenario"]
        y10 = [p.value for mv in ref.macro_variables if mv.variable == "gold_price_usd_real"
               for p in mv.time_series if p.year == 10][0]
        sets[cid] = {
            "status": "current",
            "basis": nb["inventory"]["basis"],
            "wacc": round(w, 6),
            "levels": levels,
            "terminal_shares": shares,
            "life_years": round(base.life_years, 4),
            "mine_last_period": base.mine_last_period,
            "baseline_detail": {
                "scenario": BASELINE_SCENARIO,
                "enterprise_value": round(base.enterprise_value, 1),
                "pv_explicit": round(base.pv_explicit, 1),
                "pv_terminal": round(base.pv_terminal, 1),
                "net_debt_at_valuation": round(base.net_debt_at_valuation, 1),
                "adjustments": round(base.equity_bridge_adjustments_net, 1),
                "leases": round(base.lease_liabilities, 1),
                "y1_fcff": round(base.fcff[1], 1),
                "y1_ebitda": round(base.ebitda[1], 1),
                "y1_gold_aud_oz": round(base.gold_aud_oz[1], 1),
            },
            "sensitivities": sens,
            "market": {
                "price": price,
                "gap_to_market_baseline": round(base.value_per_share / price - 1.0, 4),
                "implied_gold_scale": round(k, 4),
                "implied_real_gold_y10_usd": round(y10 * k, 0),
            },
        }
    return {"generated_by": "scripts/size_resource_valuation.py", "sets": sets}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    data = size()
    text = yaml.safe_dump(data, sort_keys=False)
    if a.write:
        OUT.write_text("# Generated. Do not hand-edit; rerun the script.\n" + text, encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
