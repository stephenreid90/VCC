"""Open item 8, step 1: the §15.5 CET1 diagnostic is warn-only and cannot move a level.

The item's finding was that the bank engine holds the payout flat in every world
while book equity compounds well below AIEA, so the implied capital ratio falls in
every year and nothing notices. These tests assert three things in order of
importance: that adding the check moves no number, that the projection is
arithmetically what it claims to be, and that it actually fires on WBC.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from vcc_valuations.dcf.bank_capital import project_cet1
from vcc_valuations.dcf.bank_engine import BankEngine
from vcc_valuations.translator import build_bank_inputs_from_data, load_inputs

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = sorted(p.stem for p in (ROOT / "data" / "scenarios").glob("*.yaml"))


def _wbc(scenario_id: str):
    return build_bank_inputs_from_data(
        load_inputs(ROOT, scenario_id, "australian_major_banks", "wbc"), scenario_id
    )


# --------------------------------------------------------------- the invariant
# This is the test that matters. Book equity in the §15 build is a pure
# accumulator -- net interest income comes from AIEA, never from equity -- so a
# per-period roll-forward must sum to exactly the closing figure the engine
# already computed for the terminal value. If that ever stops holding, the
# diagnostic has become load-bearing and is no longer warn-only.
@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_the_equity_path_sums_to_the_closing_equity_the_terminal_uses(scenario_id):
    r = BankEngine().run(_wbc(scenario_id))
    assert r.book_equity_path, "no equity path produced"
    assert r.book_equity_path[-1] == pytest.approx(r.closing_book_equity, rel=0, abs=1e-9)
    assert sum(r.retained_by_period) == pytest.approx(r.retained_earnings, rel=0, abs=1e-9)


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_the_diagnostic_does_not_change_value_per_share(scenario_id):
    """Same inputs with the capital block stripped must give the same share price."""
    inp = _wbc(scenario_id)
    without = replace(
        inp, cet1_anchor_ratio=None, rwa_anchor=None, rwa_density=None,
        cet1_floor=None, cet1_operating_target=None,
    )
    with_diag = BankEngine().run(inp)
    no_diag = BankEngine().run(without)

    assert with_diag.value_per_share == pytest.approx(no_diag.value_per_share, rel=0, abs=1e-12)
    assert no_diag.cet1_trajectory is None, "diagnostic ran without its inputs"
    assert with_diag.cet1_trajectory is not None, "diagnostic did not run with its inputs"


def test_a_bank_with_no_capital_data_simply_gets_no_warning():
    """Absent data must not be a reason a valuation fails to build."""
    inp = replace(_wbc("muddle_through"), cet1_anchor_ratio=None)
    r = BankEngine().run(inp)
    assert r.cet1_trajectory is None
    assert r.value_per_share > 0


# ------------------------------------------------------------ the arithmetic
def _flat(n: int, **over):
    """A bank whose equity and RWA grow at the same rate: the ratio must not move."""
    base = dict(
        labels=[f"Y{i}" for i in range(1, n + 1)],
        opening_book_equity=1000.0,
        retained_by_period=[],
        rwa_by_period=[],
        rwa_anchor=10000.0,
        anchor_ratio=0.12,
        floor=0.1025,
        operating_target=0.115,
    )
    base.update(over)
    return base


def test_equal_growth_rates_hold_the_ratio_flat():
    g = 0.05
    equity, rwa = 1000.0, 10000.0
    retained, rwas = [], []
    for _ in range(5):
        retained.append(equity * g)
        equity += equity * g
        rwa *= 1.0 + g
        rwas.append(rwa)

    t = project_cet1(**_flat(5, retained_by_period=retained, rwa_by_period=rwas))
    for pt in t.points:
        assert pt.cet1_ratio == pytest.approx(0.12, abs=1e-12)
    assert t.drift == pytest.approx(0.0, abs=1e-12)
    assert t.is_capital_consistent
    assert t.warnings == []


def test_a_constant_rwa_density_cancels_out_entirely():
    """Density only matters when it moves — so the level of it must not shift the path."""
    retained = [20.0] * 5
    aiea = [10000.0 * (1.04 ** k) for k in range(1, 6)]

    def run(density):
        return project_cet1(**_flat(
            5,
            retained_by_period=retained,
            rwa_by_period=[a * density for a in aiea],
            rwa_anchor=10000.0 * density,
        ))

    a, b = run(0.45), run(0.90)
    assert [p.cet1_ratio for p in a.points] == pytest.approx([p.cet1_ratio for p in b.points])


def test_equity_growing_slower_than_rwa_erodes_the_ratio_and_warns():
    retained = [10.0] * 5                                  # ~1% on 1000
    rwas = [10000.0 * (1.05 ** k) for k in range(1, 6)]    # 5%
    t = project_cet1(**_flat(5, retained_by_period=retained, rwa_by_period=rwas))

    assert t.closing_ratio < t.anchor_ratio
    assert t.drift < 0
    assert not t.is_capital_consistent
    assert any("erodes" in w for w in t.warnings)


def test_the_floor_warning_fires_and_reads_worse_than_the_target_one():
    retained = [0.0] * 5
    rwas = [10000.0 * (1.10 ** k) for k in range(1, 6)]
    t = project_cet1(**_flat(5, retained_by_period=retained, rwa_by_period=rwas,
                             anchor_ratio=0.106))

    assert t.first_below_target is not None
    assert t.first_below_floor is not None
    assert any("APRA floor" in w for w in t.warnings)
    # Worst last, so a reader who stops at the first line still sees the mildest.
    assert t.warnings[-1].count("APRA floor") == 1


def test_the_anchor_rwa_is_measured_from_the_reported_balance_sheet():
    """Dropping the anchor would lose or double-count one period of asset growth.

    With one period and RWA growing 10% off the reported base, the ratio must move
    by that 10% and not by nothing.
    """
    t = project_cet1(**_flat(1, retained_by_period=[0.0], rwa_by_period=[11000.0]))
    assert t.points[0].rwa_growth == pytest.approx(0.10)
    assert t.closing_ratio == pytest.approx(0.12 / 1.10)


def test_mismatched_series_lengths_are_rejected():
    with pytest.raises(ValueError, match="same length"):
        project_cet1(**_flat(3, retained_by_period=[1.0, 2.0], rwa_by_period=[1.0, 2.0, 3.0]))


# ------------------------------------------------- the finding, pinned on WBC
def test_wbc_erodes_capital_in_every_scenario_which_is_the_item_8_finding():
    """Every world erodes, because the payout never responds to asset growth."""
    drifts = {}
    for s in SCENARIOS:
        t = BankEngine().run(_wbc(s)).cet1_trajectory
        assert t is not None
        drifts[s] = t.drift

    assert all(d < 0 for d in drifts.values()), drifts
    assert all(t < 0 for t in drifts.values())
    # None of them breaches the regulatory floor inside the explicit period; the
    # problem is the drift and the operating target, not an APRA event.
    for s in SCENARIOS:
        assert BankEngine().run(_wbc(s)).cet1_trajectory.first_below_floor is None


def test_the_cited_drift_figures_come_from_here():
    """Standing rule 4: the figures quoted in the handover are produced by this test.

    Pinned loosely on purpose — to the nearest 5bp — because the point being
    recorded is the magnitude of the erosion, not a sixth decimal place, and a
    tight pin on a quantity that moves whenever WBC's balance sheet is refreshed
    would be a tripwire rather than evidence.
    """
    def drift_bps(s):
        return BankEngine().run(_wbc(s)).cet1_trajectory.drift_bps

    assert drift_bps("muddle_through") == pytest.approx(-97, abs=5)
    assert drift_bps("orderly_convergence") == pytest.approx(-165, abs=5)
    assert drift_bps("stagflation_persists") == pytest.approx(-71, abs=5)

    central = BankEngine().run(_wbc("muddle_through")).cet1_trajectory
    assert central.anchor_ratio == pytest.approx(0.1242, abs=1e-6)
    assert central.closing_ratio == pytest.approx(0.1145, abs=5e-4)
    assert central.first_below_target == "Y5"


def test_the_capital_ordering_is_inverted_against_value():
    """The best scenario for value is the worst for capital, and that is real.

    Orderly Convergence produces the highest share price and erodes the most
    capital, because the same strong asset growth that drives the value consumes
    the capital; Stagflation erodes least because the balance sheet barely grows.
    Asserted so that a change in this relationship is a conscious event, in the
    spirit of D-56: ordering is read, not assumed.
    """
    rows = {}
    for s in SCENARIOS:
        r = BankEngine().run(_wbc(s))
        rows[s] = (r.value_per_share, r.cet1_trajectory.drift)

    best_value = max(rows, key=lambda s: rows[s][0])
    worst_capital = min(rows, key=lambda s: rows[s][1])
    assert best_value == worst_capital == "orderly_convergence", rows

    worst_value = min(rows, key=lambda s: rows[s][0])
    best_capital = max(rows, key=lambda s: rows[s][1])
    assert worst_value == best_capital == "stagflation_persists", rows


# ------------------------------------- D-60: the rule, built but switched off
# Ruled 16 September 2026 (answers 6b and 7): let the ratio drift, and once it
# reaches the OPERATING TARGET cut the payout by just enough to hold it there.
# Implemented and tested here, and deliberately not switched on -- see
# test_the_constraint_raises_value_which_is_why_it_is_off for the reason.
def _on(scenario_id: str):
    return replace(_wbc(scenario_id), constrain_payout_to_capital=True)


def test_the_constraint_is_off_by_default_so_no_level_moved():
    inp = _wbc("muddle_through")
    assert inp.constrain_payout_to_capital is False
    r = BankEngine().run(inp)
    assert r.value_per_share == pytest.approx(30.0304, abs=1e-3)
    assert r.capital_constraint_binds_from is None
    assert r.dividends_forgone == 0.0


def test_when_on_it_holds_the_ratio_exactly_on_the_operating_target():
    """The rule as ruled: the target is a floor for the ratio, not a target to sit on."""
    r = BankEngine().run(_on("muddle_through"))
    t = r.cet1_trajectory
    assert r.capital_constraint_binds_from == "Y5"
    # Before it binds the ratio drifts freely; from the binding period it sits on
    # the target to within rounding.
    assert t.points[-1].cet1_ratio == pytest.approx(t.operating_target, abs=1e-9)
    assert all(p.cet1_ratio > t.operating_target for p in t.points[:-1])


def test_the_rule_is_one_sided_and_never_raises_the_payout():
    """A bank above its target does not mechanically distribute the surplus."""
    for s in SCENARIOS:
        r = BankEngine().run(_on(s))
        stated = _wbc(s).dividend_payout_ratio
        assert all(p <= stated + 1e-12 for p in r.payout_applied), (s, r.payout_applied)


def test_a_scenario_that_never_reaches_the_target_is_untouched():
    """Stagflation and Fragmentation erode least, so the rule must not bite."""
    for s in ("stagflation_persists", "fragmentation"):
        off = BankEngine().run(_wbc(s))
        on = BankEngine().run(_on(s))
        assert on.capital_constraint_binds_from is None, s
        assert on.value_per_share == pytest.approx(off.value_per_share, abs=1e-12), s


def test_the_constraint_raises_value_which_is_why_it_is_off():
    """The finding that stopped D-60 being switched on.

    Retention is capitalised in the terminal at (ROE - g)/(Ke - g). WBC's
    terminal ROE exceeds its cost of equity, so that multiple is above one and a
    withheld dividend is worth more retained than paid. The capital constraint
    therefore INCREASES the valuation, most where it withholds most. Under D-45
    that is not admissible: retention is the derived third of terminal growth,
    terminal return and reinvestment, and here it changes while both of the
    others stay fixed, so retained capital earns the terminal ROE forever with
    nothing given up.

    Asserted rather than described so that the day someone links retention to
    terminal ROE or g, this test fails and says why.
    """
    for s in SCENARIOS:
        inp = _wbc(s)
        multiple = (inp.terminal_roe - inp.terminal_growth) / (inp.cost_of_equity - inp.terminal_growth)
        off = BankEngine().run(inp)
        on = BankEngine().run(_on(s))

        assert multiple > 1.0, (s, multiple)
        if on.dividends_forgone > 0:
            assert on.value_per_share > off.value_per_share, (s, off.value_per_share, on.value_per_share)
            assert on.terminal_share_of_claim > off.terminal_share_of_claim, s


def test_the_uplift_is_the_retention_multiple_and_nothing_else():
    """Decomposed, so the mechanism is pinned rather than just the direction."""
    inp = _wbc("orderly_convergence")
    off = BankEngine().run(inp)
    on = BankEngine().run(_on("orderly_convergence"))

    # Every dollar withheld lands in closing equity.
    assert on.closing_book_equity - off.closing_book_equity == pytest.approx(
        on.dividends_forgone, rel=1e-9)
    # The terminal gains that equity times the justified multiple, discounted.
    multiple = (inp.terminal_roe - inp.terminal_growth) / (inp.cost_of_equity - inp.terminal_growth)
    expected = on.dividends_forgone * multiple * on.terminal_discount_factor
    assert on.pv_terminal_value - off.pv_terminal_value == pytest.approx(expected, rel=1e-9)
    # And loses the PV of the dividends it did not pay, which is smaller.
    assert off.pv_explicit_dividends - on.pv_explicit_dividends < expected
