"""Check the resource engine against EVN's own stated figures (EVN review 20 Oct 2026, §3 item 2).

Two checks, printed as a reconciliation. Nothing here tunes the model; the gaps are
reported and explained in ``design/methodology/evn_engine_vs_company_2026-10-20.md``,
which cites this script's output (CLAUDE.md standing rule 4).

(a) Gold sensitivity. Add GOLD_STEP_AUD (A$/oz) to every period of the Muddle Through gold path and
    report the change in the engine's FY27 cash flow, against the company's "FY27 cash flow
    sensitivities (A$M) ... Gold price (+/- $100/oz) 65-70" (FY26 results presentation,  # ssot-allow: quoted company wording
    slide 14).
(b) Backcast. Run the engine with gold and copper held at FY26 achieved prices
    (``royalties_fy26`` in the financials file) and compare EBITDA, net mine cash flow and
    group cash flow with the FY26 actuals. FY26 mine-by-mine volumes and costs are not held
    in the data files, so the volumes, costs and capital are the FY27 guidance midpoints.

Period convention. The valuation date (20 Oct 2026) falls inside FY27, so the engine's
period 0 is the FY27 stub (stub_years of a year) and "Y1" is FY28. FY27 figures here are
the stub divided by stub_years: every period-0 flow scales with the stub fraction, the
period-0 cost index is 1.0 (guidance dollars) and working-capital change is nil, so the
annualised stub is exactly "FY27 guidance at the given prices".

(c) FY26 actuals rerun (``--fy26-actuals``). Rebuild the period-0 inputs from
    ``data/financials/actuals/evn_fy26_actuals.yaml`` (FY26 Appendix 4E and financial report): each
    mine's FY26 gold and copper produced, AISC, sustaining and major capital, Mt Rawdon added,
    site exploration nil (the company reports it as a separate Exploration segment), FY26
    expensed exploration and corporate overheads, group D&A, FY26 achieved prices, one full year.
    Compare EBITDA, net mine cash flow and group cash flow with the stated FY26 figures, group
    and mine by mine. Inputs the report does not hold (royalty rate, stream cash terms, working
    capital) stay as the data files have them, and are named in the output.

Usage: ``python scripts/check_resource_engine_vs_company.py`` (checks a and b), or
``python scripts/check_resource_engine_vs_company.py --fy26-actuals`` (check c).
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vcc_valuations.dcf.resource_engine import MineInputs, ResourceEngine  # noqa: E402
from vcc_valuations.resource_translator import build_resource_inputs_from_data  # noqa: E402
from vcc_valuations.translator import load_inputs  # noqa: E402

CID = "evn"
SCENARIO = "muddle_through"
GOLD_STEP_AUD = 100.0  # ssot-allow: the company's stated sensitivity step, A$/oz
_THOUSANDS_PER_MILLION = 1.0e3  # ssot-allow: unit conversion

# Company-stated check figures, A$m. Quoted from the source documents, not model inputs.
COMPANY = {  # ssot-allow: company-stated check figures, quoted in the findings note
    "gold_sens_low": 65.0, "gold_sens_high": 70.0,      # FYP slide 14
    "ebitda": 3171.0,                                   # FYR p2 "Underlying EBITDA $M 3,171"
    "operating_mine_cf": 3394.0,                        # FYR p2
    "net_mine_cf": 2079.0,                              # FYR p2
    "group_cf": 1389.0,                                 # FYR p2, before dividends, debt, M&A
    # June 2026 quarterly, group cash flow table (FY26 column)
    "sustaining": -239.0, "major_capital": -850.0, "non_operational": -118.0,
    "stream_delivery": -108.0, "corporate_discovery": -144.0, "net_interest": -43.0,
    "other_income": 14.0, "working_capital": -109.0, "tax_paid": -409.0,
    "aisc_fy26": 1717.0,                                # FYR p2 "AISC $/oz 1,717"
    "aisc_fy27_low": 1795.0, "aisc_fy27_high": 1995.0,  # FYR p4 group guidance
    "mt_rawdon_omcf": 44.0,                             # JQ Appendix 2, closed Sep qtr FY27
}


def _inputs(scenario: str = SCENARIO):
    d = yaml.safe_load((ROOT / "data" / "companies" / f"{CID}.yaml").read_text(encoding="utf-8"))
    arch = d["company_position"]["industry_archetype"]
    inp = load_inputs(ROOT, scenario, arch, CID)
    return inp, build_resource_inputs_from_data(inp, scenario)


def _period(r, ri, t: int, annualise: bool) -> dict:
    """One period's lines, A$m. ``annualise`` divides the stub by its fraction."""
    k = ri.stub_years if (annualise and t == 0) else 1.0
    gold_koz = r.gold_koz[t]
    corporate = (ri.corporate_cost_aud_oz * gold_koz / _THOUSANDS_PER_MILLION
                 + ri.greenfields_exploration * (ri.stub_years if t == 0 else 1.0)) * ri.cost_index[t]
    out = {
        "gold_koz": gold_koz, "copper_kt": r.copper_kt[t],
        "gold_aud_oz": r.gold_aud_oz[t], "copper_aud_t": r.copper_aud_t[t],
        "revenue": r.revenue[t], "royalty": -r.royalty[t], "operating_cost": -r.operating_cost[t],
        "mine_exploration": -(r.exploration_and_corporate[t] - corporate),
        "corporate_and_greenfields": -corporate,
        "ebitda": r.ebitda[t], "tax": -r.tax[t], "capex": -r.capex[t], "delta_wc": -r.delta_wc[t],
        "fcff": r.fcff[t],
    }
    # Engine analogues of the company's mine-level measures (before corporate, tax, WC).
    out["operating_mine_cf"] = out["revenue"] + out["royalty"] + out["operating_cost"] + out["mine_exploration"]
    out["net_mine_cf"] = out["operating_mine_cf"] + out["capex"]
    return {key: (v / k if key not in ("gold_aud_oz", "copper_aud_t") else v) for key, v in out.items()}


