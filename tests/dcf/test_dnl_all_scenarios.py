"""DNL — all six scenarios assembled from data (M2 scenario roll-out).

Each scenario is built end-to-end via ``build_engine_inputs_from_data`` from the
``by_scenario`` macro + operating deltas over the shared baseline. The per-scenario
DRIVERS (revenue growth, Y5 EBIT margin) tie the ``dnl_scenarios_comparison_v4``
workbook to the cent; the per-share LEVELS are the engine's own output at the
ratified WACC (beta 1.10), which supersede that workbook's stale (beta-0.95)
per-share numbers exactly as MT's 3.073 superseded 3.484.

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
WORKBOOK = {
    "muddle_through":                     (0.0615, 0.146, 0.0250),
    "orderly_convergence":                (0.0744, 0.151, 0.0275),
    "ai_productivity_lag":                (0.0555, 0.151, 0.0225),
    "fragmentation":                      (0.0630, 0.116, 0.0225),
    "disorderly_climate_crystallisation": (0.0756, 0.116, 0.0175),
    "stagflation_persists":               (0.0549, 0.071, 0.0225),
}


def _run(scenario: str):
    inp = load_inputs(ROOT, scenario, "industrial_explosives", "dnl")
    built = build_engine_inputs_from_data(inp, scenario)
    return inp, built, FcfEngine().run(built)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_scenario_drivers_tie_the_comparison_workbook(scenario):
    """Revenue growth, Y5 EBIT margin and terminal growth reproduce the v4 workbook."""
    inp, built, r = _run(scenario)
    wb_growth, wb_y5_margin, wb_terminal = WORKBOOK[scenario]
    assert abs(revenue_growth_from_data(inp, scenario) - wb_growth) < 5e-5
    assert abs(r.ebit_margin[-1] - wb_y5_margin) < 5e-4         # Y5 (last explicit) margin
    assert abs(built.terminal_growth - wb_terminal) < 1e-9


def test_muddle_through_is_the_ratified_headline():
    _, _, r = _run("muddle_through")
    assert round(r.value_per_share, 3) == 3.073


def test_scenario_asymmetry_is_downside_skewed():
    """Per-share ordering is upside -> downside, and the downside bites harder than
    the upside lifts (the framework's central claim about DNL)."""
    vps = {s: _run(s)[2].value_per_share for s in SCENARIOS}
    assert (
        vps["orderly_convergence"]
        > vps["muddle_through"]
        > vps["ai_productivity_lag"]
        > vps["fragmentation"]
        > vps["disorderly_climate_crystallisation"]
        > vps["stagflation_persists"]
    )
    mt = vps["muddle_through"]
    upside = vps["orderly_convergence"] - mt
    downside = mt - vps["stagflation_persists"]
    assert downside > 3.0 * upside          # asymmetry ~4x (v4 workbook: 4.05x)
    assert all(v > 0 for v in vps.values())  # every scenario still yields positive equity


def test_single_wacc_held_across_scenarios():
    """Single-discount-rate discipline: the WACC is identical across all six."""
    waccs = {round(_run(s)[2].wacc, 6) for s in SCENARIOS}
    assert len(waccs) == 1
    assert abs(next(iter(waccs)) - 0.088772) < 1e-4
