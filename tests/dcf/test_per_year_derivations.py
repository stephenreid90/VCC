"""Task 2: the per-year operating build is surfaced as a Derivation for all three engines.

Each engine's ``per_year_derivation`` reads the year-by-year build out of the engine's own
result (revenue / profit / cash line per period), so the workings can be rendered without
re-deriving anything. These tests pin that the derivation rows tie the result arrays.
"""

from pathlib import Path

import pytest

from vcc_valuations.dcf.bank_engine import BankEngine
from vcc_valuations.dcf.fcf_engine import FcfEngine
from vcc_valuations.dcf.segment_engine import SegmentEngine
from vcc_valuations.translator import (
    build_bank_inputs_from_data, build_engine_inputs_from_data,
    build_segment_inputs_from_data, load_inputs,
)

ROOT = Path(__file__).resolve().parents[2]


def test_dnl_per_year_derivation_ties_result():
    inp = load_inputs(ROOT, "muddle_through", "industrial_explosives", "dnl")
    r = FcfEngine().run(build_engine_inputs_from_data(inp, "muddle_through"))
    d = FcfEngine().per_year_derivation(r)
    # last explicit year's FCFF is the headline and ties the result array
    assert d.result == pytest.approx(r.fcff[-1], abs=1e-9)
    # each period contributes a revenue / EBIT / FCFF row that ties
    assert d[f"{r.period_labels[0]}_rev"].value == pytest.approx(r.revenue[0], abs=1e-9)
    assert d[f"{r.period_labels[-1]}_ebit"].value == pytest.approx(r.ebit[-1], abs=1e-9)
    assert len(d) == 3 * len(r.period_labels)


def test_wbc_per_year_derivation_ties_result():
    inp = load_inputs(ROOT, "muddle_through", "australian_major_banks", "wbc")
    r = BankEngine().run(build_bank_inputs_from_data(inp, "muddle_through"))
    d = BankEngine().per_year_derivation(r)
    assert d.result == pytest.approx(r.dividends[-1], abs=1e-9)
    assert d[f"{r.period_labels[-1]}_npat"].value == pytest.approx(r.cash_npat[-1], abs=1e-9)


def test_csl_per_year_derivation_ties_result():
    inp = load_inputs(ROOT, "muddle_through", "biopharmaceuticals", "csl")
    r = SegmentEngine().run(build_segment_inputs_from_data(inp, "muddle_through"))
    d = SegmentEngine().per_year_derivation(r)
    assert d.result == pytest.approx(r.fcff[-1], abs=1e-9)
    # FY26..FY31 (skips the FY25 anchor): 6 years x 3 lines
    assert len(d) == 3 * (len(r.year_labels) - 1)
    assert d["FY31_ebit"].value == pytest.approx(r.group_ebit[-1], abs=1e-9)
