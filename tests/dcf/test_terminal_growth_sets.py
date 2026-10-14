"""The terminal-growth set is regenerable, and D-79's disclosure is pinned.

D-72 and D-79. The committed set in ``design/methodology/terminal_growth_sets.yaml`` is
the published table; this test is the ``asserted_by`` half of the standing-rule-4
contract -- regenerate from the production engines and the committed figures must come
back. The pins below are the sentences D-79 makes in DECISIONS.md, as numbers.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from size_terminal_growth import as_set, collect  # noqa: E402

SET_PATH = ROOT / "design" / "methodology" / "terminal_growth_sets.yaml"


@pytest.fixture(scope="module")
def rows():
    return collect()


@pytest.fixture(scope="module")
def by_key(rows):
    return {(r.company_id, r.scenario_id): r for r in rows}


@pytest.fixture(scope="module")
def committed():
    return yaml.safe_load(SET_PATH.read_text(encoding="utf-8"))


def test_the_committed_set_regenerates(rows, committed):
    """Standing rule 4: the published table comes back from the engines."""
    assert as_set(rows) == committed, (
        "design/methodology/terminal_growth_sets.yaml is stale -- "
        "run scripts/size_terminal_growth.py"
    )


def test_every_valuation_is_covered(rows):
    scenarios = sorted(p.stem for p in (ROOT / "data" / "scenarios").glob("*.yaml"))
    assert len(rows) == 3 * len(scenarios)
    assert {r.company_id for r in rows} == {"dnl", "wbc", "csl"}


def test_g_is_the_capped_chain_everywhere(rows):
    for r in rows:
        assert r.g == pytest.approx(min(r.g_chain, r.g_cap), abs=1e-12), (r.company_id, r.scenario_id)
        assert r.capped == (r.g_cap < r.g_chain)


def test_the_cap_binds_where_the_chain_outgrows_the_world(by_key):
    """Orderly Convergence for all three; Muddle Through and AI Productivity Lag for CSL
    (Vifor's share of the group has grown by Y10; AI Lag sits 1bp over the cap)."""
    capped = {k for k, r in by_key.items() if r.capped}
    assert capped == {
        ("dnl", "orderly_convergence"), ("wbc", "orderly_convergence"),
        ("csl", "orderly_convergence"), ("csl", "muddle_through"), ("csl", "ai_productivity_lag"),
    }


def test_nominal_gdp_at_year_ten_is_about_five_percent_in_every_scenario(rows):
    """The disclosure's premise: the scenario files assert 4.9-5.6% nominal GDP at Y10,
    about 2pp above the typed 3-3.5% that D-79 retired. If scenario development
    lowers the year-10 CPI, this moves and the levels move with it."""
    for r in rows:
        assert 0.048 < r.g_cap < 0.057, (r.scenario_id, r.g_cap)


def test_d79_moved_the_levels_as_disclosed(by_key):
    """The movement from the typed rate to the derived one, as D-79 states it:
    WBC +17% / +7% / +7% / +3% / +0.5% / -3%; CSL +11% / +12% / +9% / +5% / +5% / -1%."""
    want = {
        ("wbc", "orderly_convergence"): 0.167, ("wbc", "muddle_through"): 0.065,
        ("wbc", "ai_productivity_lag"): 0.071, ("wbc", "fragmentation"): 0.030,
        ("wbc", "disorderly_climate_crystallisation"): 0.005, ("wbc", "stagflation_persists"): -0.028,
        ("csl", "orderly_convergence"): 0.114, ("csl", "muddle_through"): 0.120,
        ("csl", "ai_productivity_lag"): 0.095, ("csl", "fragmentation"): 0.048,
        ("csl", "disorderly_climate_crystallisation"): 0.046, ("csl", "stagflation_persists"): -0.010,
    }
    for k, pct in want.items():
        assert by_key[k].level_change == pytest.approx(pct, abs=0.0015), (k, by_key[k].level_change)
    for k, r in by_key.items():
        if k[0] == "dnl":
            assert r.retired_typed_growth is None and r.level_change is None
