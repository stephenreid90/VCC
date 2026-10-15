"""Item (c), step 1 (15 Oct 2026): the CSL segment growth splits into volume and price.

The split is reporting only. Price is the archetype's declared price rate (advanced CPI),
volume is the remainder of the nominal driver. The nominal path is unchanged, so no level
moves. These tests pin that.
"""

from pathlib import Path

import pytest

from vcc_valuations.translator import (
    load_inputs,
    segment_growth_path_from_data,
    segment_volume_price_split,
)

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = ["orderly_convergence", "muddle_through", "ai_productivity_lag",
             "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists"]
SEGMENTS = ["csl_behring", "csl_seqirus", "csl_vifor"]
H = 10


def _inputs(scenario):
    return load_inputs(ROOT, scenario, "biopharmaceuticals", "csl")


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("seg", SEGMENTS)
def test_volume_plus_price_is_the_nominal_path(scenario, seg):
    inp = _inputs(scenario)
    s = segment_volume_price_split(inp, scenario, seg, H)
    nominal = segment_growth_path_from_data(inp, scenario, seg, H)
    for t in range(H):
        assert s["volume"][t] + s["price"][t] == pytest.approx(nominal[t], abs=1e-12)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_price_is_advanced_cpi_in_every_year(scenario):
    from vcc_valuations.translator import macro_series_at
    inp = _inputs(scenario)
    s = segment_volume_price_split(inp, scenario, "csl_behring", H)
    for t in range(H):
        assert s["price"][t] == pytest.approx(macro_series_at(inp, "cpi_inflation_advanced", t + 1), abs=1e-12)


def test_the_split_is_reporting_only_and_moves_no_level():
    # The engine's pinned Muddle Through level is unchanged by building the split.
    from vcc_valuations.dcf.segment_engine import SegmentEngine
    from vcc_valuations.translator import build_segment_inputs_from_data
    inp = _inputs("muddle_through")
    before = SegmentEngine().run(build_segment_inputs_from_data(inp, "muddle_through")).value_per_share_aud
    segment_volume_price_split(inp, "muddle_through", "csl_seqirus", H)
    after = SegmentEngine().run(build_segment_inputs_from_data(inp, "muddle_through")).value_per_share_aud
    assert after == pytest.approx(before, abs=1e-9)