def _capex_split(ri) -> dict:
    """FY27 full-year capital by type at guidance (cost index 1.0), A$m."""
    sus = sum(m.sustaining_capex for m in ri.mines if m.start_period == 0)
    dev = sum(m.mine_development for m in ri.mines if m.start_period == 0)
    proj = sum(m.project_capex[0] for m in ri.mines if m.project_capex and m.start_period == 0)
    return {"sustaining": sus, "mine_development": dev, "major_project": proj}


def check_gold_sensitivity() -> dict:
    inp, ri = _inputs()
    eng = ResourceEngine()
    base = eng.run(ri)
    bumped = eng.run(dataclasses.replace(ri, gold_aud_oz=[p + GOLD_STEP_AUD for p in ri.gold_aud_oz]))
    out = {}
    for label, t in (("FY27 (stub, annualised)", 0), ("FY28 (engine Y1)", 1)):
        b, u = _period(base, ri, t, True), _period(bumped, ri, t, True)
        out[label] = {"base": b, "delta": {k: u[k] - b[k] for k in b}}
    m_np = [m for m in ri.mines if m.stream_delivered_fraction > 0]
    stream_koz = sum(m.gold_koz_pa * m.stream_delivered_fraction * (1 - m.stream_cash_fraction_of_spot)
                     for m in m_np)
    out["context"] = {"royalty_rate": ri.royalty_rate, "tax_rate": ri.tax_rate,
                      "fy27_gold_koz": sum(m.gold_koz_pa for m in ri.mines if m.start_period == 0),
                      "stream_haircut_koz": stream_koz}
    return out


def check_backcast() -> dict:
    inp, ri = _inputs()
    ry = inp["financials"]["royalties_fy26"]
    n = len(ri.gold_aud_oz)
    ri_fy26 = dataclasses.replace(ri, gold_aud_oz=[ry["achieved_gold_aud_oz"]] * n,
                                  copper_aud_t=[ry["achieved_copper_aud_t"]] * n)
    r = ResourceEngine().run(ri_fy26)
    p = _period(r, ri_fy26, 0, True)
    cs = _capex_split(ri_fy26)
    koz = p["gold_koz"]
    corp_aisc = ri.corporate_cost_aud_oz * koz / _THOUSANDS_PER_MILLION
    cu_rev = p["copper_kt"] * p["copper_aud_t"] / _THOUSANDS_PER_MILLION
    # AISC on the WGC definition: site cash cost + royalty + sustaining + corporate G&A,
    # less the copper credit, per gold ounce (stream and exploration excluded).
    aisc = (-p["operating_cost"] - p["royalty"] + cs["sustaining"] + corp_aisc - cu_rev) * _THOUSANDS_PER_MILLION / koz
    stream_koz = sum(m.gold_koz_pa * m.stream_delivered_fraction * (1 - m.stream_cash_fraction_of_spot)
                     for m in ri.mines if m.start_period == 0)
    return {"engine": p, "capex_split": cs, "engine_aisc": aisc,
            "stream_value": stream_koz * p["gold_aud_oz"] / _THOUSANDS_PER_MILLION,
            "fy26_sold_koz": ry["gold_sold_oz"] / _THOUSANDS_PER_MILLION,
            "fy26_copper_kt": ry["copper_produced_t"] / _THOUSANDS_PER_MILLION}


