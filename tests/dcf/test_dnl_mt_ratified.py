"""DNL x Muddle Through — the RATIFIED production valuation (beta 1.10, data-driven).

The discount rate is built from the data files via
``translator.build_wacc_from_inputs`` rather than hardcoded: beta 1.10
(peer-triangulation, ratified 25 Jul 2026) with the methodology-§5.3-anchored E/V
weights (equity 6,390 / debt 1,260.8). This is the first end-to-end M2 wiring —
the discount-rate half of ``AssumptionSet -> FcfEngineInputs`` — driven from the
YAML rather than a hand-typed constant.

It SUPERSEDES the beta-0.95 workbook headline of 3.484 as the production per-share.
``test_e2e_dnl_mt.py`` retains 3.484 only as the engine-mechanics oracle: the engine
faithfully reproduces the audited v6 workbook when fed its (now beta-stale) inputs,
which validates the mechanics independently of any figure the engine itself emits.

The per-year structural overlays (margin glide, gas roll-off, tax glide, capex step,
the Fertilisers-separation equity bridge, the revenue-growth chain) still come from
the hand-typed ``dnl_mt_inputs`` stand-in; migrating those into the data files is the
remaining M2 work. This test wires the WACC half and pins the ratified result.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from vcc_valuations.translator import load_inputs, build_wacc_from_inputs
from vcc_valuations.dcf.fcf_engine import FcfEngine
from tests.dcf.golden.dnl_mt_inputs import dnl_muddle_through_inputs

ROOT = Path(__file__).resolve().parents[2]


def _load():
    return load_inputs(
        ROOT,
        scenario_id="muddle_through",
        archetype_id="industrial_explosives",
        company_id="dnl",
    )


def test_discount_rate_is_data_driven():
    """The WACC is assembled from the YAML, not hardcoded: ratified beta 1.10
    over the §5.3-anchored E/V weights."""
    w = build_wacc_from_inputs(_load())
    assert w.beta == 1.10                      # peer-triangulation, ratified 25 Jul 2026
    assert w.equity_market_value == 6390.0     # methodology §5.3 anchor
    assert w.debt_market_value == 1260.8
    assert abs(w.equity_weight - 0.8352) < 1e-3


def test_dnl_mt_ratified_per_share():
    """End-to-end: data-driven WACC into the engine over the (still hand-typed)
    structural overlays. Pins the ratified beta-1.10 production valuation."""
    inp = dataclasses.replace(dnl_muddle_through_inputs(), wacc=build_wacc_from_inputs(_load()))
    r = FcfEngine().run(inp)
    assert abs(r.wacc - 0.088772) < 1e-4
    assert round(r.value_per_share, 3) == 3.073     # supersedes beta-0.95 3.484
    assert round(r.enterprise_value, 1) == 7009.2
    # sanity: still a terminal-heavy DCF, below market
    assert r.value_per_share < r.market_reference_price
