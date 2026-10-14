"""D-71 terminal form in the bank and segment engines (bridge note step 2, 14 Oct 2026).

No data path selects convergence for WBC or CSL yet (no decay horizon is declared;
tests/terminal_form_baseline.json lists all twelve pairs), so the form is proven on
the live inputs with the horizon set by hand. The same four facts the industrial
engine pins: N -> infinity reproduces Gordon on the earned/declared return; N = 0
is convergence at the forecast end (TV = capital); the form is symmetric in the
excess; and the inputs are validated.
"""

from __future__ import annotations

import math
from dataclasses import replace
from pathlib import Path

import pytest

from vcc_valuations.dcf.bank_engine import BankEngine
from vcc_valuations.dcf.segment_engine import SegmentEngine
from vcc_valuations.translator import (
    build_bank_inputs_from_data, build_segment_inputs_from_data, csl_terminal_invested_capital, load_inputs,
)

ROOT = Path(__file__).resolve().parents[2]


def _bank(s="muddle_through"):
    return build_bank_inputs_from_data(load_inputs(ROOT, s, "australian_major_banks", "wbc"), s)


def _seg(s="muddle_through"):
    inp = load_inputs(ROOT, s, "biopharmaceuticals", "csl")
    si = build_segment_inputs_from_data(inp, s)
    return si, csl_terminal_invested_capital(inp, s)


# ------------------------------------------------------------------ bank
def test_bank_data_path_is_gordon_fallback_today():
    r = BankEngine().run(_bank())
    assert r.terminal_form == "gordon" and r.convergence_years is None


def test_bank_convergence_at_infinity_is_the_justified_price_to_book():
    base = BankEngine().run(_bank())
    conv = BankEngine().run(replace(_bank(), terminal_form="excess_return_convergence", convergence_years=math.inf))
    assert conv.terminal_value == pytest.approx(base.terminal_value, rel=1e-12)
    assert conv.value_per_share == pytest.approx(base.value_per_share, rel=1e-12)


def test_bank_convergence_at_zero_years_is_closing_equity():
    conv = BankEngine().run(replace(_bank(), terminal_form="excess_return_convergence", convergence_years=0))
    assert conv.terminal_value == pytest.approx(conv.closing_book_equity, rel=1e-12)


def test_bank_convergence_is_symmetric_in_the_excess():
    """ROE above Ke converges DOWN (TV below Gordon); ROE below Ke converges UP (TV above Gordon)."""
    inp = _bank()
    ke = inp.cost_of_equity
    for roe in (ke + 0.02, ke - 0.02):
        g = replace(inp, terminal_roe=roe)
        gordon = BankEngine().run(g)
        conv = BankEngine().run(replace(g, terminal_form="excess_return_convergence", convergence_years=12.5))
        if roe > ke:
            assert conv.terminal_value < gordon.terminal_value
        else:
            assert conv.terminal_value > gordon.terminal_value
        # and strictly between TV(0) = C and TV(inf) = Gordon
        assert min(gordon.terminal_value, conv.closing_book_equity) < conv.terminal_value < max(gordon.terminal_value, conv.closing_book_equity)


def test_bank_convergence_inputs_are_validated():
    with pytest.raises(ValueError):
        BankEngine().run(replace(_bank(), terminal_form="excess_return_convergence"))
    with pytest.raises(ValueError):
        BankEngine().run(replace(_bank(), terminal_form="three_phase"))


# --------------------------------------------------------------- segment
def test_segment_data_path_is_gordon_fallback_today():
    si, _ = _seg()
    r = SegmentEngine().run(si)
    assert r.terminal_form == "gordon" and r.terminal_earned_return is None


def test_segment_convergence_at_infinity_is_gordon_on_the_earned_return():
    """At N -> inf the two-stage form is C x (R-g)/(Ke-g) with R the earned return on C."""
    si, cap = _seg()
    conv = SegmentEngine().run(replace(si, terminal_form="excess_return_convergence",
                                       convergence_years=math.inf, terminal_invested_capital=cap))
    ke, g = si.cost_of_equity, si.terminal_growth
    assert conv.terminal_earned_return is not None
    assert conv.terminal_value == pytest.approx(cap * (conv.terminal_earned_return - g) / (ke - g), rel=1e-12)


def test_segment_convergence_at_zero_years_is_the_capital_base():
    si, cap = _seg()
    conv = SegmentEngine().run(replace(si, terminal_form="excess_return_convergence",
                                       convergence_years=0, terminal_invested_capital=cap))
    assert conv.terminal_value == pytest.approx(cap, rel=1e-12)


def test_csl_earns_well_above_ke_so_convergence_cuts_the_terminal():
    """D-67: CSL earns 18-25% on its capital base against an 8.75% Ke, so a finite
    moat is worth less than the Gordon terminal that holds that return forever."""
    si, cap = _seg()
    gordon = SegmentEngine().run(si)
    conv = SegmentEngine().run(replace(si, terminal_form="excess_return_convergence",
                                       convergence_years=12.5, terminal_invested_capital=cap))
    assert conv.terminal_earned_return > si.cost_of_equity
    assert cap < conv.terminal_value < gordon.terminal_value
    assert conv.value_per_share_aud < gordon.value_per_share_aud


def test_segment_convergence_inputs_are_validated():
    si, cap = _seg()
    with pytest.raises(ValueError):
        SegmentEngine().run(replace(si, terminal_form="excess_return_convergence", convergence_years=12.5))
    with pytest.raises(ValueError):
        SegmentEngine().run(replace(si, terminal_form="excess_return_convergence", terminal_invested_capital=cap))
    with pytest.raises(ValueError):
        SegmentEngine().run(replace(si, terminal_form="three_phase"))
