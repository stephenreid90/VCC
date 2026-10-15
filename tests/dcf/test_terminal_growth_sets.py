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
    """Orderly Convergence for all three; Muddle Through for DNL and CSL; AI Productivity
    Lag for CSL (Vifor's share of the group has grown by Y10). D-80 (14 Oct 2026) lowered
    the caps and DNL Muddle Through joined the list (chain 4.91% vs cap 4.86%)."""
    capped = {k for k, r in by_key.items() if r.capped}
    assert capped == {
        ("dnl", "orderly_convergence"), ("wbc", "orderly_convergence"),
        ("csl", "orderly_convergence"), ("csl", "muddle_through"), ("csl", "ai_productivity_lag"),
        ("dnl", "muddle_through"),
    }


def test_nominal_gdp_at_year_ten_is_four_and_a_half_to_five_percent_in_every_scenario(rows):
    """The disclosure's premise. Until D-80 the scenario files asserted 4.9-5.6% nominal
    GDP at Y10 (advanced CPI 2.3-3.5%). D-80 (14 Oct 2026, Stephen's ruling) lowered
    year-10 CPI to where central banks hold it over a decade (2.0-3.0%), so the caps
    are 4.55-5.06%: still 1-2pp above the typed 3-3.5% that D-79 retired. If scenario
    development moves the year-10 CPI again, this moves and the levels move with it."""
    for r in rows:
        assert 0.045 < r.g_cap < 0.051, (r.scenario_id, r.g_cap)
    assert {r.scenario_id: round(r.g_cap, 4) for r in rows} == {
        "orderly_convergence": 0.0506, "muddle_through": 0.0486, "ai_productivity_lag": 0.0455,
        "fragmentation": 0.0486, "disorderly_climate_crystallisation": 0.0475, "stagflation_persists": 0.0506,
    }


def test_d79_moved_the_levels_as_disclosed(by_key):
    """The movement from the retired typed rate to the derived one, on today's scenario
    files. D-79 stated it on the pre-D-80 files as WBC +17% / +7% / +7% / +3% / +0.5% /
    -3% and CSL +11% / +12% / +9% / +5% / +5% / -1%. D-80 (14 Oct 2026) lowered the
    year-10 CPI, so the derived rates sit closer to the typed ones and the movement is
    smaller: WBC +12% / +4% / +5% / +1% / -0.3% / -3.5%; CSL +9% / +9% / +8% / +3% /
    +3% / -2%. The typed rate's level is re-run on today's paths too, so this is a
    like-for-like reading of the growth judgement alone."""
    want = {
        ("wbc", "orderly_convergence"): 0.121, ("wbc", "muddle_through"): 0.038,
        ("wbc", "ai_productivity_lag"): 0.054, ("wbc", "fragmentation"): 0.013,
        ("wbc", "disorderly_climate_crystallisation"): -0.003, ("wbc", "stagflation_persists"): -0.035,
        # CSL re-pinned 15 Oct 2026 (item (c), US driver): OC 0.095 -> 0.0943, MT 0.090 -> 0.0899,
        # Frag 0.032 -> 0.0294, Stag -0.023 -> -0.011.
        ("csl", "orderly_convergence"): 0.0943, ("csl", "muddle_through"): 0.0899,
        ("csl", "ai_productivity_lag"): 0.078, ("csl", "fragmentation"): 0.0294,
        ("csl", "disorderly_climate_crystallisation"): 0.030, ("csl", "stagflation_persists"): -0.011,
    }
    for k, pct in want.items():
        assert by_key[k].level_change == pytest.approx(pct, abs=0.0015), (k, by_key[k].level_change)
    for k, r in by_key.items():
        if k[0] == "dnl":
            assert r.retired_typed_growth is None and r.level_change is None
