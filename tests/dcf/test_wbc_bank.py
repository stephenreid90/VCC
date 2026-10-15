"""WBC-3: the bank valuation engine reproduces the §15 workbook from data.

The Muddle Through per-share value ties the audited workbook
(analyses/wbc/valuations/wbc_muddle_through_valuation_v4_formulas.xlsx) to the
cent, built end-to-end from data with no hand-typed constant in the engine.
The six scenarios value from the same engine path and are downside-skewed.
"""

from dataclasses import replace
from pathlib import Path

import pytest

from vcc_valuations.dcf.bank_engine import BankEngine
from vcc_valuations.translator import build_bank_inputs_from_data, load_inputs

ROOT = Path(__file__).resolve().parents[2]

SCENARIOS = [
    "orderly_convergence", "muddle_through", "ai_productivity_lag",
    "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists",
]


def _run(scenario):
    inp = load_inputs(ROOT, scenario, "australian_major_banks", "wbc")
    return BankEngine().run(build_bank_inputs_from_data(inp, scenario))


# The terminal growth the hand-built v4 workbook types per scenario. D-79 (14 Oct
# 2026) derives WBC's terminal growth from the chain, so the live engine no longer
# carries these; the workbook tie keeps them because they are the WORKBOOK's inputs
# -- the tie audits the §15 mechanics, not the growth judgement.
V4_WORKBOOK_G = {"muddle_through": 0.035, "orderly_convergence": 0.0375}
# The AIEA growth the v4 Muddle Through workbook types: a flat 4.5% industry rate less
# WBC's 0.15pp share-loss offset. Until D-80 (14 Oct 2026) the live D-72 path was flat
# at the same number because Muddle Through's world series were flat; D-80 lowered the
# year-10 CPI, the path now slopes, and the tie runs at the WORKBOOK's input for the
# same reason it runs at the workbook's g. Orderly Convergence has no such entry: its
# five-year figure below was re-pinned onto the D-72 path on 14 Oct and is a golden,
# not a workbook tie.
V4_WORKBOOK_AIEA_G = {"muddle_through": 0.045 - 0.0015}


def _at_five_years(inp):
    """The audited v4 workbook is a FIVE-year model. D-71 moved WBC to ten years on
    14 Oct 2026; the workbook stays the independent audit of the §15 mechanics by
    running the same engine at the workbook's own horizon (glides sliced to Y5, the
    growth path to Y1..Y5) and at the workbook's own typed terminal growth (D-79
    derives the live one). Nothing else about the engine differs between the runs."""
    path = list(BankEngine.aiea_growth_path(inp))[:5]
    if inp.scenario_id in V4_WORKBOOK_AIEA_G:
        path = [V4_WORKBOOK_AIEA_G[inp.scenario_id]] * 5
    return replace(
        inp, horizon_years=5, retained_earns_ke=False,  # 16 Oct 2026: the v4 workbook has no retained income
        aiea_growth=path,
        nim_applied=inp.nim_applied[:6], cost_to_income=inp.cost_to_income[:6],
        credit_loss_rate=inp.credit_loss_rate[:6],
        terminal_form="gordon", convergence_years=None,
        terminal_growth=V4_WORKBOOK_G[inp.scenario_id],
    )


def test_muddle_through_ties_workbook():
    """The independent tie, struck on the UNCONSTRAINED path (D-60, 16 Sep 2026).

    The audited v4 workbook has no capital constraint in it, so once D-60 was
    switched on the engine stopped reproducing it -- and the right response was
    not to re-pin this test onto the engine's new answer, which would have
    dissolved the only independent check on the §15 mechanics into a
    self-comparison. The workbook audits the DDM and the ROE-fade terminal; the
    payout constraint is an overlay on top of that with its own tests. So this
    ties the base engine, and the constrained level is asserted separately below.
    """
    r = BankEngine().run(replace(
        _at_five_years(build_bank_inputs_from_data(load_inputs(ROOT, "muddle_through",
                                                               "australian_major_banks", "wbc"),
                                                   "muddle_through")),
        constrain_payout_to_capital=False,
    ))
    # headline value per share (workbook DDM + ROE-fade terminal), at the workbook's five years
    assert r.value_per_share == pytest.approx(30.0304, abs=1e-3)
    # key bridge lines tie the audited workbook
    assert r.closing_book_equity == pytest.approx(83682.114, abs=0.1)
    assert r.terminal_value == pytest.approx(128741.71, abs=1.0)
    assert r.pv_terminal_value == pytest.approx(85079.86, abs=1.0)
    assert r.ordinary_equity_value == pytest.approx(102550.79, abs=1.0)
    # cost of equity is Rf + beta*ERP = 4.30% + 0.75*5.00%
    assert r.cost_of_equity == pytest.approx(0.0805, abs=1e-6)


