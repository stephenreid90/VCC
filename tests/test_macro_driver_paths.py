"""D-72: the derived macro-driver paths in the scenario files regenerate from their basis.

Standing rule 4. ``scripts/derive_macro_driver_paths.py`` writes
``global_mining_real_growth`` and ``gas_price_growth`` into every scenario file
from (a) the scenario's own ``real_gdp_growth_world`` series and ``time_profile``
and (b) the level anchors DNL carries in ``revenue_growth_chain.by_scenario``.
This asserts the committed series are exactly that derivation -- so a hand edit
to either side fails here rather than silently drifting -- and pins the two
rulings the derivation encodes (spread not multiple; transition-then-baseline).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from derive_macro_driver_paths import (  # noqa: E402
    ANCHOR_YEARS, BASELINE_SCENARIO, DERIVED, SCENARIOS, derive, level_anchors,
)


def _committed(scenario_id, variable):
    doc = yaml.safe_load((ROOT / "data" / "scenarios" / f"{scenario_id}.yaml").read_text(encoding="utf-8"))
    for mv in doc["scenario"]["macro_variables"]:
        if mv["variable"] == variable:
            return [(p["year"], p["value"]) for p in mv["time_series"]]
    raise KeyError((scenario_id, variable))


@pytest.mark.parametrize("scenario_id", SCENARIOS)
@pytest.mark.parametrize("variable", DERIVED)
def test_committed_series_equal_the_derivation(scenario_id, variable):
    assert _committed(scenario_id, variable) == derive(scenario_id)[variable], (
        "data/scenarios/%s.yaml %s is stale -- rerun "
        "`PYTHONPATH=src python scripts/derive_macro_driver_paths.py --write`"
        % (scenario_id, variable)
    )


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_series_sit_on_d37_anchor_years(scenario_id):
    for variable in DERIVED:
        assert [y for y, _ in _committed(scenario_id, variable)] == list(ANCHOR_YEARS)


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_mining_is_world_gdp_plus_a_fixed_gap_averaging_to_the_anchor(scenario_id):
    """Decision 2: spread, not multiple. The path's mean reproduces the level anchor."""
    series = _committed(scenario_id, "global_mining_real_growth")
    anchor = level_anchors()[scenario_id]["global_mining_real_growth"] * 100.0
    assert sum(v for _, v in series) / len(series) == pytest.approx(anchor, abs=0.011)


def test_a_multiple_would_hold_stagflation_at_zero_forever():
    """Why decision 2 is a spread: the Stagflation anchor is 0.0%, and 0 x anything is 0."""
    series = _committed("stagflation_persists", "global_mining_real_growth")
    assert any(v != 0.0 for _, v in series)
    assert min(v for _, v in series) < 0 < max(v for _, v in series)


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_gas_runs_at_the_anchor_through_transition_then_the_baseline(scenario_id):
    """Decision 3."""
    anchors = level_anchors()
    eq = derive(scenario_id)["_eq"]
    transition = anchors[scenario_id]["gas_price_growth"] * 100.0
    baseline = anchors[BASELINE_SCENARIO]["gas_price_growth"] * 100.0
    for year, value in _committed(scenario_id, "gas_price_growth"):
        assert value == pytest.approx(transition if year < eq else baseline), (scenario_id, year)


def test_ai_lag_gas_is_the_baseline_by_absence_not_by_view():
    """The AI Lag write-up never assessed gas (gap audit §2); its anchor equals the baseline."""
    anchors = level_anchors()
    assert anchors["ai_productivity_lag"]["gas_price_growth"] == anchors[BASELINE_SCENARIO]["gas_price_growth"]