FY26_FILE = ROOT / "data" / "financials" / "actuals" / f"{CID}_fy26_actuals.yaml"
FY26_MINES = ("cowal", "ernest_henry", "northparkes", "mungari", "red_lake", "mt_rawdon")


def _v(node) -> float:
    """A cited figure from the actuals file; refuses a NOT_FOUND line."""
    if not isinstance(node, dict) or "value" not in node:
        raise KeyError(f"figure not in the FY26 report: {node!r}")
    return float(node["value"])


def _m(node) -> float:
    """A cited A$'000 figure, in A$m."""
    return _v(node) / _THOUSANDS_PER_MILLION


def _fy26_inputs(ri, a: dict):
    """Period-0 engine inputs rebuilt from FY26 actuals. Returns (inputs, notes)."""
    px = a["prices"]
    gold_px, cu_px = _v(px["gold_achieved_aud_oz"]), _v(px["copper_achieved_aud_t"])
    by_name = {m.name: m for m in ri.mines}
    gold_total_koz = _v(a["group_volumes"]["gold_produced_oz"]) / _THOUSANDS_PER_MILLION
    # Group D&A spread evenly per ounce: the report has no mine split, and the engine's tax
    # depends only on the group total, so this reproduces FY26 D&A exactly.
    da_oz = _m(a["group_pnl"]["d_and_a"]) * _THOUSANDS_PER_MILLION / gold_total_koz
    mines, kept = [], []
    for name in FY26_MINES:
        x = a["mines"][name]
        base = by_name.get(name)
        stream_f = (_v(x["stream_delivered_fraction_of_gold_produced"])
                    if "stream_delivered_fraction_of_gold_produced" in x else 0.0)
        cash_f = base.stream_cash_fraction_of_spot if (base and stream_f) else 0.0
        if stream_f:
            kept.append(f"{name} stream cash price {cash_f:.0%} of spot (data file; not in the report)")
        g = _v(x["gold_produced_oz"]) / _THOUSANDS_PER_MILLION
        c = _v(x["copper_produced_t"]) / _THOUSANDS_PER_MILLION
        mines.append(MineInputs(
            name=name, gold_koz_pa=g, copper_kt_pa=c,
            inventory_gold_koz=g * 2, inventory_copper_kt=c * 2,  # one period only; never binds
            aisc_aud_oz=_v(x["aisc_aud_oz"]), sustaining_capex=_m(x["sustaining_capital"]),
            mine_development=_m(x["major_capital"]), exploration=0.0, da_aud_oz=da_oz,
            project_capex=[], stream_delivered_fraction=stream_f,
            stream_cash_fraction_of_spot=cash_f, start_period=0))
    corp_oz = _m(a["group_pnl"]["corporate_overheads"]) * _THOUSANDS_PER_MILLION / gold_total_koz
    kept.append(f"royalty rate {ri.royalty_rate:.4f} of revenue (data file; the report gives only the group total)")
    kept.append(f"tax rate {ri.tax_rate:.2f} on EBITDA less D&A (accrual; the report gives cash tax paid)")
    fy = dataclasses.replace(
        ri, stub_years=1.0, mines=mines, gold_aud_oz=[gold_px], copper_aud_t=[cu_px], cost_index=[1.0],
        guidance_gold_aud_oz=gold_px, guidance_copper_aud_t=cu_px, corporate_cost_aud_oz=corp_oz,
        greenfields_exploration=_m(a["exploration"]["expensed"]))
    return fy, kept


def _first(r) -> dict:
    return {k: getattr(r, k)[0] for k in ("revenue", "royalty", "operating_cost", "exploration_and_corporate",
                                          "ebitda", "da", "tax", "capex", "delta_wc", "fcff")}