def test_muddle_through_no_longer_binds_so_it_ties_the_workbook_on_both_paths():
    """M13, 17 Sep 2026: correcting the target to 11.25% stopped the bite.

    D-60 bound the payout to the archetype's 11.50% and Muddle Through's CET1
    crossed it at Y5. Westpac's own board target is above 11.25% post-dividend,
    and the company target overrides the archetype anchor, so the ratio no longer
    reaches the level it has to defend. The constrained and unconstrained paths
    therefore agree here, and both tie the audited v4 workbook -- which is a
    stronger position than the overlay it replaced.
    """
    r = BankEngine().run(_at_five_years(build_bank_inputs_from_data(
        load_inputs(ROOT, "muddle_through", "australian_major_banks", "wbc"), "muddle_through")))
    assert r.value_per_share == pytest.approx(30.0304, abs=1e-3)
    assert r.capital_constraint_binds_from is None
    assert r.dividends_forgone == 0.0
    assert r.closing_book_equity == pytest.approx(83682.114, abs=0.1)


def test_at_ten_years_the_constraint_binds_in_muddle_through_too():
    """D-71 (14 Oct 2026): five more years of CET1 drift reach the 11.25% target in
    every scenario -- Muddle Through at Y7. The v4 tie above is unchanged because it
    runs at the workbook's own five years; this is the live ten-year level.
    D-79 (14 Oct 2026): 31.0502 -> 33.0779 as terminal growth moves from the typed
    3.5% to the derived 4.5% (the system path at Y10, capped at nominal GDP).
    D-80 (14 Oct 2026): 33.0779 -> 32.2655 as year-10 CPI falls to 2.5% (derived g 4.14%).
    D-81 (15 Oct 2026): 32.2655 -> 32.3984 as the share-loss offset glides to zero by Y5."""
    r = _run("muddle_through")
    assert len(r.period_labels) == 11   # stub + Y1..Y10
    # 16 Oct 2026 (option 1b, retained equity earns Ke): 32.3984 -> 33.9332.
    assert r.value_per_share == pytest.approx(33.9332, abs=1e-3)
    assert r.capital_constraint_binds_from == "Y6"   # Y7 before D-80; knife-edge, see test_bank_capital
    assert r.dividends_forgone > 0


def test_orderly_convergence_is_the_one_scenario_the_constraint_still_bites():
    """It erodes fastest — 165bp — so it is the one that still reaches 11.25% inside FIVE years.

    Keeps a live assertion on the D-60 machinery. If this stops binding too, the
    payout constraint has become dead code and the register should say so. At the
    ten-year horizon (D-71, 14 Oct 2026) every scenario eventually binds; this test
    keeps the five-year reading because that is the claim the docstring makes.
    """
    r = BankEngine().run(_at_five_years(build_bank_inputs_from_data(
        load_inputs(ROOT, "orderly_convergence", "australian_major_banks", "wbc"), "orderly_convergence")))
    # 36.1619 before the D-72 bank path; 36.2265 before D-80's lower year-10 CPI (both 14 Oct 2026);
    # 36.2925 before D-81's offset glide (15 Oct 2026)
    assert r.value_per_share == pytest.approx(36.3596, abs=1e-3)
    assert r.capital_constraint_binds_from == "Y4"
    assert r.dividends_forgone > 0
    assert r.cet1_trajectory.operating_target == pytest.approx(0.1125, abs=1e-9)


def test_all_six_scenarios_value_and_are_ordered():
    vals = {s: _run(s).value_per_share for s in SCENARIOS}
    # every world produces a finite positive per-share value
    assert all(v > 0 for v in vals.values())
    # downside skew: Orderly Convergence highest, Stagflation lowest, MT in between
    assert vals["orderly_convergence"] > vals["muddle_through"] > vals["stagflation_persists"]
    assert vals["muddle_through"] > vals["fragmentation"] > vals["disorderly_climate_crystallisation"]


def test_single_ke_held_across_scenarios():
    # single-Ke discipline (§15.2(d)): the discount rate does not move by scenario
    kes = {_run(s).cost_of_equity for s in SCENARIOS}
    assert len(kes) == 1


def test_derivation_headline_is_value_per_share():
    inp = load_inputs(ROOT, "muddle_through", "australian_major_banks", "wbc")
    bi = build_bank_inputs_from_data(inp, "muddle_through")
    r = BankEngine().run(bi)
    d = BankEngine().derivation(bi, r)
    assert d.result == pytest.approx(r.value_per_share, abs=1e-9)


def test_retained_income_is_the_cost_of_equity_on_the_opening_retained_balance():
    """16 Oct 2026 (bridge item (e), option 1b). An independent hand computation of the cash
    earned on retained equity in the explicit years, checked against the engine's line. The
    audited workbook has no such line, so the workbook ties switch it off and this test is the
    check on it."""
    for scen in SCENARIOS:
        r = _run(scen)
        ke = r.cost_of_equity
        bal, pv = 0.0, 0.0
        for p in range(len(r.retained_by_period)):
            pv += ke * bal * r.period_length[p] * r.discount_factors[p]
            bal += r.retained_by_period[p]
        assert r.pv_retained_income == pytest.approx(pv, rel=1e-12), scen
        assert r.pv_retained_income > 0.0, scen
