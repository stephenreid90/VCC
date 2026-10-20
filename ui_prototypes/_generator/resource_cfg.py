# -*- coding: utf-8 -*-
"""Resource-engine companies in the scenario-interface prototype (gap 9, 20 Oct 2026).

Builds the page config for a company whose ``normalised_baseline.engine`` is ``resource``
by running the production resource engine at generation time (D-23: no JS port; the page
reads engine output). Every number on the page comes from the engine or the data files;
nothing here is typed. Names no company: ``build_resource_cfg(cid, arch)``.

The browser-side "reduced form" for a resource company is an interpolation between values
the engine computed here for each scenario: a grid over the gold-path multiple on each
inventory basis, WACC steps either side of the engine rate, and the D-104 cost-price-link
elasticity across its declared range. The page multiplies the three factors, which is the
approximation it labels as such.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts"))

from size_resource_valuation import SCENARIOS, market_implied_gold_scale, run  # noqa: E402
from build_resource_review_data import LB_PER_T, scenario_meta  # noqa: E402
from vcc_valuations.resource_translator import (  # noqa: E402
    build_resource_inputs_from_data, cost_price_link_params, price_and_cost_paths, resource_wacc_from_data,
)

GOLD_SCALES = [round(0.7 + 0.1 * i, 2) for i in range(14)]   # ssot-allow: 0.7x to 2.0x, the review page's range
WACC_STEPS_PP = [-2.0, -1.0, 0.0, 1.0, 2.0]                   # ssot-allow: percentage-point steps either side of the engine rate
PCT = 100.0                                                    # ssot-allow: per cent
LINK_GRID_STEP = 0.5                                           # ssot-allow: slider step for the elasticity, % per 10%

DISPLAY = {
    "orderly_convergence": ("Orderly Convergence", "down"),
    "muddle_through": ("Muddle Through", "live"),
    "ai_productivity_lag": ("AI Productivity Lag", "up"),
    "fragmentation": ("Fragmentation", "up"),
    "disorderly_climate_crystallisation": ("Disorderly Climate", "up"),
    "stagflation_persists": ("Stagflation Persists", "up"),
}
BASIS_LABEL = {"reserves": "Ore Reserves only", "stated_life": "Stated life of mine", "life_extension": "+%d years per mine"}
_TAG = {"disclosed": "disclosed", "derived": "derived", "judgment": "judgment", "default": "judgment"}


def _m(v):
    return "{:,.0f}".format(round(v))


def _neg(v):
    return "(%s)" % _m(abs(v))


def _pct(v, dp=0):
    return "%+.*f%%" % (dp, v * PCT)


def _r1(xs):
    return [round(x, 1) for x in xs]


def _frange(lo, hi, step):
    out, x = [], lo
    while x <= hi + 1e-9:
        out.append(round(x, 4)); x += step
    return out


def resource_pack(cid, arch):
    """Run the engine for every scenario and every sized variant the page interpolates on."""
    base, inp = run(cid, arch, "muddle_through")
    fin = inp["financials"]
    nb = inp["company_raw"]["normalised_baseline"]
    spot = fin["spot_reference"]
    flat = {"gold_usd_oz": spot["gold_usd_oz"], "aud_usd": spot["aud_usd"],
            "copper_usd_t": spot["copper_usd_lb_sep_qtr_achieved"] * LB_PER_T}
    link = cost_price_link_params(inp)
    link_lo, link_hi = link["sensitivity_range_per_10pct"]
    link_x = sorted(set([0.0] + _frange(link_lo, link_hi, LINK_GRID_STEP) + [link["elasticity_per_10pct"]]))
    _all = [nb["inventory"]["basis"]] + list(nb["inventory"]["sensitivity_bases"])
    bases = [b for b in ("reserves", "stated_life", "life_extension") if b in _all] + [b for b in _all if b not in ("reserves", "stated_life", "life_extension")]  # shortest life first
    wb = resource_wacc_from_data(inp)
    wacc = base.wacc
    vd = str(nb["valuation_date"])
    fy0 = int(vd[2:4]) + (1 if int(vd[5:7]) > 6 else 0)  # June year-end
    market = fin["market_data"]["price_aud"]

    scen = {}
    for sid in SCENARIOS:
        r, sinp = run(cid, arch, sid)
        v0 = r.value_per_share
        gold = {b: [run(cid, arch, sid, basis=b, gold_scale=k)[0].value_per_share for k in GOLD_SCALES] for b in bases}
        wacc_y = [run(cid, arch, sid, wacc_override=wacc + s / PCT)[0].value_per_share / v0 for s in WACC_STEPS_PP]
        link_y = [run(cid, arch, sid, cost_link_override={"elasticity_per_10pct": e})[0].value_per_share / v0 for e in link_x]
        n = len(r.fcff)
        paths = price_and_cost_paths(sinp, sid, n)
        meta = scenario_meta(sid)
        pts = {v: dict(map(tuple, meta["series"][v]["points"])) for v in meta["series"]}
        scen[sid] = {
            "name": DISPLAY[sid][0], "kind": DISPLAY[sid][1], "result": r, "meta": meta,
            "value": v0, "gold": gold,
            "wacc_x": [round((wacc + s / PCT) * PCT, 4) for s in WACC_STEPS_PP], "wacc_y": wacc_y,
            "link_x": link_x, "link_y": link_y,
            "y10": {"gold_usd_real": pts["gold_price_usd_real"].get(10), "copper_usd_real": pts["copper_price_usd_real"].get(10),
                    "aud_usd": pts["aud_usd"].get(10)},
            "gold_usd_real_path": [paths["gold_aud_oz"][t] * paths["aud_usd"][t] / paths["cpi_index"][t] for t in range(n)],
            "aud_usd_path": list(paths["aud_usd"]),
            "years": [("FY%d stub" % fy0) if t == 0 else "FY%d" % (fy0 + t) for t in range(n)],
            "spot_flat": run(cid, arch, sid, flat_real=flat)[0].value_per_share,
            "implied_gold_scale": market_implied_gold_scale(cid, arch, sid, market),
        }
    return {"base": base, "inp": inp, "fin": fin, "nb": nb, "wb": wb, "wacc": wacc, "link": link, "bases": bases,
            "fy0": fy0, "market": market, "flat": flat, "scen": scen, "live": "muddle_through",
            "life_extension_years": int(nb["inventory"].get("life_extension_years", 0))}


def _industry(arch):
    d = yaml.safe_load((_ROOT / "data" / "industries" / f"{arch}.yaml").read_text(encoding="utf-8"))
    return d["industry_archetype"]


def _rating(s):
    return str(s).replace("_", " ").replace(" to ", "–").capitalize()


def _tidy(s):
    return " ".join(str(s).split())


def build_resource_cfg(cid, arch, world_desc, dtable, bridge, buildup_note):
    """The page config dict for one resource company (the same shape the other pages use)."""
    p = resource_pack(cid, arch)
    base, inp, fin, nb, wb = p["base"], p["inp"], p["fin"], p["nb"], p["wb"]
    cp = inp["company_raw"]["company_position"]
    live = p["scen"][p["live"]]
    r0 = live["result"]
    bases = p["bases"]
    basis_labels = [BASIS_LABEL[b] % p["life_extension_years"] if "%" in BASIS_LABEL[b] else BASIS_LABEL[b] for b in bases]
    basis_default = bases.index(nb["inventory"]["basis"])
    link = p["link"]
    wacc_ui = round(p["wacc"] * PCT, 2)
    market = p["market"]
    vals = {s["name"]: round(s["value"], 3) for s in p["scen"].values()}
    mt = vals["Muddle Through"]
    ups = [v - mt for v in vals.values() if v > mt]
    downs = [mt - v for v in vals.values() if v < mt]
    asym = (max(downs) / max(ups)) if (ups and downs) else None
    yrs = live["years"]
    hz = r0.horizon_years
    explicit = "%s–%s" % (yrs[0], yrs[hz])
    runoff = "%s–%s" % (yrs[hz + 1], yrs[-1]) if len(yrs) > hz + 1 else "none"
    last_mine = max(r0.mine_last_period.items(), key=lambda kv: kv[1])
    first_mine = min((kv for kv in r0.mine_last_period.items() if ":" not in kv[0]), key=lambda kv: kv[1])
    spot_flat = live["spot_flat"]
    gold_mult = live["implied_gold_scale"]
    rf_date = str(fin.get("wacc_inputs", {}).get("risk_free_rate_date") or fin.get("risk_free_rate_date") or "")
    if not rf_date:
        for blk in fin.values():
            if isinstance(blk, dict) and "risk_free_rate_date" in blk:
                rf_date = str(blk["risk_free_rate_date"]); break
    price_date = str(fin["market_data"]["price_date"])
    spot_gold = p["flat"]["gold_usd_oz"]
    spot_aud = p["flat"]["aud_usd"]
    real_gold_usd = spot_gold * gold_mult

    # ---- bars: six worlds in the page's order, the spot-held-flat reference after the live case ----
    order = ["orderly_convergence", "muddle_through", "ai_productivity_lag", "disorderly_climate_crystallisation",
             "fragmentation", "stagflation_persists"]
    bars = []
    for sid in order:
        s = p["scen"][sid]
        bars.append({"n": s["name"], "v": vals[s["name"]], "kind": s["kind"]})
        if sid == p["live"]:
            bars.append({"n": "Spot held flat (real)", "v": round(spot_flat, 3), "kind": "broker"})

    # ---- engine grid the browser interpolates on ----
    grid = {"live": "Muddle Through", "goldScales": GOLD_SCALES, "bases": bases, "basisDefault": basis_default, "byScen": {}}
    for s in p["scen"].values():
        grid["byScen"][s["name"]] = {"gold": {b: [round(v, 4) for v in s["gold"][b]] for b in bases},
                                     "wacc": {"x": s["wacc_x"], "y": [round(y, 6) for y in s["wacc_y"]]},
                                     "link": {"x": s["link_x"], "y": [round(y, 6) for y in s["link_y"]]}}

    sliders = [
        {"k": "re", "label": "Discount rate (WACC)", "min": round(wacc_ui - 2.0, 2), "max": round(wacc_ui + 2.0, 2), "step": 0.25, "def": wacc_ui, "suf": "%", "dec": 2},  # ssot-allow: slider step
        {"k": "gold", "label": "Gold price path (× the scenario's path)", "min": GOLD_SCALES[0], "max": GOLD_SCALES[-1], "step": 0.05, "def": 1.0, "suf": "×", "dec": 2},  # ssot-allow: slider step
        {"k": "basis", "label": "Inventory basis (mine life)", "min": 0, "max": len(bases) - 1, "step": 1, "def": basis_default, "suf": "", "dec": 0, "labels": basis_labels},
        {"k": "link", "label": "Cost response to gold (% per 10% real move, D-104)", "min": 0.0, "max": link["sensitivity_range_per_10pct"][1], "step": LINK_GRID_STEP, "def": link["elasticity_per_10pct"], "suf": "%", "dec": 1},
    ]

    # ---- Five Forces: archetype rating and rationale from data/industries, company position from layer 2 ----
    ind = _industry(arch)
    ff = ind["five_forces"]
    cpos = cp["five_forces_company_position"]
    rows = [
        ["Buyer power", _rating(ff["buyer_power"]["rating"]), _tidy(ff["buyer_power"]["rationale"]), "at industry average", "0 bps", "A price taker like every producer; the scenario price series carry the whole effect."],
        ["Supplier power", _rating(ff["supplier_power"]["rating"]), _tidy(ff["supplier_power"]["rationale"]), "at industry average", "0 bps", "Costs escalate with CPI plus the scenario escalator and respond to the gold price (D-104); no company offset."],
        ["New entrants", _rating(ff["threat_of_new_entrants"]["rating"]), _tidy(ff["threat_of_new_entrants"]["rationale"]), "at industry average", "0 bps", "Entry adds supply slowly and cannot set the price."],
        ["Substitutes", _rating(ff["threat_of_substitutes"]["rating"]), _tidy(ff["threat_of_substitutes"]["rationale"]), "at industry average", "0 bps", "Other stores of value move the price, not the company's ounces."],
        ["Rivalry", _rating(ff["rivalry"]["rating"]), _tidy(ff["rivalry"]["rationale"]), "more favourable", "0 bps",
         "Cost position %s: %s" % (str(cpos["cost_position"]["placement_on_curve"]).replace("_", " "), _tidy(cpos["cost_position"]["evidence"]))],
    ]
    forces = {
        "intro": "<b>The industry.</b> %s. %s" % (ind["name"], "Producers sell every ounce at the quoted price, so the forces do not set a growth or margin offset the way they do for an industrial. The return over the cost of capital is a rent on the ore, with an end date, carried mine by mine in the cash flows (D-43a)."),
        "rows": rows,
        "net": "No growth or margin offset is routed from the forces (0 bps). %s moat: %s. The company&rsquo;s position shows in its place on the cost curve and in each mine&rsquo;s life, both of which the engine reads directly." % (cp["name"], _tidy(cpos["moat"]["evidence"])),
        "impacts": [{"drv": "", "bps": 0} for _ in rows],
    }

    # ---- company position ----
    segs = "".join("<li><b>%s</b> (%.0f%% of FY25 revenue) &ndash; %s</li>" % (sg["segment"].replace("_", " ").title(), sg["revenue_share"] * PCT, _tidy(sg["notes"])) for sg in cp["segments"])
    closures = sorted(((k, v) for k, v in r0.mine_last_period.items() if ":" not in k), key=lambda kv: kv[1])
    close_txt = "; ".join("%s FY%d" % (k.replace("_", " ").title(), p["fy0"] + v) for k, v in closures)
    position = (
        '<div class="thytag" style="color:var(--text3); margin:0 0 4px;">Mines and lives</div><ul style="padding-left:18px;">' + segs +
        '<li><b>Stated lives</b> (engine, %s basis) &ndash; %s. The last mine closes %.1f years from the valuation date.</li></ul>' % (nb["inventory"]["basis"].replace("_", " "), close_txt, r0.life_years) +
        '<div class="thytag" style="color:var(--text3); margin:14px 0 4px;">Balance sheet and capital</div><ul style="padding-left:18px;">' +
        '<li><b>Liquidity</b> &ndash; %s</li><li><b>Dividends</b> &ndash; %s</li><li><b>M&amp;A</b> &ndash; %s</li></ul>' % (_tidy(cp["balance_sheet"]["liquidity"]), _tidy(cp["capital_allocation"]["dividend_policy"]), _tidy(cp["capital_allocation"]["m_and_a_posture"])) +
        '<div class="thytag" style="color:var(--text3); margin:14px 0 4px;">Management and transition</div><ul style="padding-left:18px;">' +
        '<li><b>Strategy</b> &ndash; %s</li><li><b>Execution</b> &ndash; %s</li><li><b>Transition</b> &ndash; %s %s</li></ul>' % (_tidy(cp["management_and_governance"]["strategy_evidence"]), _tidy(cp["management_and_governance"]["execution_evidence"]), _tidy(cp["esg_and_transition"]["carbon_intensity"]), _tidy(cp["esg_and_transition"]["transition_plan"]))
    )

    # ---- discount rate ----
    ke = wb.cost_of_equity if hasattr(wb, "cost_of_equity") else wb.risk_free_rate + wb.beta * wb.equity_risk_premium
    ev_w = wb.equity_market_value / (wb.equity_market_value + wb.debt_market_value)
    beta_sel = nb["wacc_build"]["beta_selection_rationale"]
    discount = (
        '<p>Single WACC of %.2f%%, held across the stub, the ten explicit years and the run-off (D-01). Risk sits in the price paths and the mine plans, not the rate.</p>' % (p["wacc"] * PCT) +
        dtable([["Risk-free rate (10y bond, %s)" % rf_date, "%.2f%%" % (wb.risk_free_rate * PCT), "disclosed"],
                ["Equity risk premium", "%.2f%%" % (wb.equity_risk_premium * PCT), "judgment"],
                ["Beta — selected", "%.2f" % wb.beta, "judgment"],
                ["= Cost of equity", "%.2f%%" % (ke * PCT), "derived"],
                ["Cost of debt (pre-tax, Rf + spread)", "%.2f%%" % (wb.cost_of_debt_pretax * PCT), "derived"],
                ["= WACC (%.0f/%.0f E/D, spot weights)" % (ev_w * PCT, (1 - ev_w) * PCT), "%.2f%%" % (p["wacc"] * PCT), "derived"]]) +
        '<p style="margin-top:8px;"><b>Beta — %s (D-101, held).</b> Peers %s. %s No beta workbench is shown for this company: the peer betas are not observed in the repo, and the page does not invent them.</p>' % (beta_sel["method"], ", ".join(beta_sel["peers"]), _tidy(beta_sel["selection"]))
    )
    assum = [
        ["Valuation date", str(nb["valuation_date"]), "disclosed", "D-94; stub of %.4f years to the June year-end." % nb["stub_years"]],
        ["Risk-free rate", "%.2f%%" % (wb.risk_free_rate * PCT), "disclosed", "10-year Australian government bond, %s (D-101)." % rf_date],
        ["Equity risk premium", "%.2f%%" % (wb.equity_risk_premium * PCT), "judgment", "House ERP, as for the other companies."],
        ["Beta (selected)", "%.2f" % wb.beta, "judgment", "Peer judgement; observed peer betas awaited (D-101 held)."],
        ["Cost of debt (pre-tax)", "%.2f%%" % (wb.cost_of_debt_pretax * PCT), "derived", _tidy(nb["wacc_build"]["cost_of_debt_rationale"])],
        ["WACC", "%.2f%%" % (p["wacc"] * PCT), "derived", "Spot market-value weights: equity A$%sm, debt A$%sm." % (_m(wb.equity_market_value), _m(wb.debt_market_value))],
        ["Inventory basis", basis_labels[basis_default], "disclosed", _tidy(nb["inventory"]["basis_rationale"])],
        ["Life extension (sensitivity)", "%d years per mine" % p["life_extension_years"], "judgment", "Resource conversion upside, a sized alternative, never the default (D-97)."],
        ["Replacement after depletion", "Zero NPV", "judgment", "Ounces are replaced at prices that earn the cost of capital, so the terminal carries no perpetuity (D-97)."],
        ["Project capital run-off", ", ".join("%.0f%%" % (x * PCT) for x in nb["project_capex_runoff"]), "judgment", _tidy(nb["project_capex_runoff_rationale"])],
        ["Cost-price link", "%.1f%% per 10%%, lag %dy, cap +%.0f%%" % (link["elasticity_per_10pct"], link["lag_years"], link["cap_above_base_pct"]), "judgment", "D-104: non-royalty cash cost and sustaining capital follow the real A$ gold price against the scenario's period-0 level; symmetric. Range %.1f–%.1f%% sized." % tuple(link["sensitivity_range_per_10pct"])],
        ["Royalty rate", "%.2f%% of revenue" % (build_resource_inputs_from_data(inp, p["live"]).royalty_rate * PCT), "derived", "One group rate, fully price-linked (paper §6 gap 5)."],
        ["Tax rate", "%.0f%%" % (wb.tax_rate * PCT), "disclosed", "Australian company rate; book D&amp;A per ounce is the depreciation proxy."],
        ["Net debt at valuation", "A$%sm" % _m(r0.net_debt_at_valuation), "derived", _tidy(nb["equity_bridge_run_rates"]["rationale"])],
        ["Rehabilitation and other claims", "A$%sm" % _m(r0.equity_bridge_adjustments_net), "disclosed", "Closure costs are not in the mine cash flows, so the provision is a debt-like claim (D-100)."],  # ssot-allow: decision id
        ["Leases", "A$%sm" % _m(r0.lease_liabilities), "disclosed", "Approach A (leases are debt, methodology §4.6)."],
        ["Shares", "%.1fm" % r0.shares_outstanding, "disclosed", _tidy(fin["share_statistics"]["shares_outstanding_source"])],
    ]

    # ---- build-up (engine, Muddle Through) ----
    rows_dcf = [
        ["Sum PV explicit FCFF (%s)" % explicit, _m(r0.pv_explicit), "The stub and ten explicit years of free cash flow to the firm, discounted at the single WACC of %.2f%% with mid-period discounting. Each mine produces at its FY27 guidance rate at the scenario's gold and copper prices in A$." % (p["wacc"] * PCT)],
        ["PV of life-of-mine cash flows after year 10 (%s)" % runoff, _m(r0.pv_terminal), "The depletion run-off (D-97): the same mine-by-mine cash flows continued to each mine's stated closure, the last in %s. No perpetuity; replacement is at zero NPV. This is %.0f%% of enterprise value." % (yrs[-1], r0.terminal_share_of_ev * PCT)],
        ["Enterprise value", _m(r0.enterprise_value), "PV of explicit FCFF %s + PV of the run-off %s." % (_m(r0.pv_explicit), _m(r0.pv_terminal))],
        ["Less: net debt", _neg(r0.net_debt_at_valuation), "Net cash at 30 Sep 2026 less the final dividend paid 2 Oct 2026 (D-100)."],  # ssot-allow: decision id
        ["Less: rehabilitation and other claims", _neg(r0.equity_bridge_adjustments_net), "Rehabilitation provision, a debt-like claim because closure costs are outside the mine cash flows."],
        ["Less: leases", _neg(r0.lease_liabilities), "Lease liabilities as debt (Approach A)."],
        ["Equity value", _m(r0.equity_value), "Enterprise value less net debt, rehabilitation and leases."],
        ["÷ shares (m)", "%.1f" % r0.shares_outstanding, "Issued shares at 30 Sep 2026, anchored to the same date as net debt."],
        ["Value per share AUD", "%.2f" % r0.value_per_share, ""],
    ]
    dcf_intro = ("A$ m. Click any line to see its make-up. Stub plus ten explicit years (%s) and the life-of-mine run-off (%s), one WACC of %.2f%%. "
                 "The terminal is the depletion run-off, not a growth perpetuity (D-97). %s" % (explicit, runoff, p["wacc"] * PCT, buildup_note))
    dcf_html = bridge([[r[0], r[1]] for r in rows_dcf],
                      "A$ m. Engine-computed Muddle Through. Explicit %s at WACC %.2f%%; run-off %s is %.0f%% of enterprise value; life %.1f years." % (explicit, p["wacc"] * PCT, runoff, r0.terminal_share_of_ev * PCT, r0.life_years))

    def _row(label, arr, pct=False):
        return {"label": label, "vals": [round(x, 4 if pct else 1) + 0.0 for x in arr], "pct": pct}
    workings = {"title": "Per-year mine build — Muddle Through (A$ m)",
                "note": "Bottom-up from the resource engine: ounces and tonnes at guidance rates × the scenario's A$ prices → revenue less royalty, operating cost (with the D-104 cost response), exploration and corporate → EBITDA → FCFF after tax, capital and working capital. Columns run to the last mine's closure.",
                "years": yrs,
                "rows": [_row("Gold sold (koz)", r0.gold_koz), _row("Copper sold (kt)", r0.copper_kt),
                         _row("Gold price (A$/oz, nominal)", r0.gold_aud_oz), _row("Revenue", r0.revenue),
                         _row("Royalty", [-x for x in r0.royalty]), _row("Operating cost", [-x for x in r0.operating_cost]),
                         _row("Exploration and corporate", [-x for x in r0.exploration_and_corporate]),
                         _row("EBITDA", r0.ebitda), _row("Tax", [-x for x in r0.tax]), _row("Capital", [-x for x in r0.capex]),
                         _row("Working capital", [-x for x in r0.delta_wc]), _row("FCFF", r0.fcff),
                         _row("PV of FCFF", r0.pv_fcff), _row("Cost response (D-104, % on base unit cost)", [m - 1.0 for m in r0.cost_price_link], True)],
                "foot": "The engine&#39;s central case (does not move with the sliders); the same per-year build the EVN valuation review page shows."}

    # ---- narratives: the written price basis per scenario, then why the number lands there ----
    def _narr(sid):
        s = p["scen"][sid]; r = s["result"]; nm = s["name"]
        ser = s["meta"]["series"]
        v = vals[nm]; d_mt = (v / mt - 1.0) * PCT; d_mk = (v / market - 1.0) * PCT
        y10 = s["y10"]
        g10 = (y10["gold_usd_real"] / spot_gold - 1.0) * PCT if y10["gold_usd_real"] else 0.0
        a10 = y10["aud_usd"] if y10["aud_usd"] else spot_aud
        linkmax = max(r.cost_price_link) if r.cost_price_link else 1.0
        g_fy = r.gold_aud_oz[hz] / r0.gold_aud_oz[hz] - 1.0
        if sid == p["live"]:
            lead = "Spot gold and today\u2019s exchange rate held flat in real terms, so the A$ price per ounce rises only with inflation and each mine earns its current margin to the end of its stated life."
        else:
            lead = ("The A$ gold price in %s is %.0f%% %s Muddle Through\u2019s, from real gold at US$%s by year 10 and AUD/USD at %.2f, and the value follows it %s."
                    % (yrs[hz], abs(g_fy) * PCT, "above" if g_fy >= 0 else "below", _m(y10["gold_usd_real"] or spot_gold), a10, "up" if v >= mt else "down"))
        parts = ['<p>%s</p>' % lead, '<p><b>Gold.</b> %s <b>Copper.</b> %s <b>AUD/USD.</b> %s</p>' % (ser["gold_price_usd_real"]["basis"] or "As Muddle Through.", ser["copper_price_usd_real"]["basis"] or "As Muddle Through.", ser["aud_usd"]["basis"] or "As Muddle Through.")]
        parts.append('<p><b>Channels.</b> Real gold reaches US$%s an ounce by year 10 (%+.0f%% on spot US$%s) at AUD/USD %.2f; the FY28 A$ price is %s/oz. Unit costs respond to the real A$ price with a one-year lag (D-104): the multiplier peaks at %.3f. Volumes do not move: each mine runs at its guidance rate to its stated closure.</p>'
                     % (_m(y10["gold_usd_real"] or spot_gold), g10, _m(spot_gold), a10, _m(r.gold_aud_oz[1]), linkmax))
        if sid == p["live"]:
            parts.append('<p><b>Why A$%.2f?</b> Spot held flat in real terms (D-102) at today&rsquo;s AUD gives FY28 EBITDA of A$%sm on %s koz of gold and %s kt of copper; the stub and ten explicit years are %.0f%% of enterprise value and the run-off %.0f%%. The value sits %.0f%% below the A$%.2f market price: the market needs a gold path %.2f times this one, about US$%s an ounce in real terms. The gap is disclosed, not reconciled (D-92).</p>'
                         % (v, _m(r.ebitda[1]), _m(r.gold_koz[1]), _m(r.copper_kt[1]), (1 - r.terminal_share_of_ev) * PCT, r.terminal_share_of_ev * PCT, abs(d_mk), market, gold_mult, _m(real_gold_usd)))
            parts.append('<p style="background:var(--secondary); border-radius:8px; padding:10px;"><b>Mental short-cut:</b> a gold price times an exchange rate, less a cost base that creeps up with the price, on mines with dates. There is no terminal growth to argue about, only the price path and the mine lives.</p>')
        else:
            parts.append('<p><b>Why A$%.2f?</b> %+.0f%% against Muddle Through and %+.0f%% against the market price. The move is almost all the gold price in A$: the real USD path and the exchange rate together set the A$ price per ounce, and costs follow it only partly. Run-off share %.0f%%.</p>' % (v, d_mt, d_mk, r.terminal_share_of_ev * PCT))
        return "".join(parts)
    narr = {p["scen"][sid]["name"]: _narr(sid) for sid in SCENARIOS}
    narr["_placeholder"] = "<p>Scenario narrative pending.</p>"

    inv_vals = {b: round(live["gold"][b][GOLD_SCALES.index(1.0)], 2) for b in bases}
    runoff_block = (
        '<div id="runoff" class="sub" style="margin-top:10px; line-height:1.5;"><b>Depletion disclosures (paper §6 gap 7, replacing the going-concern terminal set):</b> '
        'run-off after year 10 is %.0f%% of enterprise value; life %.1f years to the last closure (%s, %s); value per share by inventory basis — %s.</div>'
        % (r0.terminal_share_of_ev * PCT, r0.life_years, last_mine[0].replace("_", " ").title(), yrs[last_mine[1]],
           "; ".join("%s A$%.2f" % (basis_labels[i], inv_vals[b]) for i, b in enumerate(bases)))
    )

    cfg = {
        "company": "%s (ASX:%s)" % (cp["name"], cp["ticker"]), "companyShort": cp["ticker"], "ccy": "AUD",
        "ccynote": "AUD · WACC-based DCF · depletion run-off (resource engine)",
        "dp": 2, "market": market, "broker": round(spot_flat, 2), "scale": round(max(list(vals.values()) + [market, spot_flat]) * 1.15, 1),  # ssot-allow: bar headroom
        "mklab": "vs market (%.2f)" % market, "brlab": "vs spot held flat (%.2f)" % spot_flat,
        "refLabel": "spot held flat (real)", "discLabel": "WACC",
        "metric4": {"label": "Gold multiple the market needs", "value": "%.2f×" % gold_mult},
        "pvsub": "", "topnote": ("Working prototype — all six scenarios computed by the production resource engine (D-96). "
                                 "Slider responses interpolate between engine-computed points (gold path, mine life, WACC, cost response); they are an approximation, not the engine. Reid Advisory, October 2026."),
        "footnote": ("Prototype for discussion. Engine-computed central case: %s Muddle Through AUD %.2f (market AUD %.2f, %s). Gold spot US$%s/oz at AUD/USD %.4f on the valuation date. Per-scenario detail in the EVN valuation review page and set `%s` in resource_valuation_sets.yaml."
                     % (cp["ticker"], mt, market, price_date, _m(spot_gold), spot_aud, cid)),
        "cp": {"form": "engine_grid", "base": mt, "re0": wacc_ui / PCT, "reEngine": round(p["wacc"], 6), "xKey": "gold", "xk": 0.0, "x0": 1.0, "grid": grid},
        "sliders": sliders,
        "scenarios": bars,
        "titles": {"world": "World scenario", "forces": "Company vs industry — Five Forces", "position": "Company position",
                   "discount": "Discount rate", "assum": "Assumptions & rationale", "dcf": "Valuation build-up"},
        "narr": narr,
        "_forces": forces,
        "_position": position,
        "_discount": discount,
        "_assum": assum,
        "dcf": dcf_html, "dcfIntro": dcf_intro, "dcfRows": rows_dcf,
        "dcfDetail": {"workings": workings},
        "worldDesc": world_desc,
        "workbookNote": "No formula workbook is embedded for this company yet: the mine-by-mine run-off workbook is its own build (paper §6 gap 9). The per-year table above is the engine's central case.",
        "_runoffBlock": runoff_block,
        "_prov": {"dataDate": price_date},
        "_pack": {"base": mt, "wacc": p["wacc"], "discount_to_market": r0.discount_to_market, "vals": vals, "asym": asym,
                  "terminal_share": r0.terminal_share_of_ev, "terminal_denom": "EV", "life_years": r0.life_years,
                  "spot_flat": spot_flat, "implied_gold_scale": gold_mult, "rf_date": rf_date, "rf": wb.risk_free_rate},
    }
    if asym is not None:
        cfg["asymNote"] = "%.2f×" % asym
    return cfg
