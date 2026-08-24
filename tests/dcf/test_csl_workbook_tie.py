"""CSL: the segment engine ties to an independently recalculated Excel workbook.

The companion to ``test_dnl_workbook_tie.py``, and it exists for the same reason.
Wiring the derived 35% working-capital intensity into
``build_segment_inputs_from_data`` (23 Aug 2026, D-30) retires the v4 workbook
tie in ``test_csl_segment.py``, which was struck at the hand-typed 10%. Replacing
one oracle with none would leave the engine certifying itself.

The oracle (``golden/csl_workbook_all_scenarios.json``) comes from
``golden/_recalc_generated_workbooks.py``, which recalculates the generated CSL
workbook in LibreOffice. The workbook is formula-only and regenerates from the
data files, so it cannot drift from the register the way a hand-built file can.

Note the index offset: the workbook's group vectors run FY26..FY31, the engine's
run FY25..FY31, so the engine side is sliced from index 1.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from vcc_valuations.dcf.segment_engine import SegmentEngine
from vcc_valuations.translator import build_segment_inputs_from_data, load_inputs

ROOT = Path(__file__).resolve().parents[2]
ORACLE = json.loads(
    (Path(__file__).parent / "golden" / "csl_workbook_all_scenarios.json").read_text()
)
SCENARIOS = list(ORACLE)
FROM_FY25 = {"group_revenue", "group_ebit"}      # engine carries the FY25 anchor
VECTORS = ["group_revenue", "group_ebit", "wc_change", "fcff"]
SCALARS = ["pv_explicit", "terminal_fcff", "terminal_value", "pv_terminal",
           "enterprise_value", "equity_value", "value_per_share_usd",
           "value_per_share_aud"]


def _result(scenario: str):
    inputs = load_inputs(ROOT, scenario, "biopharmaceuticals", "csl")
    return SegmentEngine().run(build_segment_inputs_from_data(inputs, scenario))


@pytest.fixture(scope="module")
def results():
    return {s: _result(s) for s in SCENARIOS}


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("attr", VECTORS)
def test_line_vectors_tie_to_workbook(results, scenario: str, attr: str) -> None:
    got = getattr(results[scenario], attr)
    if attr in FROM_FY25:
        got = got[1:]
    want = ORACLE[scenario]["vectors"][attr]
    assert len(got) == len(want), f"{attr}: {len(got)} vs {len(want)}"
    for year, (g, w) in enumerate(zip(got, want)):
        assert g == pytest.approx(w, rel=1e-6, abs=1e-6), (
            f"{scenario}.{attr}[{year}]: engine {g}, workbook {w}"
        )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_scalars_tie_to_workbook(results, scenario: str) -> None:
    for attr in SCALARS:
        got = getattr(results[scenario], attr)
        want = ORACLE[scenario]["scalars"][attr]
        assert got == pytest.approx(want, rel=1e-6, abs=1e-6), (
            f"{scenario}.{attr}: engine {got}, workbook {want}"
        )


def test_intensity_is_the_derived_figure_not_the_retired_ten_percent(results) -> None:
    """The defect this work fixes: a stored 10% against a derived 35%.

    Checked as a ratio off the engine's own vectors rather than against a
    hard-coded 0.35, so the test follows the data file if the clean-years
    judgement is ever revised, and still fails loudly if the wiring reverts to
    a stored driver.
    """
    from vcc_valuations.translator import working_capital_intensity_from_data

    expected = working_capital_intensity_from_data(
        load_inputs(ROOT, "muddle_through", "biopharmaceuticals", "csl")
    ).result
    for scenario, r in results.items():
        for y in range(1, len(r.wc_change)):
            revenue_step = r.group_revenue[y + 1] - r.group_revenue[y]
            assert -r.wc_change[y] == pytest.approx(
                expected * revenue_step, rel=1e-9
            ), f"{scenario} year {y}"
