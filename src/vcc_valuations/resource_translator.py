"""
Data -> ResourceEngineInputs for resource_lifecycle archetypes (D-96 proposed, 20 Oct 2026).

Kept beside ``translator.py`` rather than inside it: the resource engine reads a
different shape (a mine plan, price series, an inventory basis), and nothing here is
shared with the growth-chain machinery. Like ``translator.py`` it names no company, mine
or driver: the mines are whatever ``guidance_fy27.mines`` lists, the series are whatever
the archetype's ``resource_lifecycle`` block names, and every judgement is read from
``normalised_baseline``.

Method: ``design/methodology/resource_lifecycle_and_mining_drivers.md``.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from vcc_valuations.assumptions.wacc import WaccBuild
from vcc_valuations.dcf.fcf_engine import EquityBridge
from vcc_valuations.dcf.resource_engine import MineInputs, ResourceEngineInputs, cost_price_link_path
from vcc_valuations.translator import (
    scenario_equilibrium_year,
    working_capital_intensity_from_data,
)

INVENTORY_BASES = ("stated_life", "reserves", "life_extension")
_KOZ_PER_MOZ = 1.0e3  # ssot-allow: unit conversion


def _mid(band: dict) -> float:
    return (band["low"] + band["high"]) / 2.0


def macro_level_at(inputs: dict, variable: str, year: float) -> float:
    """A scenario series at ``year`` in its own units (no percent scaling), interpolated
    linearly between anchors and held flat outside them (the D-37 convention)."""
    scenario = inputs["scenario"]
    for mv in scenario.macro_variables:
        if mv.variable != variable or not mv.time_series:
            continue
        pts = sorted((p.year, p.value) for p in mv.time_series)
        if year <= pts[0][0]:
            return pts[0][1]
        if year >= pts[-1][0]:
            return pts[-1][1]
        for (y0, v0), (y1, v1) in zip(pts, pts[1:]):
            if y0 <= year <= y1:
                return v0 + (v1 - v0) * (year - y0) / (y1 - y0)
    raise KeyError(f"{scenario.id}: no time series for {variable!r}")


def _framework(inputs: dict):
    fw = inputs["archetype"].complementary_framework
    if fw is None or fw.type.value != "resource_lifecycle":
        raise ValueError(f"{inputs['archetype'].id}: not a resource_lifecycle archetype")
    return fw.details


def _series_for(details, role: str) -> str:
    for c in details.commodities:
        if c.role.value == role:
            return c.price_series
    raise KeyError(f"no {role} commodity declared")


def real_cost_escalation_path(inputs: dict, scenario_id: str, periods: int) -> List[float]:
    """Per-period real cost escalation (decimal) from the impact matrix.

    The matrix's ``real_cost_escalation.quantified_override.mid`` (percentage points a
    year above CPI) applies from year 1 to the year before the scenario's final phase
    starts (``scenario_equilibrium_year``); the higher level then persists. Period 0 (the
    stub) carries none: guidance is already struck in that year's dollars.
    """
    matrix = inputs.get("matrix")
    mid = 0.0
    for entry in (matrix.matrix if matrix else []):
        if entry.scenario == scenario_id and "real_cost_escalation" in entry.drivers:
            q = entry.drivers["real_cost_escalation"].quantified_override
            mid = (q.mid if q else 0.0) / 100.0  # ssot-allow: percent to decimal
    eq = scenario_equilibrium_year(inputs)
    return [mid if 1 <= t < eq else 0.0 for t in range(periods)]


def price_and_cost_paths(inputs: dict, scenario_id: str, periods: int,
                         flat_real: Optional[Dict[str, float]] = None) -> Dict[str, List[float]]:
    """Nominal A$ gold and copper prices and the cost index, per period.

    Period t reads scenario year t (the stub reads year 1, the D-37 flat-before-first-anchor
    convention). The CPI index compounds the scenario's advanced CPI from period 1; real
    prices are inflated by it and costs by it plus the real escalator.
    """
    d = _framework(inputs)
    gold_s = _series_for(d, "primary")
    cu_s = _series_for(d, "by_product")
    esc = real_cost_escalation_path(inputs, scenario_id, periods)
    cpi_idx, cost_idx = [1.0], [1.0]
    for t in range(1, periods):
        cpi = macro_level_at(inputs, d.inflation_series, t) / 100.0  # ssot-allow: percent to decimal
        cpi_idx.append(cpi_idx[-1] * (1.0 + cpi))
        cost_idx.append(cost_idx[-1] * (1.0 + cpi + esc[t]))
    # ``flat_real`` replaces the three price series with constants (real gold, real
    # copper, AUD/USD) for the spot-held-flat disclosure; CPI and costs stay the scenario's.
    def level(series: str, key: str, y: float) -> float:
        return flat_real[key] if flat_real is not None else macro_level_at(inputs, series, y)

    gold, cu, fx = [], [], []
    for t in range(periods):
        y = max(t, 1)
        aud_usd = level(d.fx_series, "aud_usd", y)
        fx.append(aud_usd)
        gold.append(level(gold_s, "gold_usd_oz", y) * cpi_idx[t] / aud_usd)
        cu.append(level(cu_s, "copper_usd_t", y) * cpi_idx[t] / aud_usd)
    return {"gold_aud_oz": gold, "copper_aud_t": cu, "cost_index": cost_idx,
            "cpi_index": cpi_idx, "aud_usd": fx, "real_escalation": esc,
            "primary_aud": gold}


def cost_price_link_params(inputs: dict, override: Optional[Dict[str, float]] = None) -> Optional[dict]:
    """The D-104 parameters: the archetype's ``cost_price_link`` block, with any fields the
    company's ``normalised_baseline.cost_price_link`` overrides, then any caller override
    (the sized sensitivities). None when the archetype declares no link."""
    d = _framework(inputs)
    if d.cost_price_link is None:
        return None
    params = d.cost_price_link.model_dump()
    nb = inputs["company_raw"]["normalised_baseline"]
    for src in (nb.get("cost_price_link") or {}, override or {}):
        for k, v in src.items():
            if k not in params:
                raise KeyError(f"cost_price_link override names an unknown field {k!r}")
            params[k] = v
    return params


def cost_price_link_from_paths(inputs: dict, paths: Dict[str, List[float]],
                               override: Optional[Dict[str, float]] = None,
                               reference: Optional[float] = None) -> List[float]:
    """Per-period D-104 multiplier from the primary commodity's REAL price in the
    functional currency (nominal path over the CPI index), against the period-0 level
    unless ``reference`` is given. Empty when the archetype declares no link."""
    params = cost_price_link_params(inputs, override)
    if params is None:
        return []
    real = [p / c for p, c in zip(paths["primary_aud"], paths["cpi_index"])]
    return cost_price_link_path(
        real, elasticity=params["elasticity_per_10pct"] / 10.0,  # ssot-allow: per-10% to per-unit
        lag_periods=params["lag_years"], cap_above_base=params["cap_above_base_pct"] / 100.0,  # ssot-allow: percent to decimal
        reference=reference, symmetric=bool(params["symmetric"]),
    )


def royalty_rate_from_data(fin: dict) -> float:
    """[derived] FY26 royalty per sold ounce over FY26 metal revenue per sold ounce."""
    ry = fin["royalties_fy26"]
    royalty = ry["royalty_aud_per_sold_oz"] * ry["gold_sold_oz"]
    revenue = ry["gold_sold_oz"] * ry["achieved_gold_aud_oz"] + ry["copper_produced_t"] * ry["achieved_copper_aud_t"]
    return royalty / revenue


def _fy_index(d: date) -> int:
    """The fiscal year (June year-end) a date falls in, e.g. 20 Oct 2026 -> 2027."""
    return d.year + 1 if d.month > 6 else d.year


def inventories_from_data(inputs: dict, basis: str) -> Dict[str, Dict[str, float]]:
    """Recoverable inventory per mine from the valuation date, on the declared basis."""
    if basis not in INVENTORY_BASES:
        raise ValueError(f"inventory basis must be one of {INVENTORY_BASES}, got {basis!r}")
    fin = inputs["financials"]
    nb = inputs["company_raw"]["normalised_baseline"]
    mines = fin["guidance_fy27"]["mines"]
    f0 = nb["stub_years"]
    first_fy = _fy_index(nb["valuation_date"])
    out: Dict[str, Dict[str, float]] = {}
    for name, g in mines.items():
        gold_rate, cu_rate = _mid(g["gold_koz"]), _mid(g["copper_kt"])
        if basis in ("stated_life", "life_extension"):
            years = f0 + (fin["stated_mine_life_end_fy"][name] - first_fy)
            if basis == "life_extension":
                years += nb["inventory"]["life_extension_years"]
            out[name] = {"gold_koz": gold_rate * years, "copper_kt": cu_rate * years}
        else:
            res = fin["ore_reserves_2025_12_31"][name]
            rec = nb["inventory"]["default_metallurgical_recovery"]
            made = fin["production_since_reserve_date"]
            out[name] = {
                "gold_koz": res["gold_moz"] * _KOZ_PER_MOZ * rec - made["gold_koz"].get(name, 0.0),
                "copper_kt": res["copper_kt"] * rec - made["copper_kt"].get(name, 0.0),
            }
    return out


def project_uplifts_from_data(inputs: dict, hosts: List[MineInputs], g: dict) -> List[MineInputs]:
    """Declared project uplifts as late-starting mines (method paper §5.3).

    Each uplift names a host mine, a first fiscal year, a life (years, or the host's
    remaining life) and annual metal. ``cost_basis``:

    - ``host_unit_cost``: new ore at the host's cost per A$ of guidance revenue
      (sustaining and mine development scaled the same way); project capital is already
      in the host's ``major_project_capex``.
    - ``incremental_recovery``: more metal from the same ore; the only extra cost is the
      royalty on it.
    """
    nb = inputs["company_raw"]["normalised_baseline"]
    pb = g["price_basis"]
    first_fy = _fy_index(nb["valuation_date"])
    f0 = nb["stub_years"]
    by_name = {m.name: m for m in hosts}
    out: List[MineInputs] = []
    for u in nb.get("project_uplifts") or []:
        host = by_name[u["host"]]
        start = u["start_fy"] - first_fy
        if u["years"] == "host_life":
            # The host stops when its FIRST metal runs out (ore-driven), so its life is
            # the shorter of the metal lives, not the longer.
            lives = [inv / rate for inv, rate in ((host.inventory_gold_koz, host.gold_koz_pa),
                                                  (host.inventory_copper_kt, host.copper_kt_pa)) if rate]
            host_years = min(lives)
            years = host_years - (f0 + start - 1)
        else:
            years = float(u["years"])
        if "fraction_of_host" in u:
            gold = host.gold_koz_pa * u["fraction_of_host"]["gold"]
            cu = host.copper_kt_pa * u["fraction_of_host"]["copper"]
        else:
            gold, cu = u["gold_koz_pa"], u["copper_kt_pa"]
        rev_u = gold * pb["gold_aud_oz"] + cu * pb["copper_aud_t"]
        if u["cost_basis"] == "host_unit_cost":
            rev_h = host.gold_koz_pa * pb["gold_aud_oz"] + host.copper_kt_pa * pb["copper_aud_t"]
            ratio = rev_u / rev_h
            gross_h = host.aisc_aud_oz * host.gold_koz_pa + host.copper_kt_pa * pb["copper_aud_t"]
            gross_u = gross_h * ratio
            sustaining, development = host.sustaining_capex * ratio, host.mine_development * ratio
        elif u["cost_basis"] == "incremental_recovery":
            gross_u = inputs_royalty_rate(inputs) * rev_u   # royalty only, at guidance prices
            sustaining = development = 0.0
        else:
            raise ValueError(f"unknown uplift cost_basis {u['cost_basis']!r}")
        aisc = (gross_u - cu * pb["copper_aud_t"]) / gold if gold else 0.0
        out.append(MineInputs(
            name=f"{u['host']}:{u['name']}", gold_koz_pa=gold, copper_kt_pa=cu,
            inventory_gold_koz=gold * years, inventory_copper_kt=cu * years,
            aisc_aud_oz=aisc, sustaining_capex=sustaining, mine_development=development,
            exploration=0.0, da_aud_oz=host.da_aud_oz, project_capex=[],
            stream_delivered_fraction=host.stream_delivered_fraction,
            stream_cash_fraction_of_spot=host.stream_cash_fraction_of_spot,
            start_period=start,
        ))
    return out


def inputs_royalty_rate(inputs: dict) -> float:
    return royalty_rate_from_data(inputs["financials"])


def resource_wacc_from_data(inputs: dict) -> WaccBuild:
    fin = inputs["financials"]
    wb = inputs["company_raw"]["normalised_baseline"]["wacc_build"]
    obs = fin["wacc_observed_inputs"]
    rf = obs["risk_free_rate"]
    equity = fin["market_data"]["price_aud"] * fin["share_statistics"]["shares_outstanding"]
    return WaccBuild(
        risk_free_rate=rf, equity_risk_premium=wb["equity_risk_premium"], beta=wb["beta"],
        cost_of_debt_pretax=rf + wb["cost_of_debt_spread"], tax_rate=wb["tax_rate"],
        equity_market_value=equity, debt_market_value=fin["debt"]["uspp_hedged_aud_m"],
    )


def resource_equity_bridge_from_data(inputs: dict) -> EquityBridge:
    fin = inputs["financials"]
    nb = inputs["company_raw"]["normalised_baseline"]["equity_bridge"]
    dm = fin["derived_metrics"]
    bs = fin["latest_balance_sheet"]  # dated by its `date` field; the translator names no date
    net_debt = -dm["net_cash_at_anchor"] + dm["final_dividend_unpaid_at_anchor"]
    adjustments = bs["rehabilitation_provision"] if nb["deduct_rehabilitation_provision"] else 0.0
    if nb["deduct_stream_deferred_revenue"]:
        adjustments += bs["stream_deferred_revenue"]
    leases = bs["lease_liabilities"] if nb["deduct_lease_liabilities"] else 0.0
    return EquityBridge(
        net_debt_at_valuation=net_debt, equity_bridge_adjustments_net=adjustments,
        lease_liabilities=leases, shares_outstanding=fin["share_statistics"]["shares_outstanding"],
        market_reference_price=fin["market_data"]["price_aud"],
    )


def _link_note(params: Optional[dict]) -> List[str]:
    if params is None:
        return []
    return [f"Cost-price link (D-104): {params['elasticity_per_10pct']}% per 10% real move in the "
            f"primary commodity, lag {params['lag_years']}y, cap +{params['cap_above_base_pct']}%, "
            f"{'symmetric' if params['symmetric'] else 'upward only'}."]


def build_resource_inputs_from_data(
    inputs: dict, scenario_id: str, basis: Optional[str] = None,
    wacc_override: Optional[float] = None, gold_scale: float = 1.0,
    flat_real: Optional[Dict[str, float]] = None,
    cost_link_override: Optional[Dict[str, float]] = None,
) -> ResourceEngineInputs:
    """Assemble one company x scenario. ``basis`` defaults to the declared inventory
    basis; the alternatives exist for the sized sensitivities. ``gold_scale`` multiplies
    the whole gold path and exists only for the market-implied disclosure; the D-104 cost
    link reads the scaled path against the UNscaled period-0 price, so a path held above
    today's price carries the cost response to it. ``cost_link_override`` replaces D-104
    fields (``elasticity_per_10pct`` and so on) for the sized sensitivities."""
    fin = inputs["financials"]
    company_raw = inputs["company_raw"]
    nb = company_raw["normalised_baseline"]
    if nb.get("engine") != "resource":
        raise ValueError(f"{company_raw['company_position']['id']}: normalised_baseline.engine is not 'resource'")
    basis = basis or nb["inventory"]["basis"]
    g = fin["guidance_fy27"]
    inv = inventories_from_data(inputs, basis)
    stream = fin["northparkes_stream"] if "northparkes_stream" in fin else None
    runoff = nb["project_capex_runoff"]

    mines: List[MineInputs] = []
    for name, m in g["mines"].items():
        project = _mid(m["major_project_capex"])
        sd = sc = 0.0
        if stream is not None and name == stream.get("mine", "northparkes"):
            sd = stream["gold_delivered_fraction_of_attributable"]
            sc = stream["cash_received_fraction_of_spot"]
        mines.append(MineInputs(
            name=name, gold_koz_pa=_mid(m["gold_koz"]), copper_kt_pa=_mid(m["copper_kt"]),
            inventory_gold_koz=inv[name]["gold_koz"], inventory_copper_kt=inv[name]["copper_kt"],
            aisc_aud_oz=_mid(m["aisc_aud_oz"]), sustaining_capex=_mid(m["sustaining_capex"]),
            mine_development=_mid(m["major_mine_development"]), exploration=_mid(m["exploration"]),
            da_aud_oz=_mid(m["da_aud_oz"]), project_capex=[project * x for x in runoff],
            stream_delivered_fraction=sd, stream_cash_fraction_of_spot=sc,
        ))
    mines.extend(project_uplifts_from_data(inputs, mines, g))
    periods = 1 + max(int(nb["horizon_years"]), 1)
    # enough periods for the longest-lived mine on any basis
    longest = max(
        mm.start_period + max((mm.inventory_gold_koz / mm.gold_koz_pa) if mm.gold_koz_pa else 0.0,
                              (mm.inventory_copper_kt / mm.copper_kt_pa) if mm.copper_kt_pa else 0.0)
        for mm in mines
    )
    periods = max(periods, int(longest) + 2)
    paths = price_and_cost_paths(inputs, scenario_id, periods, flat_real)
    # The link reads the (possibly scaled) path against the UNscaled period-0 real price:
    # the cost base is struck at today's price, so a path held above it carries a response.
    scaled = dict(paths, primary_aud=[p * gold_scale for p in paths["primary_aud"]])
    link = cost_price_link_from_paths(inputs, scaled, cost_link_override,
                                      reference=paths["primary_aud"][0] / paths["cpi_index"][0])
    wacc = wacc_override if wacc_override is not None else resource_wacc_from_data(inputs)
    wci = working_capital_intensity_from_data(inputs).result
    return ResourceEngineInputs(
        company_id=company_raw["company_position"]["id"], scenario_id=scenario_id,
        functional_currency=company_raw["company_position"]["functional_currency"],
        horizon_years=int(nb["horizon_years"]), stub_years=nb["stub_years"], mines=mines,
        gold_aud_oz=[p * gold_scale for p in paths["gold_aud_oz"]],
        copper_aud_t=paths["copper_aud_t"], cost_index=paths["cost_index"],
        guidance_gold_aud_oz=g["price_basis"]["gold_aud_oz"],
        guidance_copper_aud_t=g["price_basis"]["copper_aud_t"],
        royalty_rate=royalty_rate_from_data(fin), tax_rate=fin["statutory_tax_rate"],
        corporate_cost_aud_oz=_mid(g["corporate_aisc_aud_oz"]),
        greenfields_exploration=_mid(g["greenfields_exploration"]),
        working_capital_intensity=wci, wacc=wacc,
        equity_bridge=resource_equity_bridge_from_data(inputs),
        notes=[f"Inventory basis: {basis}."] + _link_note(cost_price_link_params(inputs, cost_link_override)),
        cost_price_link=link,
    )
