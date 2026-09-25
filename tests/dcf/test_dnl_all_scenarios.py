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
def test_scenario_drivers_tie_the_comparison_workbook(scenario):
    """Revenue growth and terminal growth still reproduce the v4 workbook.

    The Y5 EBIT margin no longer ties, and is not checked here: D-69
    (25 Sept 2026) revised DNL's gas roll-off from a flat -1.5pp (D-40, the
    basis the v4 workbook was struck on) to a deeper, later-phased -2.0pp by
    FY2032. That moves every scenario's Y5 margin down by the same ~0.5pp
    parallel shift, since the roll-off revision applies uniformly -- D-69
    working as intended, not a data error. D-35 also means Y5 is no longer
    the last explicit year (the horizon extended to Y6), so ``r.ebit_margin``
    is not indexed by ``-1`` here even for the checks that remain.
    """
    inp, built, r = _run(scenario)
    wb_growth, _wb_y5_margin, wb_terminal = WORKBOOK[scenario]
    assert abs(revenue_growth_from_data(inp, scenario) - wb_growth) < 5e-5
    assert abs(built.terminal_growth - wb_terminal) < 1e-9


def test_muddle_through_is_the_ratified_headline():
    """1.846, not 1.989: D-35/D-36 (25 Sept 2026) extended the horizon to Y6 and
    faded revenue growth to g, D-69 deepened the gas roll-off, and the D-49
    terminal-capex roll-forward fix (same day) made that roll-forward compound
    on D-36's actual per-year fade path instead of a re-flattened rate -- see
    test_dnl_mt_from_data.py for the full derivation."""
    _, _, r = _run("muddle_through")
    assert round(r.value_per_share, 3) == 1.846


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
    assert (
        vps["orderly_convergence"]
        > vps["ai_productivity_lag"]
        > vps["muddle_through"]
        > vps["fragmentation"]
        > vps["disorderly_climate_crystallisation"]
        > vps["stagflation_persists"]
    )
    mt = vps["muddle_through"]
    upside = vps["orderly_convergence"] - mt
    downside = mt - vps["stagflation_persists"]
    assert downside > 3.0 * upside          # asymmetry ~6.0x post D-35/D-36/D-69 (v4 workbook: 4.05x)
    # Stagflation Persists crossed to negative equity value under D-35/D-36/D-69
    # (25 Sept 2026): the extra year of margin compression and gas roll-off, on
    # top of the fade to g, is now enough to take the scenario through zero.
    # That is the model finding this asymmetry test exists to surface, not a
    # bug -- so every OTHER scenario still yields positive equity, and only
    # Stagflation (already the worst case, and already the closest to zero
    # before this change) is allowed through it.
    assert all(v > 0 for s, v in vps.items() if s != "stagflation_persists")
    assert vps["stagflation_persists"] < 0


def test_single_wacc_held_across_scenarios():
    """Single-discount-rate discipline: the WACC is identical across all six."""
    waccs = {round(_run(s)[2].wacc, 6) for s in SCENARIOS}
    assert len(waccs) == 1
    assert abs(next(iter(waccs)) - 0.088772) < 1e-4
