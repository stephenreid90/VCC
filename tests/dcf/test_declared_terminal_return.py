"""D-76 (14 Oct 2026): the declared terminal return is the rate the convergence starts from.

One rule in all three engines: where the impact matrix declares a terminal return
(``excess_return_defence.declared_terminal_return``) the two-stage convergence
starts from it (D-64's return lever: capital held, earnings flexed); where none is
declared it starts from the return the explicit period leaves the capital base
earning. The diagnostic keeps reporting declared against earned.

What the data path carries today: WBC declares all six (lifted off wbc.yaml, no
level moved); DNL and CSL declare none, so the earned return governs. The rule
itself is proven on live inputs with the rate set by hand.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from vcc_valuations.dcf.bank_engine import BankEngine
from vcc_valuations.dcf.fcf_engine import FcfEngine
from vcc_valuations.dcf.segment_engine import SegmentEngine
from vcc_valuations.dcf.terminal_value import two_stage
from vcc_valuations.translator import (
    build_bank_inputs_from_data, build_engine_inputs_from_data,
    build_segment_inputs_from_data, declared_terminal_return_from_matrix, load_inputs,
)

ROOT = Path(__file__).resolve().parents[2]
S = "muddle_through"


def _dnl():
    return build_engine_inputs_from_data(load_inputs(ROOT, S, "industrial_explosives", "dnl"), S)


def _wbc():
    return build_bank_inputs_from_data(load_inputs(ROOT, S, "australian_major_banks", "wbc"), S)


def _csl():
    return build_segment_inputs_from_data(load_inputs(ROOT, S, "biopharmaceuticals", "csl"), S)


# ---------------------------------------------------------------- the data path
def test_wbc_reads_its_terminal_roe_from_the_matrix_and_dnl_csl_declare_none():
    for sid, roe in {"orderly_convergence": 0.11, "muddle_through": 0.105,
                     "ai_productivity_lag": 0.105, "fragmentation": 0.10,
                     "disorderly_climate_crystallisation": 0.09,
                     "stagflation_persists": 0.09}.items():
        inp = load_inputs(ROOT, sid, "australian_major_banks", "wbc")
        assert declared_terminal_return_from_matrix(inp, sid) == pytest.approx(roe)
        assert build_bank_inputs_from_data(inp, sid).terminal_roe == pytest.approx(roe)
        assert "terminal_roe" not in (
            inp["company_raw"]["normalised_baseline"]["bank_build"]["overlays"]["by_scenario"][sid])
    for sid in ["muddle_through", "orderly_convergence", "fragmentation"]:
        assert declared_terminal_return_from_matrix(
            load_inputs(ROOT, sid, "industrial_explosives", "dnl"), sid) is None
        assert declared_terminal_return_from_matrix(
            load_inputs(ROOT, sid, "biopharmaceuticals", "csl"), sid) is None


# ------------------------------------------------------- the rule, per engine
def test_industrial_engine_starts_the_convergence_from_the_declared_rate():
    base = FcfEngine().run(_dnl())
    assert base.terminal_form == "excess_return_convergence"
    assert base.declared_terminal_return is None
    assert base.terminal_convergence_return == pytest.approx(base.terminal_earned_return)
    declared = 0.11
    res = FcfEngine().run(replace(_dnl(), declared_terminal_return=declared))
    assert res.terminal_convergence_return == pytest.approx(declared)
    assert res.terminal_earned_return == pytest.approx(base.terminal_earned_return)
    assert res.terminal_value == pytest.approx(two_stage(
        res.terminal_invested_capital, declared, res.wacc, res.terminal_growth, res.convergence_years))
    # a rate below the earned one lowers the level: the lever moves the way D-64 says
    assert res.value_per_share < base.value_per_share
    assert any("declares a terminal return" in w for w in res.warnings)


def test_segment_engine_starts_the_convergence_from_the_declared_rate():
    base = SegmentEngine().run(_csl())
    assert base.terminal_form == "excess_return_convergence"
    assert base.declared_terminal_return is None
    assert base.terminal_convergence_return == pytest.approx(base.terminal_earned_return)
    declared = 0.15
    res = SegmentEngine().run(replace(_csl(), declared_terminal_return=declared))
    assert res.terminal_convergence_return == pytest.approx(declared)
    si = _csl()
    assert res.terminal_value == pytest.approx(two_stage(
        si.terminal_invested_capital, declared, si.cost_of_equity, si.terminal_growth,
        res.convergence_years))
    assert res.value_per_share_aud < base.value_per_share_aud


def test_bank_engine_falls_back_to_the_earned_roe_when_nothing_is_declared():
    live = BankEngine().run(_wbc())
    assert live.declared_terminal_return == pytest.approx(0.105)
    assert live.terminal_roe == pytest.approx(0.105)
    assert live.terminal_earned_return == pytest.approx(
        live.cash_npat[-1] * (1.0 + _wbc().terminal_growth) / live.closing_book_equity)
    fallback = BankEngine().run(replace(_wbc(), terminal_roe=None))
    assert fallback.declared_terminal_return is None
    assert fallback.terminal_roe == pytest.approx(fallback.terminal_earned_return)
    # earned sits above declared in Muddle Through, so the fallback is worth more
    assert fallback.value_per_share > live.value_per_share


def test_the_rule_is_one_rule():
    """Declared where present, earned otherwise -- identical across engines."""
    for res in (FcfEngine().run(_dnl()), SegmentEngine().run(_csl())):
        assert res.terminal_convergence_return == (
            res.declared_terminal_return if res.declared_terminal_return is not None
            else res.terminal_earned_return)
    b = BankEngine().run(_wbc())
    assert b.terminal_roe == (b.declared_terminal_return if b.declared_terminal_return is not None
                              else b.terminal_earned_return)
