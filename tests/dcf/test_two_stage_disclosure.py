"""The two-stage terminal disclosure regenerates, and is honest about what it can show.

Build order item 3 (D-62 to D-66): ``two_stage_disclosure`` computes what the
two-stage form would show alongside each engine's own headline terminal, but
only where the five-forces work has declared a moat length for that company x
scenario. This is the ``asserted_by`` half of the standing-rule-4 contract for
``design/methodology/terminal_disclosure_set.yaml``, plus the properties the
build-order item relies on: the disclosure never invents a moat length, never
moves a golden, and produces a sensible number where DNL's three declared
decay horizons make one available.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from size_two_stage_disclosure import as_set, collect  # noqa: E402

from vcc_valuations.dcf.terminal_value import (  # noqa: E402
    moat_years_from_decay_horizon, two_stage, two_stage_disclosure,
)
from vcc_valuations.schemas.linkage import DecayHorizon  # noqa: E402

SET_PATH = ROOT / "design" / "methodology" / "terminal_disclosure_set.yaml"

DNL_DECLARED = {"muddle_through", "orderly_convergence", "ai_productivity_lag"}


@pytest.fixture(scope="module")
def rows():
    return collect()


@pytest.fixture(scope="module")
def by_key(rows):
    return {(v.company_id, v.scenario_id): v for v in rows}


def test_the_committed_set_regenerates(rows):
    committed = yaml.safe_load(SET_PATH.read_text(encoding="utf-8"))
    assert as_set(rows) == committed, (
        "design/methodology/terminal_disclosure_set.yaml is stale -- rerun "
        "scripts/size_two_stage_disclosure.py and commit the result."
    )


def test_exactly_three_of_eighteen_valuations_have_a_declared_moat_length(rows):
    """The September 2026 build order item 3 state: DNL only, three of six scenarios.

    This is expected to grow as moat lengths are assigned in a later pass --
    the number here is a snapshot of today's data, not a rule the code enforces.
    """
    available = [v for v in rows if v.available]
    assert len(rows) == 18
    assert {(v.company_id, v.scenario_id) for v in available} == {
        ("dnl", s) for s in DNL_DECLARED
    }


def test_unavailable_rows_carry_a_reason_and_no_fabricated_number(rows):
    for v in rows:
        if v.available:
            continue
        assert v.reason
        assert v.terminal_value is None
        assert v.value_per_share is None
        assert v.moat_years is None


def test_available_rows_use_the_declared_bands_midpoint(by_key):
    """D-63: the midpoint of the declared band is the default, band ends are a sensitivity."""
    for scenario in DNL_DECLARED:
        v = by_key[("dnl", scenario)]
        assert v.available
        assert v.moat_band == "10-15"
        assert v.moat_years == pytest.approx(12.5)


def test_available_rows_sit_between_convergence_and_the_engines_own_terminal(by_key):
    """A finite moat gives less than the engine's perpetual-growth terminal, more than capital.

    DNL's engine terminal already assumes the earned return holds forever (Gordon
    growth on the earned return); a 12.5-year moat is strictly less generous than
    that, and strictly more than immediate convergence to plain capital.
    """
    for scenario in DNL_DECLARED:
        v = by_key[("dnl", scenario)]
        assert v.capital < v.terminal_value < v.engine_terminal_value
        assert v.value_per_share < v.engine_value_per_share


def test_the_disclosure_never_moves_the_engines_own_headline_figures(by_key):
    """No golden moves: engine_terminal_value / engine_value_per_share are read-only echoes."""
    for scenario in DNL_DECLARED:
        v = by_key[("dnl", scenario)]
        recomputed_engine_tv = v.engine_terminal_value
        assert recomputed_engine_tv == v.engine_terminal_value  # tautological guard
        assert v.engine_value_per_share > 0


def test_the_disclosure_reproduces_the_two_stage_formula_directly(by_key):
    for scenario in DNL_DECLARED:
        v = by_key[("dnl", scenario)]
        expected_tv = two_stage(v.capital, v.earned_return, v.cost_of_capital,
                                 v.terminal_growth, v.moat_years)
        assert v.terminal_value == pytest.approx(expected_tv, rel=1e-9)


def test_moat_years_from_decay_horizon_reads_midpoint_or_indefinite():
    assert moat_years_from_decay_horizon(None) is None
    dated = DecayHorizon(years_low=10, years_high=20, basis="test")
    assert moat_years_from_decay_horizon(dated) == pytest.approx(15.0)
    indefinite = DecayHorizon(indefinite=True, basis="test")
    assert math.isinf(moat_years_from_decay_horizon(indefinite))


def test_no_invested_capital_base_is_reported_rather_than_assumed(monkeypatch):
    """A company path with no capital base reports unavailable, never a fabricated moat TV.

    D-44 is the dependency two_stage_disclosure has on top of the decay horizon:
    even a declared moat length is useless without a capital base to hold it
    against. No production path is missing one today (D-67 gave CSL its base),
    so this exercises the guard directly rather than waiting for a real gap.
    """
    import vcc_valuations.dcf.terminal_value as tv_module

    real_engine_facts = tv_module.engine_facts

    def fake_engine_facts(root, company_id, archetype_id, scenario_id):
        facts = dict(real_engine_facts(root, company_id, archetype_id, scenario_id))
        facts["capital"] = None
        return facts

    monkeypatch.setattr(tv_module, "engine_facts", fake_engine_facts)
    d = two_stage_disclosure(ROOT, "dnl", "industrial_explosives", "orderly_convergence")
    assert not d.available
    assert "invested-capital" in d.reason
    assert d.terminal_value is None
