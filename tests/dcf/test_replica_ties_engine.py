"""The replica reproduces ``FcfEngine`` exactly, or it is not evidence.

``tests/dcf/harness/replica.py`` exists to size structural changes the engine
cannot express yet. Anything it reports is worth exactly as much as its tie to
the production engine, so that tie is a test rather than a note: same inputs,
same answer, to floating-point equality, on every live scenario.

The tie is what makes a variant interpretable. When a plan that differs from the
tying plan in one declared way produces a different number, the difference is
attributable to that change -- not to a second implementation of the same
arithmetic drifting from the first.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vcc_valuations.dcf.fcf_engine import FcfEngine
from vcc_valuations.translator import build_engine_inputs_from_data, load_inputs
from tests.dcf.harness import replica

ROOT = Path(__file__).resolve().parents[2]

SCENARIOS = [
    "muddle_through",
    "orderly_convergence",
    "ai_productivity_lag",
    "fragmentation",
    "disorderly_climate_crystallisation",
    "stagflation_persists",
]


def _engine_inputs(scenario_id: str):
    return build_engine_inputs_from_data(
        load_inputs(
            ROOT,
            scenario_id=scenario_id,
            archetype_id="industrial_explosives",
            company_id="dnl",
        ),
        scenario_id,
    )


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_replica_reproduces_engine(scenario_id: str) -> None:
    inp = _engine_inputs(scenario_id)
    engine = FcfEngine().run(inp)
    got = replica.run(replica.plan_from_engine_inputs(inp))

    assert got.value_per_share == pytest.approx(engine.value_per_share, rel=1e-15, abs=0.0)
    assert got.enterprise_value == pytest.approx(engine.enterprise_value, rel=1e-15, abs=0.0)
    assert got.pv_explicit == pytest.approx(engine.pv_explicit, rel=1e-15, abs=0.0)
    assert got.pv_terminal == pytest.approx(engine.pv_terminal, rel=1e-15, abs=0.0)
    assert got.terminal_fcff == pytest.approx(engine.terminal_fcff, rel=1e-15, abs=0.0)

    for i, label in enumerate(engine.period_labels):
        assert got.revenue[i] == pytest.approx(engine.revenue[i], rel=1e-15, abs=0.0), label
        assert got.fcff[i] == pytest.approx(engine.fcff[i], rel=1e-15, abs=0.0), label
        assert got.delta_wc[i] == pytest.approx(engine.delta_wc[i], rel=1e-15, abs=0.0), label
        assert got.capex[i] == pytest.approx(engine.capex[i], rel=1e-15, abs=0.0), label


def _steady_state_plan(scenario_id: str):
    """A plan whose final explicit year is a genuine steady state.

    Growth faded onto g, capex flat at its converged rate from year one, and the
    terminal inheriting that rate -- the state D-35, D-36 and D-39 together are
    meant to produce.
    """
    base = replica.plan_from_engine_inputs(_engine_inputs(scenario_id))
    return replica.terminal_capex_from_final_year(
        replica.converge_capex(
            replica.fade_growth(base, fade_period_length=base.horizon_years),
            steady_state_pct=base.capex_pct[-1],
            converge_by_year=1,
        )
    )


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_terminal_working_capital_leads_the_explicit_convention_by_one_year(
    scenario_id: str,
) -> None:
    """The terminal's working-capital drag is struck one year ahead of the explicit one.

    An explicit year charges the intensity against the increase in the run-rate
    it has just achieved. The terminal charges ``g x intensity`` against
    terminal revenue -- which is the increase from the terminal year, not into
    it, so it is larger by a factor of ``1 + g``.

    Both are defensible readings of the same convention and the gap is small,
    but it is a real discontinuity at the boundary and it is the reason a
    steady-state explicit year does not reproduce the terminal exactly. Pinned
    here so that it stays a known convention rather than becoming a surprise the
    next time the boundary is examined.
    """
    steady = _steady_state_plan(scenario_id)
    res = replica.run(steady)
    longer = replica.run(replica.extend(steady, steady.horizon_years + 1))

    g, wc = steady.terminal_growth, steady.working_capital_intensity
    rev_T = res.revenue[-1] * (1.0 + g)
    convention_gap = rev_T * g * wc - wc * (rev_T - res.revenue[-1])

    assert longer.fcff[-1] == pytest.approx(res.terminal_fcff + convention_gap,
                                            rel=1e-12, abs=0.0)


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_a_surplus_steady_year_costs_only_the_discounting_convention(
    scenario_id: str,
) -> None:
    """D-35's "surplus years cost nothing" is true up to mid-period discounting.

    Explicit flows are discounted from the middle of their year; the terminal is
    a Gordon value struck at the end of the final explicit year. So converting a
    terminal year into an explicit one moves it half a year closer, and the
    valuation rises by a factor that depends only on WACC and g -- not on the
    company, the scenario or the horizon.

    The claim tested is therefore the sharper one: extending a steady-state plan
    changes enterprise value by exactly that analytic factor and by nothing
    else.
    """
    steady = _steady_state_plan(scenario_id)
    res = replica.run(steady)
    longer = replica.run(replica.extend(steady, steady.horizon_years + 1))

    w, g = steady.wacc, steady.terminal_growth
    wc = steady.working_capital_intensity
    rev_T = res.revenue[-1] * (1.0 + g)
    convention_gap = rev_T * g * wc - wc * (rev_T - res.revenue[-1])

    # What the extra year is worth, built from the terminal it replaces.
    pv_added = (res.terminal_fcff + convention_gap) / (1.0 + w) ** (steady.stub_years + steady.horizon_years + 0.5)
    pv_new_terminal = (
        res.terminal_fcff * (1.0 + g) / (w - g)
        / (1.0 + w) ** (steady.stub_years + steady.horizon_years + 1)
    )

    assert longer.enterprise_value == pytest.approx(
        res.pv_explicit + pv_added + pv_new_terminal, rel=1e-12, abs=0.0
    )
    # And the direction and rough size of it: half a year of discounting, gained.
    assert 1.0 < longer.enterprise_value / res.enterprise_value < 1.01
