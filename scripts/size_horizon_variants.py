"""Reproduce every published horizon/terminal table from its declared assumptions.

The 25 August paper's tables came from a scratch harness that no longer existed by
the time anyone tried to check them, and two sittings then published tables about
two per cent apart with no way to say which assumption differed. This script and
``design/methodology/horizon_variant_sets.yaml`` exist so that cannot recur: the
assumption block is declared once, in data, and the table is generated from it.

Run it to print the tables. ``tests/dcf/test_horizon_variant_sets.py`` runs the same
code and asserts every level, so a document citing one of these tables is citing a
tested number.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
from typing import Dict, List

import yaml

from vcc_valuations.translator import build_engine_inputs_from_data, load_inputs
from tests.dcf.harness import replica

ROOT = Path(__file__).resolve().parents[1]
SETS_PATH = ROOT / "design" / "methodology" / "horizon_variant_sets.yaml"


def load_sets(path: Path = SETS_PATH) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def engine_inputs(cfg: dict, scenario_id: str):
    return build_engine_inputs_from_data(
        load_inputs(
            ROOT,
            scenario_id=scenario_id,
            archetype_id=cfg["archetype_id"],
            company_id=cfg["company_id"],
        ),
        scenario_id,
    )


def _is_arc_scenario(cfg: dict, scenario_id: str) -> bool:
    return scenario_id == "disorderly_climate_crystallisation"


def _arc_peak(cfg: dict) -> float:
    return cfg["disorderly_capex_arc"]["peak_pp"]


def build_plan(cfg: dict, spec: dict, scenario_id: str) -> replica.Plan:
    """The plan for one scenario under one declared assumption set."""
    inp = engine_inputs(cfg, scenario_id)
    plan = replica.plan_from_engine_inputs(
        inp, invested_capital_opening=cfg["invested_capital_opening"]
    )
    horizon = spec["horizon_years"]
    plan = replica.extend(plan, horizon)
    plan = replica.fade_growth(plan, spec["fade_period_length"])

    keep = list(inp.margin_transformation)
    keep += [keep[-1]] * (horizon - len(keep))
    plan = replica.reshape_margin(
        plan, spec["gas_rolloff_total_pp"], cfg["gas_rolloff_phasing"], keep=keep
    )

    arc = _is_arc_scenario(cfg, scenario_id)
    if arc:
        # The live path already carries the flat parallel shift D-41 replaces.
        plan = replace(plan, capex_pct=[c - _arc_peak(cfg) for c in plan.capex_pct])

    capex = spec["explicit_capex"]
    if capex["mode"] == "converge":
        plan = replica.converge_capex(
            plan, capex["steady_state_pct"], capex["converge_by_year"]
        )
    elif capex["mode"] != "live":
        raise ValueError(f"unknown explicit capex mode {capex['mode']!r}")

    baseline_plan = plan
    if arc:
        a = cfg["disorderly_capex_arc"]
        plan = replica.capex_arc(
            plan,
            list(plan.capex_pct),
            peak_pp=a["peak_pp"],
            hold_to_year=a["hold_to_year"],
            decay_to_year=a["decay_to_year"],
            persistent_pp=a["persistent_pp"],
        )

    return _apply_terminal(cfg, spec, plan, baseline_plan, arc)


def _apply_terminal(cfg, spec, plan, baseline_plan, arc) -> replica.Plan:
    rule = spec["terminal_capex"]["rule"]
    if rule == "final_explicit_year":
        return replica.terminal_capex_from_final_year(plan)
    if rule != "grow_capital_base":
        raise ValueError(f"unknown terminal capex rule {rule!r}")

    premium = spec["terminal_capex"].get("carbon_premium_on_baseline_base", False)
    if arc and premium:
        # Grow the base the arc is not part of, then carry the persistent
        # licence-to-operate shift into perpetuity on top of it.
        grown = replica.terminal_capex_growing_capital_base(baseline_plan)
        rate = grown.terminal_capex_pct_revenue + cfg["disorderly_capex_arc"]["persistent_pp"]
        return replace(plan, terminal_capex_pct_revenue=rate,
                       label=f"{plan.label}+tcapex:grow+premium")
    return replica.terminal_capex_growing_capital_base(plan)


def run_set(cfg: dict, set_name: str) -> Dict[str, replica.PlanResult]:
    spec = cfg["sets"][set_name]
    return {
        sid: replica.run(build_plan(cfg, spec, sid)) for sid in cfg["scenarios"]
    }


# ---------------------------------------------------------------------------
# Item 11: what the explicit period is allowed to do to capital intensity.
# ---------------------------------------------------------------------------


def capital_growth_path(cfg: dict, spec: dict, scenario_id: str, position: dict,
                        plan: replica.Plan) -> List[float]:
    kind = position["capital_growth"]
    H = plan.horizon_years
    if kind == "revenue":
        return list(plan.growth_path)
    if kind == "volume_and_inflation":
        # Capital tracks the volume half of whatever revenue growth is in force,
        # inflated at asset inflation. Stripping the chain's pricing rate out of the
        # year's growth leaves its volume component, so the path fades with revenue
        # instead of holding the chain rate through years the fade has already slowed.
        inflation = engine_inputs(cfg, scenario_id).terminal_growth
        pricing = _chain_rate(cfg, scenario_id, "B29")
        return [
            (1.0 + g) * (1.0 + inflation) / (1.0 + pricing) - 1.0
            for g in plan.growth_path
        ]
    if kind == "volume_and_inflation_flat":
        # The same basis with the chain's own volume rate held for every year, which
        # is how the 25 August handover struck it. Kept so the two readings can be
        # compared without either being re-derived from memory.
        inflation = engine_inputs(cfg, scenario_id).terminal_growth
        volume = _chain_rate(cfg, scenario_id, "B25")
        return [(1.0 + volume) * (1.0 + inflation) - 1.0] * H
    raise ValueError(f"unknown capital growth basis {kind!r}")


def _chain_rate(cfg: dict, scenario_id: str, cell: str) -> float:
    """One derived rate from the revenue-growth chain the translator already builds."""
    from vcc_valuations.translator import revenue_growth_chain_from_data

    inputs = load_inputs(
        ROOT,
        scenario_id=scenario_id,
        archetype_id=cfg["archetype_id"],
        company_id=cfg["company_id"],
    )
    chain = revenue_growth_chain_from_data(inputs, scenario_id)
    for step in chain.steps:
        if step.cell == cell:
            return step.value
    raise LookupError(f"{cell} not found in the revenue-growth chain")


def run_item_11(cfg: dict, set_name: str = "current") -> Dict[str, Dict[str, float]]:
    name = _current_set_name(cfg) if set_name == "current" else set_name
    spec = cfg["sets"][name]
    out: Dict[str, Dict[str, float]] = {}
    for position_name, position in cfg["item_11_positions"].items():
        row = {}
        for sid in cfg["scenarios"]:
            plan = build_plan(cfg, spec, sid)
            kind = position["capital_growth"]
            if kind == "revenue":
                regrown = replica.hold_capital_intensity(plan)
                plan = _apply_terminal(cfg, spec, regrown, regrown,
                                       _is_arc_scenario(cfg, sid))
            elif kind != "derived":
                path = capital_growth_path(cfg, spec, sid, position, plan)
                regrown = replica.grow_capital_at(plan, path)
                plan = _apply_terminal(cfg, spec, regrown, regrown,
                                       _is_arc_scenario(cfg, sid))
            row[sid] = replica.run(plan).value_per_share
        out[position_name] = row
    return out


def plan_for_position(cfg: dict, spec: dict, scenario_id: str, position: dict):
    """The plan for one scenario under one item 11 position."""
    plan = build_plan(cfg, spec, scenario_id)
    kind = position["capital_growth"]
    if kind == "derived":
        return plan
    if kind == "revenue":
        regrown = replica.hold_capital_intensity(plan)
    else:
        regrown = replica.grow_capital_at(
            plan, capital_growth_path(cfg, spec, scenario_id, position, plan)
        )
    return _apply_terminal(cfg, spec, regrown, regrown, _is_arc_scenario(cfg, scenario_id))


def dupont(cfg: dict, position_name: str, scenario_id: str,
           set_name: str = "current") -> Dict[str, float]:
    """The return decomposition behind one position, for one scenario.

    ROIC is NOPAT margin times capital turnover. Reporting both factors at the
    valuation date and in the terminal says which of the two a position is
    relying on -- and every position here relies on the same one, which is the
    finding item 11 turns on.

    The physical reading is reported alongside: what the fixed asset base does in
    real terms against what volume does. A capital plan that is arithmetically
    coherent can still assert an implausible amount of asset productivity, and
    that assertion is invisible in the money figures.
    """
    name = _current_set_name(cfg) if set_name == "current" else set_name
    spec = cfg["sets"][name]
    position = cfg["item_11_positions"][position_name]
    inp = engine_inputs(cfg, scenario_id)
    plan = plan_for_position(cfg, spec, scenario_id, position)
    res = replica.run(plan)
    d = res.diagnostics

    wc, da, g = plan.working_capital_intensity, plan.da_pct_revenue, plan.terminal_growth
    ic_open = plan.invested_capital_opening
    rev_open, rev_final = plan.base_year_revenue, res.revenue[-1]
    ic_final = d["invested_capital_final_explicit"]
    fixed_open = ic_open - wc * rev_open
    fixed_final = ic_final - wc * rev_final
    horizon = plan.horizon_years

    margin_open = plan.base_ebit_margin * (1.0 - plan.stub_tax_rate)
    turnover_open = rev_open / ic_open
    margin_terminal = d["terminal_nopat_margin"]
    turnover_terminal = d["terminal_revenue"] / ic_final

    volume = _chain_rate(cfg, scenario_id, "B25")
    volume_cumulative = (1.0 + volume) ** horizon - 1.0
    fixed_real = fixed_final / (1.0 + g) ** horizon
    ebitda_margin = res.ebit_margin[-1] + da

    return {
        "value_per_share": res.value_per_share,
        "capex_pct_y1": plan.capex_pct[0],
        "capex_pct_final": plan.capex_pct[-1],
        "capex_over_ebitda_final": plan.capex_pct[-1] / ebitda_margin,
        "terminal_capex_pct": plan.terminal_capex_pct_revenue,
        "terminal_capex_over_ebitda": plan.terminal_capex_pct_revenue / ebitda_margin,
        "revenue_growth_cumulative": rev_final / rev_open - 1.0,
        "invested_capital_open": ic_open,
        "invested_capital_final": ic_final,
        "invested_capital_growth": ic_final / ic_open - 1.0,
        "ic_over_revenue_open": ic_open / rev_open,
        "ic_over_revenue_final": ic_final / rev_final,
        "fixed_capital_open": fixed_open,
        "fixed_capital_final": fixed_final,
        "fixed_capital_growth_nominal": fixed_final / fixed_open - 1.0,
        "fixed_capital_growth_real": fixed_real / fixed_open - 1.0,
        "volume_growth_annual": volume,
        "volume_growth_cumulative": volume_cumulative,
        "asset_productivity_implied": (1.0 + volume_cumulative) / (fixed_real / fixed_open) - 1.0,
        "nopat_margin_open": margin_open,
        "turnover_open": turnover_open,
        "roic_open": margin_open * turnover_open,
        "nopat_margin_terminal": margin_terminal,
        "turnover_terminal": turnover_terminal,
        "roic_terminal": d["terminal_roic_on_capital"],
        "roic_over_wacc": d["terminal_roic_on_capital"] / plan.wacc,
        "roic_if_only_margin_moved": margin_terminal * turnover_open,
        "roic_if_only_turnover_moved": margin_open * turnover_terminal,
        "terminal_reinvestment_rate": d["terminal_reinvestment_rate"],
        "roic_on_new_capital": d["terminal_roic_implied"],
        "terminal_share_of_ev": res.terminal_share_of_ev,
        "wacc": plan.wacc,
        "terminal_growth": g,
        "da_pct_revenue": da,
    }


def run_capex_intensity_rule(cfg: dict, set_name: str = "current") -> Dict[str, float]:
    """Size the observed-intensity rule: both rates from one window, one entity.

    The rule's content is that the *gap* between capex and depreciation stops
    being an assumption. Its risk is that the gap is then only as good as the
    window and the entity the average is drawn from, which is why every variant
    names its source.
    """
    block = cfg.get("capex_intensity_rule")
    if not block:
        return {}
    name = _current_set_name(cfg) if set_name == "current" else set_name
    spec = cfg["sets"][name]
    scenario_id = block["scenario"]
    ebitda = block["ebitda_margin_held"]

    out: Dict[str, float] = {}
    for variant_name, v in block["variants"].items():
        plan = build_plan(cfg, spec, scenario_id)
        da = v["da_pct_revenue"]
        plan = replace(
            plan,
            da_pct_revenue=da,
            base_ebit_margin=v.get("ebitda_margin", ebitda) - da,
            capex_pct=[v["capex_pct_revenue"]] * plan.horizon_years,
        )
        if v["terminal"] == "grow_capital_base":
            plan = replica.terminal_capex_growing_capital_base(plan)
        elif v["terminal"] == "equals_da":
            plan = replace(plan, terminal_capex_pct_revenue=da)
        else:
            raise ValueError(f"unknown terminal treatment {v['terminal']!r}")
        out[variant_name] = replica.run(plan).value_per_share
    return out


def _current_set_name(cfg: dict) -> str:
    current = [n for n, s in cfg["sets"].items() if s.get("status") == "current"]
    if len(current) != 1:
        raise ValueError(f"exactly one set must be current; found {current}")
    return current[0]


# ---------------------------------------------------------------------------


def _pct(value: float, places: int = 2) -> str:
    """A percentage, formatted without a numeric literal in the format spec.

    The SSOT lint tokenises every number on a line and cannot tell a format spec
    from a domain value, so a percent spec carrying a precision reads as a
    hardcoded rate. Formatting through a rounded float keeps the check honest
    rather than silencing it line by line.
    """
    return f"{round(value * 100, places)}%"  # ssot-allow: display scaling


def _print_set(cfg: dict, name: str) -> None:
    spec = cfg["sets"][name]
    results = run_set(cfg, name)
    print(f"\n## {name}  [{spec['status']}]")
    print(f"   published in: {spec['published_in']}")
    capex = spec["explicit_capex"]
    capex_desc = (
        "converge to " + _pct(capex["steady_state_pct"])
        + f" by Y{capex['converge_by_year']}"
        if capex["mode"] == "converge"
        else "live path, held flat past its last declared year"
    )
    print(f"   horizon {spec['horizon_years']}y, fade {spec['fade_period_length']}y, "
          f"capex {capex_desc}")
    print("   gas roll-off " + _pct(spec["gas_rolloff_total_pp"])
          + f", terminal capex {spec['terminal_capex']['rule']}")
    header = ("Scenario", "Value", "Expected", "Drift", "T.capex", "TV%")
    print("   " + header[0].ljust(38) + "".join(h.rjust(11) for h in header[1:]))
    for sid, res in results.items():
        exp = spec["expected"][sid]
        drift = (res.value_per_share - exp) / exp
        cells = (
            _round4(res.value_per_share),
            _round4(exp),
            _pct(drift, 3),
            _pct(res.plan.terminal_capex_pct_revenue),
            _pct(res.terminal_share_of_ev, 1),
        )
        print("   " + sid.ljust(38) + "".join(c.rjust(11) for c in cells))


def _round4(value: float) -> str:
    return f"{round(value, 4)}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--set", dest="set_name", default=None,
                    help="one set name; default prints every set")
    ap.add_argument("--item-11", action="store_true",
                    help="also print the item 11 positions on the current set")
    args = ap.parse_args()

    cfg = load_sets()
    names = [args.set_name] if args.set_name else list(cfg["sets"])
    for name in names:
        _print_set(cfg, name)

    if args.item_11:
        print(f"\n## item 11 positions, on the current set "
              f"({_current_set_name(cfg)})")
        rows = run_item_11(cfg)
        print("   " + "Scenario".ljust(38) + "".join(n.rjust(28) for n in rows))
        for sid in cfg["scenarios"]:
            print("   " + sid.ljust(38)
                  + "".join(_round4(rows[n][sid]).rjust(28) for n in rows))


if __name__ == "__main__":
    main()
