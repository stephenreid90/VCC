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
        build_bank_inputs_from_data(load_inputs(ROOT, "muddle_through",
                                                "australian_major_banks", "wbc"),
                                    "muddle_through"),
        constrain_payout_to_capital=False,
    ))
    # headline value per share (workbook DDM + ROE-fade terminal)
    assert r.value_per_share == pytest.approx(30.0304, abs=1e-3)
    # key bridge lines tie the audited workbook
    assert r.closing_book_equity == pytest.approx(83682.114, abs=0.1)
    assert r.terminal_value == pytest.approx(128741.71, abs=1.0)
    assert r.pv_terminal_value == pytest.approx(85079.86, abs=1.0)
    assert r.ordinary_equity_value == pytest.approx(102550.79, abs=1.0)
    # cost of equity is Rf + beta*ERP = 4.30% + 0.75*5.00%
    assert r.cost_of_equity == pytest.approx(0.0805, abs=1e-6)


def test_muddle_through_with_the_capital_constraint_is_the_ratified_level():
    """D-60 on: the level the register carries, and the gap to the workbook tie.

    The whole difference between this and the test above is the dividends the
    capital constraint withholds from Y5, retained into closing equity and
    capitalised in the terminal. Asserting both means the size of the overlay is
    visible in the suite rather than inferred from two numbers in a comment.
    """
    r = _run("muddle_through")
    assert r.value_per_share == pytest.approx(30.0664, abs=1e-3)
    assert r.capital_constraint_binds_from == "Y5"
    assert r.cost_of_equity == pytest.approx(0.0805, abs=1e-6)
    # Closing equity is the workbook's, plus exactly what was withheld.
    assert r.closing_book_equity - r.dividends_forgone == pytest.approx(83682.114, abs=0.1)


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