def check_fy26_actuals() -> dict:
    a = yaml.safe_load(FY26_FILE.read_text(encoding="utf-8"))
    _, ri = _inputs()
    fy, kept = _fy26_inputs(ri, a)
    eng = ResourceEngine()
    group = _first(eng.run(fy))
    per_mine = {}
    for m in fy.mines:
        solo = dataclasses.replace(fy, mines=[m], corporate_cost_aud_oz=0.0, greenfields_exploration=0.0)
        e = _first(eng.run(solo))
        x = a["mines"][m.name]
        omcf = e["revenue"] - e["royalty"] - e["operating_cost"]
        per_mine[m.name] = {
            "engine": {"revenue": e["revenue"], "ebitda": e["ebitda"], "omcf": omcf,
                       "nmcf": omcf - e["capex"]},
            "company": {"revenue": _m(x["revenue"]), "ebitda": _m(x["segment_ebitda"]),
                        "omcf": _m(x["operating_mine_cash_flow"]),
                        "nmcf_pre_nonop": _m(x["net_mine_cash_flow"]) + _m(x["non_operational_costs"]),
                        "non_op": -_m(x["non_operational_costs"]), "nmcf": _m(x["net_mine_cash_flow"])}}
    return {"actuals": a, "inputs": fy, "kept": kept, "group": group, "mines": per_mine}


def _row(label: str, engine: float, company: float | None = None) -> str:
    if company is None:
        return f"  {label:<44}{engine:>10.1f}"
    return f"  {label:<44}{engine:>10.1f}{company:>10.1f}{engine - company:>10.1f}"


