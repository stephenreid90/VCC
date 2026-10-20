"""Build the data file behind the resource-company review page (standing rule 4).

For each company whose ``normalised_baseline.engine`` is ``resource``, runs the resource
engine for every scenario and writes ``ui_prototypes/resource_review/<company>_review_data.json``:
the six values, the price paths each scenario carries (with the written basis from the
scenario file), the year-by-year cash flow, mine closures, the sized sensitivities, and a
grid of values across multiples of each scenario's gold path. The page reads this file and
never recomputes anything (D-23: no engine port in the browser).

Usage: ``python scripts/build_resource_review_data.py``. Names no company.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from size_resource_valuation import SCENARIOS, market_implied_gold_scale, resource_companies, run  # noqa: E402
from vcc_valuations.resource_translator import (  # noqa: E402
    build_resource_inputs_from_data, price_and_cost_paths, resource_wacc_from_data,
)

OUT_DIR = ROOT / "ui_prototypes" / "resource_review"
GOLD_SCALES = [round(0.70 + 0.05 * i, 2) for i in range(27)]  # ssot-allow: 0.70x to 2.00x grid
PRICE_VARS = ["gold_price_usd_real", "copper_price_usd_real", "aud_usd"]
LB_PER_T = 2204.62262  # ssot-allow: unit conversion


def scenario_meta(sid: str) -> dict:
    """Display name, the written basis for each price series, and its typed anchor points."""
    text = (ROOT / "data" / "scenarios" / f"{sid}.yaml").read_text(encoding="utf-8")
    import yaml
    d = yaml.safe_load(text)
    name = d.get("name") or d.get("scenario_name") or sid.replace("_", " ").title().replace("Ai ", "AI ")
    out = {"id": sid, "name": name, "series": {}}
    lines = text.splitlines()
    for var in PRICE_VARS + ["cpi_inflation_advanced", "policy_rate_real_advanced"]:
        basis, anchor = [], None
        for i, ln in enumerate(lines):
            if re.match(rf"\s*- variable: {var}\s*$", ln):
                j = i + 1
                while j < len(lines) and "time_series:" not in lines[j]:
                    c = lines[j].strip()
                    if c.startswith("#"):
                        c = c.lstrip("#").strip()
                        if c.startswith("Basis:"):
                            basis.append(c[len("Basis:"):].strip())
                        elif basis and not c.startswith(("Year 0", "Scenario development")):
                            basis.append(c)
                        if c.startswith("Year 0 reference:"):
                            anchor = c[len("Year 0 reference:"):].strip()
                    j += 1
                break
        pts = []
        for blk in _walk(d):
            if blk.get("variable") == var:
                pts = [[p["year"], p["value"]] for p in blk.get("time_series", [])]
                break
        out["series"][var] = {"basis": " ".join(basis), "anchor": anchor, "points": pts}
    return out


def _walk(o):
    if isinstance(o, dict):
        if "variable" in o:
            yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def r1(xs):
    return [round(x, 1) for x in xs]


def build(cid: str, arch: str) -> dict:
    base, inp = run(cid, arch, "muddle_through")
    fin = inp["financials"]
    nb = inp["company_raw"]["normalised_baseline"]
    spot = fin["spot_reference"]
    flat = {"gold_usd_oz": spot["gold_usd_oz"], "aud_usd": spot["aud_usd"],
            "copper_usd_t": spot["copper_usd_lb_sep_qtr_achieved"] * LB_PER_T}
    wb = resource_wacc_from_data(inp)
    bases = [nb["inventory"]["basis"]] + list(nb["inventory"]["sensitivity_bases"])
    vd = str(nb["valuation_date"])
    fy0 = int(vd[2:4]) + (1 if int(vd[5:7]) > 6 else 0)  # June year-end: Oct 2026 sits in FY27

    scen = []
    for s in SCENARIOS:
        r, sinp = run(cid, arch, s)
        ei = build_resource_inputs_from_data(sinp, s)
        n = len(r.fcff)
        paths = price_and_cost_paths(sinp, s, n)
        mines = {m.name: m for m in ei.mines}
        closures = []
        for name, last in r.mine_last_period.items():
            m = mines[name]
            closures.append({"mine": name, "last_period": last, "last_fy": f"FY{fy0 + last}",
                             "start_period": m.start_period, "gold_koz_pa": round(m.gold_koz_pa, 1),
                             "copper_kt_pa": round(m.copper_kt_pa, 2), "aisc_aud_oz": round(m.aisc_aud_oz, 0)})
        grid = {}
        for b in bases:
            grid[b] = [round(run(cid, arch, s, basis=b, gold_scale=k)[0].value_per_share, 4) for k in GOLD_SCALES]
        flat_r = run(cid, arch, s, flat_real=flat)[0]
        scen.append({
            **scenario_meta(s),
            "value_per_share": round(r.value_per_share, 4),
            "enterprise_value": round(r.enterprise_value, 1),
            "pv_explicit": round(r.pv_explicit, 1),
            "pv_terminal": round(r.pv_terminal, 1),
            "terminal_share": round(r.terminal_share_of_ev, 4),
            "equity_value": round(r.equity_value, 1),
            "gap_to_market": round(r.discount_to_market, 4),
            "life_years": round(r.life_years, 2),
            "implied_gold_scale": round(market_implied_gold_scale(cid, arch, s, fin["market_data"]["price_aud"]), 4),
            "closures": closures,
            "sensitivities": {
                "reserves": grid["reserves"][GOLD_SCALES.index(1.0)],
                "life_extension": grid["life_extension"][GOLD_SCALES.index(1.0)],
                "spot_flat_real": round(flat_r.value_per_share, 4),
                "spot_flat_real_life_extension": round(run(cid, arch, s, flat_real=flat, basis="life_extension")[0].value_per_share, 4),
                "wacc_minus_1pp": round(run(cid, arch, s, wacc_override=r.wacc - 0.01)[0].value_per_share, 4),  # ssot-allow: 1pp step
                "wacc_plus_1pp": round(run(cid, arch, s, wacc_override=r.wacc + 0.01)[0].value_per_share, 4),  # ssot-allow: 1pp step
            },
            "gold_scale_grid": grid,
            "years": {
                "label": [("FY%d stub" % fy0) if t == 0 else "FY%d" % (fy0 + t) for t in range(n)],
                "period": r.period_labels,
                "gold_usd_real": [round(paths["gold_aud_oz"][t] * paths["aud_usd"][t] / paths["cpi_index"][t], 0) for t in range(n)],
                "copper_usd_real": [round(paths["copper_aud_t"][t] * paths["aud_usd"][t] / paths["cpi_index"][t], 0) for t in range(n)],
                "aud_usd": [round(x, 4) for x in paths["aud_usd"]],
                "gold_aud_nominal": r1(r.gold_aud_oz),
                "copper_aud_nominal": r1(r.copper_aud_t),
                "cost_index": [round(x, 4) for x in paths["cost_index"]],
                "gold_koz": r1(r.gold_koz), "copper_kt": [round(x, 2) for x in r.copper_kt],
                "revenue": r1(r.revenue), "royalty": r1(r.royalty), "operating_cost": r1(r.operating_cost),
                "exploration_and_corporate": r1(r.exploration_and_corporate), "ebitda": r1(r.ebitda),
                "tax": r1(r.tax), "capex": r1(r.capex), "delta_wc": r1(r.delta_wc), "fcff": r1(r.fcff),
                "discount_factor": [round(x, 4) for x in r.discount_factors], "pv_fcff": r1(r.pv_fcff),
            },
        })

    return {
        "generated_by": "scripts/build_resource_review_data.py",
        "engine_commit": _commit(),
        "company_id": cid,
        "company_name": inp["company_raw"]["company_position"]["name"],
        "ticker": inp["company_raw"]["company_position"].get("ticker", cid.upper()),
        "archetype": arch,
        "valuation_date": str(nb["valuation_date"]),
        "market_price_aud": fin["market_data"]["price_aud"],
        "shares_m": round(fin["share_statistics"]["shares_outstanding"], 1),
        "horizon_years": base.horizon_years,
        "inventory_basis": nb["inventory"]["basis"],
        "inventory_bases": bases,
        "spot": {"gold_usd_oz": flat["gold_usd_oz"], "aud_usd": flat["aud_usd"],
                 "copper_usd_t": round(flat["copper_usd_t"], 0)},
        "wacc": {"wacc": round(wb.wacc, 6), "risk_free": wb.risk_free_rate, "beta": wb.beta,
                 "erp": wb.equity_risk_premium, "cost_of_equity": round(wb.cost_of_equity, 6),
                 "kd_pretax": round(wb.cost_of_debt_pretax, 6), "tax": wb.tax_rate,
                 "equity_mv": round(wb.equity_market_value, 1), "debt_mv": round(wb.debt_market_value, 1)},
        "bridge": {"net_debt": round(base.net_debt_at_valuation, 1),
                   "rehabilitation_and_other": round(base.equity_bridge_adjustments_net, 1),
                   "leases": round(base.lease_liabilities, 1)},
        "gold_scales": GOLD_SCALES,
        "scenarios": scen,
    }


def flat_tables(d: dict) -> dict:
    """The same content as row tables, one per page source (the review page reads these)."""
    sc, paths, cf, grid, basis = [], [], [], [], []
    for order, s in enumerate(d["scenarios"]):
        y = s["years"]
        y10 = {v: dict(map(tuple, s["series"][v]["points"])).get(10) for v in PRICE_VARS}
        sc.append({"scenario": s["id"], "name": s["name"], "order": order,
                   "value_per_share": s["value_per_share"], "gap_to_market": s["gap_to_market"],
                   "enterprise_value": s["enterprise_value"], "pv_explicit": s["pv_explicit"],
                   "pv_run_off": s["pv_terminal"], "run_off_share": s["terminal_share"],
                   "equity_value": s["equity_value"], "life_years": s["life_years"],
                   "implied_gold_scale": s["implied_gold_scale"],
                   **{k: v for k, v in s["sensitivities"].items()},
                   "gold_y10_usd_real": y10["gold_price_usd_real"],
                   "copper_y10_usd_real": y10["copper_price_usd_real"], "aud_usd_y10": y10["aud_usd"]})
        for t, fy in enumerate(y["label"]):
            phase = "stub" if t == 0 else ("explicit" if t <= d["horizon_years"] else "run_off")
            paths.append({"scenario": s["id"], "fy": fy, "t": t, "gold_usd_real": y["gold_usd_real"][t],
                          "copper_usd_real": y["copper_usd_real"][t], "aud_usd": y["aud_usd"][t],
                          "gold_aud_nominal": y["gold_aud_nominal"][t],
                          "copper_aud_nominal": y["copper_aud_nominal"][t], "cost_index": y["cost_index"][t]})
            cf.append({"scenario": s["id"], "fy": fy, "t": t, "phase": phase,
                       **{k: y[k][t] for k in ("gold_koz", "copper_kt", "revenue", "royalty", "operating_cost",
                                                "exploration_and_corporate", "ebitda", "tax", "capex",
                                                "delta_wc", "fcff", "discount_factor", "pv_fcff")}})
        for b, vals in s["gold_scale_grid"].items():
            for k, v in zip(d["gold_scales"], vals):
                grid.append({"scenario": s["id"], "basis": b, "gold_scale": k, "value_per_share": v})
        for v in PRICE_VARS:
            ser = s["series"][v]
            pts = dict(map(tuple, ser["points"]))
            basis.append({"scenario": s["id"], "name": s["name"], "series": v, "basis": ser["basis"], "anchor": ser["anchor"] or "",
                          **{f"y{k}": pts.get(k) for k in (1, 3, 5, 7, 10)}})
    mines = [{"mine": c["mine"], "first_fy": d["scenarios"][0]["years"]["label"][c["start_period"]].split()[0],
              "last_fy": c["last_fy"], "start_period": c["start_period"], "last_period": c["last_period"],
              "gold_koz_pa": c["gold_koz_pa"], "copper_kt_pa": c["copper_kt_pa"], "aisc_aud_oz": c["aisc_aud_oz"]}
             for c in d["scenarios"][1]["closures"]]
    w, b = d["wacc"], d["bridge"]
    inputs = [
        {"item": "market_price", "label": "Market reference price", "value": d["market_price_aud"], "unit": "A$/share", "basis": "D-94"},
        {"item": "shares", "label": "Shares on issue", "value": d["shares_m"], "unit": "m", "basis": "30 Sep 2026 quarterly (D-100)"},  # ssot-allow: decision id
        {"item": "spot_gold", "label": "Spot gold", "value": d["spot"]["gold_usd_oz"], "unit": "US$/oz", "basis": "year 0 reference"},
        {"item": "spot_copper", "label": "Spot copper", "value": d["spot"]["copper_usd_t"], "unit": "US$/t", "basis": "Sep quarter achieved"},
        {"item": "spot_aud_usd", "label": "AUD/USD", "value": d["spot"]["aud_usd"], "unit": "US$ per A$", "basis": "year 0 reference"},
        {"item": "risk_free", "label": "Risk-free rate", "value": w["risk_free"], "unit": "pct", "basis": "10-year bond, 14 Oct 2026 (D-101)"},
        {"item": "beta", "label": "Beta", "value": w["beta"], "unit": "x", "basis": "peer judgement (D-101)"},
        {"item": "erp", "label": "Equity risk premium", "value": w["erp"], "unit": "pct", "basis": "house"},
        {"item": "cost_of_equity", "label": "Cost of equity", "value": w["cost_of_equity"], "unit": "pct", "basis": "Rf + beta x ERP"},
        {"item": "kd_pretax", "label": "Cost of debt, pre-tax", "value": w["kd_pretax"], "unit": "pct", "basis": "Rf + 150bp"},
        {"item": "equity_mv", "label": "Equity, market value", "value": w["equity_mv"], "unit": "A$m", "basis": "spot weights (D-55)"},
        {"item": "debt_mv", "label": "Debt", "value": w["debt_mv"], "unit": "A$m", "basis": "USPP at swapped value"},
        {"item": "wacc", "label": "WACC", "value": w["wacc"], "unit": "pct", "basis": "one rate, all periods (D-01)"},
        {"item": "net_debt", "label": "Net debt at valuation", "value": b["net_debt"], "unit": "A$m", "basis": "net cash at 30 Sep less the final dividend paid 2 Oct (D-100)"},  # ssot-allow: decision id
        {"item": "rehabilitation", "label": "Rehabilitation", "value": b["rehabilitation_and_other"], "unit": "A$m", "basis": "30 Jun 2025 (D-100)"},  # ssot-allow: decision id
        {"item": "leases", "label": "Leases", "value": b["leases"], "unit": "A$m", "basis": "30 Jun 2025 (D-100)"},  # ssot-allow: decision id
    ]
    return {"scenarios": sc, "price_paths": paths, "cash_flow": cf, "gold_grid": grid,
            "price_basis": basis, "mines": mines, "model_inputs": inputs}


def _commit() -> str:
    try:
        import subprocess
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for cid, arch in resource_companies():
        p = OUT_DIR / f"{cid}_review_data.json"
        d = build(cid, arch)
        p.write_text(json.dumps(d, indent=1), encoding="utf-8")
        print(f"wrote {p.relative_to(ROOT)}")
        sub = OUT_DIR / cid
        sub.mkdir(exist_ok=True)
        for name, rows in flat_tables(d).items():
            q = sub / f"{name}.json"
            q.write_text(json.dumps(rows), encoding="utf-8")
            print(f"wrote {q.relative_to(ROOT)} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
