"""D-71: the headline terminal form, and the ratchet on its Gordon fallback.

The framework default is excess-return convergence over the declared decay
horizon. Where no decay horizon has been declared for a company x scenario the
data assembler falls back to Gordon and says so. That fallback is a gap the
five-forces work owes, not a choice, so it is ratcheted here the same way
checks 10, 13 and 14 and the D-42 defence baseline are: a new fallback fails,
and a closed one must leave the baseline.

Only the industrial FCFF engine carries the form today (DNL). The bank and
segment engines strike their terminals as before; declaring decay horizons for
WBC and CSL, and routing them through the same form, is the pass the gap audit
(analyses/dnl/five_forces_driver_gap_audit_2026-09-25.md) describes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vcc_valuations.dcf.fcf_engine import FcfEngine, FcfEngineInputs  # noqa: E402
from vcc_valuations.dcf.terminal_value import two_stage  # noqa: E402
from vcc_valuations.translator import (  # noqa: E402
    build_engine_inputs_from_data, load_inputs, scenario_equilibrium_year,
    terminal_form_from_data,
)

BASELINE = ROOT / "tests" / "terminal_form_baseline.json"
SCENARIOS = ["muddle_through", "orderly_convergence", "ai_productivity_lag",
             "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists"]


def _inputs(scenario):
    return load_inputs(ROOT, scenario, "industrial_explosives", "dnl")


@pytest.fixture(scope="module")
def results():
    return {s: FcfEngine().run(build_engine_inputs_from_data(_inputs(s), s))
            for s in SCENARIOS}


def test_the_explicit_period_is_ten_years_everywhere(results):
    """D-71 supersedes D-35's computed horizon with a fixed ten."""
    for s, r in results.items():
        assert r.horizon_years == 10, s


def test_every_scenario_reaches_its_own_equilibrium_inside_the_explicit_period():
    """D-71's first static-state condition. Fragmentation is the latest, at year 10.

    A scenario whose time_profile reached equilibrium later would need the
    three-phase form D-71 describes and nothing has built; the assembler raises
    rather than capitalising a world mid-transition.
    """
    years = {s: scenario_equilibrium_year(_inputs(s)) for s in SCENARIOS}
    assert max(years.values()) == 10
    assert years["fragmentation"] == 10
    for s, y in years.items():
        assert y <= 10, (s, y)


def test_gordon_fallbacks_are_baselined_and_only_shrink(results):
    found = sorted(f"dnl:{s}" for s, r in results.items() if r.terminal_form == "gordon")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    recorded = sorted(baseline["gordon_fallback"])
    new = sorted(set(found) - set(recorded))
    assert not new, (
        "A valuation fell back to Gordon with no declared decay horizon and is not "
        "baselined (D-71):\n  " + "\n  ".join(new)
        + "\nDeclare an excess_return_defence.decay_horizon on the impact matrix, or add "
          "the pair to tests/terminal_form_baseline.json with a reason."
    )
    stale = sorted(set(recorded) - set(found))
    assert not stale, (
        "Baseline entries no longer fall back -- a decay horizon landed (good, remove "
        "them so the ratchet tightens):\n  " + "\n  ".join(stale)
    )


def test_declared_scenarios_converge_on_the_declared_midpoint(results):
    for s, r in results.items():
        if r.terminal_form != "excess_return_convergence":
            continue
        assert r.convergence_years == pytest.approx(12.5), s   # the 10-15 band's midpoint
        assert r.terminal_invested_capital is not None
        expected = two_stage(r.terminal_invested_capital, r.terminal_earned_return,
                             r.wacc, r.terminal_growth, r.convergence_years)
        assert r.terminal_value == pytest.approx(expected, rel=1e-12), s


def test_convergence_is_symmetric_in_the_excess(results):
    """Disorderly Climate earns below its WACC; it converges UP, and that lifts its terminal.

    The same mechanism in the other direction -- the test that would have
    called this a bug is the one D-71 retired.
    """
    r = results["disorderly_climate_crystallisation"]
    assert r.terminal_form == "excess_return_convergence"
    assert r.terminal_earned_return < r.wacc
    gordon_on_earned = r.terminal_invested_capital * (
        (r.terminal_earned_return - r.terminal_growth) / (r.wacc - r.terminal_growth))
    assert gordon_on_earned < r.terminal_value < r.terminal_invested_capital
    for s in ("muddle_through", "orderly_convergence", "ai_productivity_lag"):
        r = results[s]
        assert r.terminal_earned_return > r.wacc
        gordon_on_earned = r.terminal_invested_capital * (
            (r.terminal_earned_return - r.terminal_growth) / (r.wacc - r.terminal_growth))
        assert r.terminal_invested_capital < r.terminal_value < gordon_on_earned, s


def test_the_simpler_option_is_selectable(results):
    """D-71: Gordon remains a user-selectable option on the same inputs."""
    import dataclasses
    inp = build_engine_inputs_from_data(_inputs("muddle_through"), "muddle_through")
    assert inp.terminal_form == "excess_return_convergence"
    gordon = FcfEngine().run(dataclasses.replace(inp, terminal_form="gordon",
                                                 convergence_years=None))
    assert gordon.terminal_form == "gordon"
    assert gordon.value_per_share == pytest.approx(2.2288, abs=5e-4)
    assert gordon.value_per_share > results["muddle_through"].value_per_share


def test_the_form_is_declared_not_defaulted_on_the_data_path():
    form, years, note = terminal_form_from_data(_inputs("fragmentation"), "fragmentation", 10)
    assert form == "gordon" and years is None and "no decay_horizon" in note
    form, years, note = terminal_form_from_data(_inputs("muddle_through"), "muddle_through", 10)
    assert form == "excess_return_convergence" and years == 12.5 and note is None
    with pytest.raises(NotImplementedError):
        terminal_form_from_data(_inputs("fragmentation"), "fragmentation", 9)


def test_convergence_inputs_are_validated():
    import dataclasses
    inp = build_engine_inputs_from_data(_inputs("muddle_through"), "muddle_through")
    with pytest.raises(ValueError):
        dataclasses.replace(inp, terminal_form="excess_return_convergence", convergence_years=None)
    with pytest.raises(ValueError):
        dataclasses.replace(inp, terminal_form="gordon")   # convergence_years still set
    with pytest.raises(ValueError):
        dataclasses.replace(inp, terminal_form="three_phase")
