"""DNL — all six scenarios assembled from data (M2 scenario roll-out).

Each scenario is built end-to-end via ``build_engine_inputs_from_data`` from the
``by_scenario`` macro + operating deltas over the shared baseline. The per-scenario
DRIVERS (revenue growth, Y5 EBIT margin) tie the ``dnl_scenarios_comparison_v4``
workbook to the cent; the per-share LEVELS are the engine's own output at the
ratified WACC (beta 1.10), which supersede that workbook's stale (beta-0.95)
per-share numbers exactly as MT's 3.073 superseded 3.484, and as 2.831
superseded 3.073 when reinvestment was normalised (D-13, 23 Aug 2026).

Scenario margin/capex deltas are applied as a PARALLEL SHIFT across the explicit
years (owner decision, 12 Aug 2026).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vcc_valuations.translator import (
    load_inputs,
    build_engine_inputs_from_data,
    revenue_growth_from_data,
)
from vcc_valuations.dcf.fcf_engine import FcfEngine

ROOT = Path(__file__).resolve().parents[2]

SCENARIOS = [
    "muddle_through",
    "orderly_convergence",
    "ai_productivity_lag",
    "fragmentation",
    "disorderly_climate_crystallisation",
    "stagflation_persists",
]

# dnl_scenarios_comparison_v4 Inputs sheet: (revenue growth row 26, Y5 EBIT margin
# row 27, applied terminal growth DCF-Outputs row 13).
# Y5 margins re-pinned 14 September 2026: the base EBIT margin was restated from
# 14.10% to 12.72% under D-48 and D-50, so every scenario's Y5 margin falls by the
# same 1.38pp. Revenue growth and terminal growth are untouched, which is the
# check that the restatement moved the margin and nothing else. Previous margins
# were 0.146 / 0.151 / 0.151 / 0.116 / 0.116 / 0.071.
WORKBOOK = {
    "muddle_through":                     (0.0615, 0.1357, 0.0250),
    "orderly_convergence":                (0.0744, 0.1407, 0.0275),
    "ai_productivity_lag":                (0.0555, 0.1407, 0.0225),
    "fragmentation":                      (0.0630, 0.1057, 0.0225),
    "disorderly_climate_crystallisation": (0.0756, 0.1057, 0.0175),
    "stagflation_persists":               (0.0549, 0.0607, 0.0225),
}


def _run(scenario: str):
    inp = load_inputs(ROOT, scenario, "industrial_explosives", "dnl")
    built = build_engine_inputs_from_data(inp, scenario)
    return inp, built, FcfEngine().run(built)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_scenario_drivers_are_derived_from_the_scenario_not_the_v4_workbook(scenario):
    """D-72 (2 Oct 2026) retired the v4-workbook tie on growth and terminal g.

    The v4 Inputs sheet supplied flat per-scenario scalars; they survive as the
    LEVEL anchors the derived mining and gas paths are calibrated to (asserted
    in tests/test_macro_driver_paths.py). The chain now reads the scenario's
    own year-anchored series -- DM inflation is the scenario CPI, ~0.5pp above
    the old "through-cycle" value on the central scenarios, so year-1 growth
    sits above the v4 figure by 0.7 x that gap, by construction. Terminal g is
    derived (equilibrium chain, capped at scenario nominal GDP), not the typed
    number the WORKBOOK tuple carries.
    """
    from vcc_valuations.translator import (
        chain_macro_at, macro_series_at, terminal_growth_from_data,
    )
    inp, built, r = _run(scenario)
    wb_growth, _wb_y5_margin, wb_terminal = WORKBOOK[scenario]
    # The chain's inputs at year 1 ARE the scenario series at year 1.
    m = chain_macro_at(inp, 1)
    assert m["dm_inflation"] == pytest.approx(macro_series_at(inp, "cpi_inflation_advanced", 1))
    assert m["global_mining_real_growth"] == pytest.approx(
        macro_series_at(inp, "global_mining_real_growth", 1))
    # Terminal g is derived and capped, and is no longer the typed v4 number.
    tg = terminal_growth_from_data(inp, scenario, built.horizon_years)
    assert built.terminal_growth == pytest.approx(tg.result)
    assert built.terminal_growth <= tg["g_cap"].value + 1e-12
    assert built.terminal_growth != pytest.approx(wb_terminal, abs=1e-4)
    assert 0.03 <= built.terminal_growth <= 0.06        # the range Stephen set, 2 Oct 2026
    # The year-1 chain moved off the v4 growth by the DM-inflation basis change only
    # where the scenario series differ from the old anchors; it is not pinned to v4.
    assert abs(revenue_growth_from_data(inp, scenario) - wb_growth) < 0.02


def test_muddle_through_is_the_ratified_headline():
    """1.846, not 1.989: D-35/D-36 (25 Sept 2026) extended the horizon to Y6 and
    faded revenue growth to g, D-69 deepened the gas roll-off, and the D-49
    terminal-capex roll-forward fix (same day) made that roll-forward compound
    on D-36's actual per-year fade path instead of a re-flattened rate -- see
    test_dnl_mt_from_data.py for the full derivation."""
    _, _, r = _run("muddle_through")
    # 1.942 under D-71 (2 Oct 2026): fixed ten-year horizon, convergence terminal.
    # 2.138 under D-72 (same day): the chain on the scenario's own paths (CPI
    # 3.0% vs the old 2.5% DM-inflation anchor) and a derived 5.27% terminal g.
    assert round(r.value_per_share, 3) == 2.138


def test_scenario_asymmetry_is_downside_skewed():
    """Per-share ordering is upside -> downside, and the downside bites harder than
    the upside lifts (the framework's central claim about DNL).

    AI Productivity Lag and Muddle Through swapped places on 14 September 2026 and
    the swap is a consequence of D-49, not a data error. AI Lag carries +0.5pp of
    margin and a lower terminal growth rate; once terminal capex is depreciation
    plus g times the fixed base, a lower g also means a lower perpetual
    reinvestment call, and that offset is now large enough to outweigh the slower
    growth. Whether the scenario narrative still supports AI Lag sitting above the
    central case is a question for the owner, flagged in WORKING_NOTES.
    """
    vps = {s: _run(s)[2].value_per_share for s in SCENARIOS}
    # D-72 (2 Oct 2026) reordered the downside. Decisions 3 and 4 make
    # Stagflation a CYCLICAL scenario -- its gas spike ends and its margin hit
    # reverts at its own 'resolution' phase (year 5) -- while Fragmentation's
    # duplication costs and Disorderly Climate's carbon cost are STRUCTURAL and
    # persist. So Stagflation is no longer the floor: Disorderly Climate is, and
    # Stagflation sits between Fragmentation and it. AI Lag also drops back
    # below Muddle Through (its lower derived g no longer buys the terminal
    # capex relief it did under a typed 2.25%). Ordering before D-72:
    # OC > AI > MT > Frag > DCC > Stag.
    assert (
        vps["orderly_convergence"]
        > vps["muddle_through"]
        > vps["ai_productivity_lag"]
        > vps["fragmentation"]
        > vps["stagflation_persists"]
        > vps["disorderly_climate_crystallisation"]
    )
    mt = vps["muddle_through"]
    upside = vps["orderly_convergence"] - mt
    downside = mt - min(vps.values())
    assert downside > 2.5 * upside          # asymmetry ~3.0x post D-72 (was ~6x; v4 workbook: 4.05x)
    assert all(v > 0 for v in vps.values())


def test_single_wacc_held_across_scenarios():
    """Single-discount-rate discipline: the WACC is identical across all six."""
    waccs = {round(_run(s)[2].wacc, 6) for s in SCENARIOS}
    assert len(waccs) == 1
    assert abs(next(iter(waccs)) - 0.088772) < 1e-4
