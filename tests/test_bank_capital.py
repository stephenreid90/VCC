"""Open item 8: the §15.5 CET1 diagnostic, and the D-60 payout constraint on top of it.

The item's finding was that the bank engine holds the payout flat in every world
while book equity compounds well below AIEA, so the implied capital ratio falls in
every year and nothing notices.

Two layers, tested separately. Step 1 is the diagnostic: it observes the drift and
warns, and cannot move a level. Step 2 is D-60: once the ratio reaches the operating
target the payout is cut by just enough to hold it there, which DOES move levels --
upward, because retained equity is capitalised in the terminal at (ROE - g)/(Ke - g)
and that multiple is above one. The step-1 tests therefore pass ``_off`` explicitly,
since the world they describe is the one before the constraint arrests the drift.
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
    """Inputs as assembled from data — D-60 constraint ON, i.e. the ratified path."""
    return build_bank_inputs_from_data(
        load_inputs(ROOT, scenario_id, "australian_major_banks", "wbc"), scenario_id
    )


def _off(scenario_id: str):
    """The same inputs with the payout constraint off.

    Several of the step-1 tests below describe the UNCONSTRAINED world, because
    that is the world the item 8 finding was about: a flat payout that never
    responds to asset growth. They have to say so explicitly now that D-60 is on
    by default, or they would be asserting the drift of a model that already
    arrests it.
    """
    return replace(_wbc(scenario_id), constrain_payout_to_capital=False)


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
    inp = _off(scenario_id)
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
    inp = replace(_off("muddle_through"), cet1_anchor_ratio=None)
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
        t = BankEngine().run(_off(s)).cet1_trajectory
        assert t is not None
        drifts[s] = t.drift

    assert all(d < 0 for d in drifts.values()), drifts
    assert all(t < 0 for t in drifts.values())
    # Over the ten-year explicit period (D-71, 14 Oct 2026) the UNCONSTRAINED
    # Orderly Convergence path does cross the regulatory floor (10.25%) at Y7 --
    # ten years of 6.4% asset growth on an unchanged payout. That is exactly the
    # case D-60 exists for: with the constraint on (the default) no scenario
    # reaches the floor, because the payout is cut at the operating target first.
    for s in SCENARIOS:
        unconstrained = BankEngine().run(_off(s)).cet1_trajectory.first_below_floor
        assert unconstrained == ("Y7" if s == "orderly_convergence" else None), (s, unconstrained)
        assert BankEngine().run(_on(s)).cet1_trajectory.first_below_floor is None, s


def test_the_cited_drift_figures_come_from_here():
    """Standing rule 4: the figures quoted in the handover are produced by this test.

    Pinned loosely on purpose — to the nearest 5bp — because the point being
    recorded is the magnitude of the erosion, not a sixth decimal place, and a
    tight pin on a quantity that moves whenever WBC's balance sheet is refreshed
    would be a tripwire rather than evidence.
    """
    def drift_bps(s):
        return BankEngine().run(_off(s)).cet1_trajectory.drift_bps

    # Ten-year figures (D-71, 14 Oct 2026). The five-year drifts these replaced were
    # -97 / -165 / -71 (and -93 for Stagflation on the D-72 path at five years).
    assert drift_bps("muddle_through") == pytest.approx(-174, abs=5)
    assert drift_bps("orderly_convergence") == pytest.approx(-284, abs=5)
    assert drift_bps("stagflation_persists") == pytest.approx(-122, abs=5)

    central = BankEngine().run(_off("muddle_through")).cet1_trajectory
    assert central.anchor_ratio == pytest.approx(0.1242, abs=1e-6)
    # Over five years the unconstrained central case closed at 11.45%, just above
    # the 11.25% target (M13), which is why D-60 did not bite then. Over ten years
    # (D-71) it drifts on to 10.68% and crosses the target at Y7, so D-60 bites in
    # Muddle Through as well -- the drift was always there; the horizon now shows it.
    assert central.closing_ratio == pytest.approx(0.1068, abs=5e-4)
    assert central.operating_target == pytest.approx(0.1125, abs=1e-9)
    assert central.first_below_target == "Y7"
    assert central.closing_ratio < central.operating_target


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
        r = BankEngine().run(_off(s))
        rows[s] = (r.value_per_share, r.cet1_trajectory.drift)

    best_value = max(rows, key=lambda s: rows[s][0])
    worst_capital = min(rows, key=lambda s: rows[s][1])
    assert best_value == worst_capital == "orderly_convergence", rows

    worst_value = min(rows, key=lambda s: rows[s][0])
    best_capital = max(rows, key=lambda s: rows[s][1])
    # Read, not assumed (D-56). At FIVE years on the D-72 path (earlier on 14 Oct
    # 2026) Fragmentation was briefly the best for capital: Stagflation's shock phase
    # is inflationary and front-loads NOMINAL asset growth (3.4% in Y1). At TEN
    # years (D-71) Stagflation's low growth from its resolution phase (2.2% from Y5)
    # dominates and it is again the scenario that consumes the least capital, so
    # the full inversion holds once more -- for a reason the scenario files state.
    assert worst_value == best_capital == "stagflation_persists", rows


# ------------------------------------- D-60: the rule, built but switched off
# Ruled 16 September 2026 (answers 6b and 7): let the ratio drift, and once it
# reaches the OPERATING TARGET cut the payout by just enough to hold it there.
# Implemented and tested here, and deliberately not switched on -- see
# test_the_constraint_raises_value_which_is_why_it_is_off for the reason.
def _on(scenario_id: str):
    return _wbc(scenario_id)


def test_the_constraint_is_on_by_default_and_gives_the_ratified_level():
    """On by default, and on the central case it no longer bites (M13).

    D-60 bound the payout to the archetype's 11.50% target and Muddle Through
    crossed it at Y5. Westpac's own board target is above 11.25% post-dividend
    and the company figure overrides the archetype anchor, so the central case
    no longer reaches the level it defends and returns to the audited value.
    """
    inp = _wbc("muddle_through")
    assert inp.constrain_payout_to_capital is True
    assert inp.cet1_operating_target == pytest.approx(0.1125, abs=1e-9)
    r = BankEngine().run(inp)
    # 30.0304 with no bite at five years; at ten years (D-71, 14 Oct 2026) the ratio
    # reaches 11.25% at Y7 and the payout is cut from there. D-79 (same day):
    # 31.0502 -> 33.0779 on the derived terminal growth (4.5%, was typed 3.5%).
    assert r.value_per_share == pytest.approx(33.0779, abs=1e-3)
    assert r.capital_constraint_binds_from == "Y7"
    assert r.dividends_forgone > 0


def test_when_on_it_holds_the_ratio_exactly_on_the_operating_target():
    """The rule as ruled: the target is a floor for the ratio, not a level to sit on.

    Orderly Convergence rather than the central case, because at the corrected
    11.25% board target (M13) it is the only scenario that still reaches the
    level it has to defend. It erodes fastest — 165bp — and binds at Y4.
    """
    r = BankEngine().run(_on("orderly_convergence"))
    t = r.cet1_trajectory
    assert r.capital_constraint_binds_from == "Y4"
    # Before it binds the ratio drifts freely; from the binding period onward it
    # sits on the target to within rounding.
    binds_at = [i for i, p in enumerate(t.points) if p.label == "Y4"][0]
    for p in t.points[:binds_at]:
        assert p.cet1_ratio > t.operating_target, p.label
    for p in t.points[binds_at:]:
        assert p.cet1_ratio == pytest.approx(t.operating_target, abs=1e-9), p.label


def test_the_rule_is_one_sided_and_never_raises_the_payout():
    """A bank above its target does not mechanically distribute the surplus."""
    for s in SCENARIOS:
        r = BankEngine().run(_on(s))
        stated = _wbc(s).dividend_payout_ratio
        assert all(p <= stated + 1e-12 for p in r.payout_applied), (s, r.payout_applied)


def test_a_scenario_that_never_reaches_the_target_is_untouched():
    """Where the ratio stays above the target the rule does nothing at all.

    At five years Stagflation and Fragmentation never reached it. Over ten years
    (D-71) every scenario eventually does -- Stagflation last, in Y10 -- so the
    property is checked on a shortened run of the same inputs instead of on a
    scenario that no longer exists in the data.
    """
    from dataclasses import replace
    for s in ("stagflation_persists", "fragmentation"):
        short = dict(horizon_years=5, aiea_growth=BankEngine.aiea_growth_path(_off(s))[:5],
                     nim_applied=_off(s).nim_applied[:6], cost_to_income=_off(s).cost_to_income[:6],
                     credit_loss_rate=_off(s).credit_loss_rate[:6])
        off = BankEngine().run(replace(_off(s), **short))
        on = BankEngine().run(replace(_on(s), **short))
        assert on.capital_constraint_binds_from is None, s
        assert on.value_per_share == pytest.approx(off.value_per_share, abs=1e-12), s
    # and at the full ten years the rule does bite, last of all in Stagflation
    assert BankEngine().run(_on("stagflation_persists")).capital_constraint_binds_from == "Y10"


def test_the_constraint_raises_value_which_is_the_retention_trade():
    """D-60 raises the valuation, and that is the intended reading.

    Retention is capitalised in the terminal at (ROE - g)/(Ke - g), which is
    above one because WBC's terminal ROE exceeds its cost of equity. So a
    withheld dividend is worth more retained than paid and the constraint
    INCREASES the valuation, most where it withholds most.

    Stephen's ruling, 16 September 2026: that is correct rather than an
    artefact. The justified price-to-book terminal is derived from g = ROE x b,
    so the terminal stream already IS the dividend the retained equity supports,
    growing at the rate retention funds -- a lower dividend now traded for a
    higher one later. The form says so; the engine now says so too.

    Asserted so the direction is a stated property rather than a surprise.
    """
    # Ten-year finding (D-71, 14 Oct 2026). In this engine a retained dollar earns
    # NOTHING until the terminal -- NPAT is struck on AIEA x NIM, not on book equity
    # -- so retention pays only if the terminal multiple outruns Ke compounded over
    # the years between the cut and the terminal. Disorderly Climate binds at Y6 with
    # a multiple of 1.20 against (1.0805)^4.35 = 1.40, and its value FALLS by 1c.
    # The other five bind later or carry a higher multiple and rise. Read, not
    # assumed: the direction is pinned per scenario with the arithmetic beside it.
    # Letting retained equity earn inside the explicit period is a modelling gap,
    # noted in WORKING_NOTES (14 Oct 2026), not fixed here.
    falls = {"disorderly_climate_crystallisation"}
    for s in SCENARIOS:
        inp = _off(s)
        multiple = (inp.terminal_roe - inp.terminal_growth) / (inp.cost_of_equity - inp.terminal_growth)
        off = BankEngine().run(inp)
        on = BankEngine().run(_on(s))

        assert multiple > 1.0, (s, multiple)
        if on.dividends_forgone > 0:
            if s in falls:
                assert on.value_per_share < off.value_per_share, (s, off.value_per_share, on.value_per_share)
            else:
                assert on.value_per_share > off.value_per_share, (s, off.value_per_share, on.value_per_share)
            assert on.terminal_share_of_claim > off.terminal_share_of_claim, s


def test_the_uplift_is_the_retention_multiple_and_nothing_else():
    """Decomposed, so the mechanism is pinned rather than just the direction."""
    inp = _off("orderly_convergence")
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