def main_fy26() -> int:
    res = check_fy26_actuals()
    a, fy, g = res["actuals"], res["inputs"], res["group"]
    gc, gp, tx = a["group_cash_flow"], a["group_pnl"], a["tax"]
    print("(c) FY26 ACTUALS RERUN: engine on FY26 mine volumes, AISC, capital and achieved prices "
          f"(gold A${fy.gold_aud_oz[0]:,.0f}/oz, copper A${fy.copper_aud_t[0]:,.0f}/t), one full year, A$m")
    print(f"  source: {FY26_FILE.relative_to(ROOT).as_posix()}")
    print(f"  inputs kept from the data files: {'; '.join(res['kept'])}")
    print(f"  site exploration per mine 0.0 (Exploration is its own segment); expensed exploration "
          f"{fy.greenfields_exploration:.1f}; corporate {fy.corporate_cost_aud_oz:.1f} A$/oz")
    print()
    print(f"  {'mine':<14}{'revenue':>9}{'co.':>9}{'EBITDA':>9}{'co.':>9}{'OMCF':>9}{'co.':>9}"
          f"{'NMCF*':>9}{'co.*':>9}{'non-op':>9}")
    for name, d in res["mines"].items():
        e, c = d["engine"], d["company"]
        print(f"  {name:<14}{e['revenue']:>9.1f}{c['revenue']:>9.1f}{e['ebitda']:>9.1f}{c['ebitda']:>9.1f}"
              f"{e['omcf']:>9.1f}{c['omcf']:>9.1f}{e['nmcf']:>9.1f}{c['nmcf_pre_nonop']:>9.1f}{c['non_op']:>9.1f}")
    print("  * NMCF before non-operational costs (company NMCF + its non-op line); "
          "company EBITDA is statutory segment EBITDA")
    print()
    omcf_e = sum(d["engine"]["omcf"] for d in res["mines"].values())
    nmcf_e = sum(d["engine"]["nmcf"] for d in res["mines"].values())
    non_op = -_m(gc["non_operational_cash_costs"])
    e_capex_expl = -_m(a["exploration"]["capitalised_additions"])
    corp_cap = -_m(a["segments_other"]["corporate"]["sustaining_capital"])
    print(f"  {'':<44}{'engine':>10}{'company':>10}{'gap':>10}")
    print(_row("revenue", g["revenue"], _m(gp["revenue"])))
    print(_row("royalty (co.: royalty and other selling)", -g["royalty"], -_m(gp["royalty_and_other_selling_costs"])))
    print(_row("corporate + expensed exploration", -g["exploration_and_corporate"],
               -_m(a["exploration"]["in_underlying_ebitda_line"])))
    print(_row("EBITDA (co.: underlying)", g["ebitda"], COMPANY["ebitda"]))
    print(_row("operating mine cash flow", omcf_e, _m(gc["operating_mine_cash_flow"])))
    print(_row("non-operational costs (engine: none)", 0.0, non_op))
    print(_row("net mine cash flow", nmcf_e, COMPANY["net_mine_cf"]))
    print(_row("tax (co.: income taxes paid)", -g["tax"], -_m(tx["income_taxes_paid"])))
    print(_row("tax (co.: income tax expense, accrual)", -g["tax"], -_m(tx["income_tax_expense"])))
    print(_row("group cash flow (engine: FCFF)", g["fcff"], COMPANY["group_cf"]))
    print()
    print("  items the engine has no input for (FY26, A$m, from the actuals file):")
    print(_row("capitalised exploration (E&E additions)", e_capex_expl))
    print(_row("corporate capital", corp_cap))
    print(_row("working capital change (Note 6(a))",
               sum(_m(v) for v in a["working_capital_change"].values())))
    print(_row("D&A used for engine tax (group, p57)", -g["da"]))
    wc = sum(_m(v) for v in a["working_capital_change"].values())
    fin = _m(gc["interest_received"]) + _m(gc["interest_paid"]) + _m(gc["other_income_received"])
    print(_row("net interest + other income received (p52)", fin))
    print(_row("tax paid less engine accrued tax", g["tax"] - _m(tx["income_taxes_paid"])))
    # The engine already takes the Northparkes stream out of revenue, so only the other
    # non-operational costs are added here (the stream payment would count twice).
    stream_pay = -_m(a["mines"]["northparkes"]["non_operational_costs"])
    print(_row("non-op costs other than the stream payment", non_op - stream_pay))
    print(_row("net mine cash flow, co. before those one-offs", nmcf_e,
               COMPANY["net_mine_cf"] - (non_op - stream_pay)))
    adj = g["fcff"] + e_capex_expl + corp_cap + (non_op - stream_pay) + wc + fin + g["tax"] - _m(tx["income_taxes_paid"])
    print(_row("engine FCFF on the company's basis", adj, COMPANY["group_cf"]))
    np_d = res["mines"]["northparkes"]
    np_gap = np_d["engine"]["omcf"] - np_d["company"]["omcf"]
    omcf_gap = omcf_e - _m(gc["operating_mine_cash_flow"])
    print(_row("  of which Northparkes OMCF (stream placement)", np_gap))
    print(_row("  stream payment, company below OMCF", -stream_pay))
    print(_row("  of which other five mines' OMCF", omcf_gap - np_gap))
    print(_row("  of which other, not separable", adj - COMPANY["group_cf"] - omcf_gap + stream_pay))
    print()
    print("  company revenue per gold ounce produced, gold-only mines (engine uses one group price):")
    for name in ("cowal", "mungari", "red_lake", "mt_rawdon"):
        x = a["mines"][name]
        print(f"    {name:<12} A${_v(x['revenue']) / _v(x['gold_produced_oz']) * _THOUSANDS_PER_MILLION:,.0f}/oz")
    return 0


def main() -> int:
    if "--fy26-actuals" in sys.argv[1:]:
        return main_fy26()
    a = check_gold_sensitivity()
    print(f"(a) GOLD SENSITIVITY: {SCENARIO} gold path +A${GOLD_STEP_AUD:.0f}/oz in every period, A$m")
    c = a["context"]
    print(f"  royalty rate {c['royalty_rate']:.4f}; tax rate {c['tax_rate']:.2f}; FY27 gold "
          f"{c['fy27_gold_koz']:.1f} koz; stream ounces sold at 10% of spot (lost value) "
          f"{c['stream_haircut_koz']:.2f} koz")
    for label in ("FY27 (stub, annualised)", "FY28 (engine Y1)"):
        b, d = a[label]["base"], a[label]["delta"]
        print(f"  {label}: base gold A${b['gold_aud_oz']:,.0f}/oz, gold {b['gold_koz']:.1f} koz")
        for k in ("revenue", "royalty", "operating_mine_cf", "ebitda", "tax", "fcff"):
            print(_row(f"  change in {k}", d[k]))
    print(f"  company stated: {COMPANY['gold_sens_low']:.0f}-{COMPANY['gold_sens_high']:.0f} "
          f"(FY27 cash flow, per A${GOLD_STEP_AUD:.0f}/oz)")
    print()

    b = check_backcast()
    e = b["engine"]
    print("(b) BACKCAST: FY27 guidance volumes, costs and capital at FY26 achieved prices "
          f"(gold A${e['gold_aud_oz']:,.0f}/oz, copper A${e['copper_aud_t']:,.0f}/t), A$m")
    print(f"  volumes: engine FY27 gold {e['gold_koz']:.1f} koz, copper {e['copper_kt']:.1f} kt; "
          f"FY26 actual gold sold {b['fy26_sold_koz']:.1f} koz, copper {b['fy26_copper_kt']:.1f} kt")
    print(f"  {'':<44}{'engine':>10}{'company':>10}{'gap':>10}")
    for k in ("revenue", "royalty", "operating_cost", "mine_exploration", "corporate_and_greenfields"):
        print(_row(k, e[k]))
    print(_row("EBITDA", e["ebitda"], COMPANY["ebitda"]))
    print(_row("operating mine cash flow (pre-capex)", e["operating_mine_cf"], COMPANY["operating_mine_cf"]))
    cs = b["capex_split"]
    print(_row("sustaining capital", -cs["sustaining"], COMPANY["sustaining"]))
    print(_row("major capital (mine dev + project)", -(cs["mine_development"] + cs["major_project"]),
               COMPANY["major_capital"]))
    print(_row("non-operational costs", 0.0, COMPANY["non_operational"]))
    print(_row("stream delivery (engine: in revenue)", 0.0, COMPANY["stream_delivery"]))
    print(_row("net mine cash flow", e["net_mine_cf"], COMPANY["net_mine_cf"]))
    print(_row("corporate and discovery", e["corporate_and_greenfields"], COMPANY["corporate_discovery"]))
    print(_row("net interest + other income", 0.0, COMPANY["net_interest"] + COMPANY["other_income"]))
    print(_row("working capital", e["delta_wc"], COMPANY["working_capital"]))
    print(_row("tax", e["tax"], COMPANY["tax_paid"]))
    print(_row("group cash flow (engine: FCFF)", e["fcff"], COMPANY["group_cf"]))
    print()
    fy26_koz = b["fy26_sold_koz"]
    gap = e["operating_mine_cf"] - COMPANY["operating_mine_cf"]
    stream = -b["stream_value"]
    rawdon = -COMPANY["mt_rawdon_omcf"]
    # unit cost: AISC difference on engine ounces, less the sustaining part (below OMCF)
    cost = -(b["engine_aisc"] - COMPANY["aisc_fy26"]) * e["gold_koz"] / _THOUSANDS_PER_MILLION \
        - (-cs["sustaining"] - COMPANY["sustaining"])
    volume = (e["gold_koz"] - fy26_koz) * (e["gold_aud_oz"] - COMPANY["aisc_fy26"]) / _THOUSANDS_PER_MILLION
    expl = e["mine_exploration"]
    print("  operating mine cash flow gap, approximate split (A$m):")
    print(f"    engine AISC-equivalent A${b['engine_aisc']:,.0f}/oz; FY26 actual A${COMPANY['aisc_fy26']:,.0f}/oz; "
          f"FY27 guidance A${COMPANY['aisc_fy27_low']:,.0f}-{COMPANY['aisc_fy27_high']:,.0f}/oz")
    for label, v in (("stream: engine nets it in revenue, company below", stream),
                     ("Mt Rawdon in FY26, closed for FY27", rawdon),
                     ("FY27 unit cost above FY26 (ex sustaining)", cost),
                     ("FY27 gold volume below FY26 sold", volume),
                     ("mine exploration charged in engine", expl)):
        print(_row(label, v))
    print(_row("residual (sold vs produced, other)", gap - stream - rawdon - cost - volume - expl))
    print(_row("total gap", gap))
    print()
    _, ri_mt = _inputs()
    base = ResourceEngine().run(ri_mt)
    y1 = _period(base, ri_mt, 1, False)
    print(f"  context: {SCENARIO} engine Y1 (= FY28) FCFF {y1['fcff']:.1f}, EBITDA {y1['ebitda']:.1f}, "
          f"capex {y1['capex']:.1f}, tax {y1['tax']:.1f}, gold A${y1['gold_aud_oz']:,.0f}/oz")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
