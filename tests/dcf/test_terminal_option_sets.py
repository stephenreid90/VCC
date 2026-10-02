"""The terminal-option set is regenerable, its maths inverts, and its findings are pinned.

``design/methodology/terminal_value.md`` (D-62 to D-66, PROPOSED) cites the committed
set in ``design/methodology/terminal_option_sets.yaml``. This test is the
``asserted_by`` half of the standing-rule-4 contract, plus the properties of the
two-stage form the paper relies on, plus the findings the paper is built around.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from size_terminal_options import (  # noqa: E402
    EXTENSION_GRID, as_set, collect, implied_moat, implied_perpetual_return,
    perpetual_multiple, two_stage,
)

SET_PATH = ROOT / "design" / "methodology" / "terminal_option_sets.yaml"


@pytest.fixture(scope="module")
def rows():
    return collect()


@pytest.fixture(scope="module")
def by_key(rows):
    return {(v.company_id, v.scenario_id): v for v in rows}


def _basis(v, name):
    return next(b for b in v.bases if b.name == name)


def test_the_committed_set_regenerates(rows):
    committed = yaml.safe_load(SET_PATH.read_text(encoding="utf-8"))
    assert as_set(rows) == committed, (
        "design/methodology/terminal_option_sets.yaml is stale -- "
        "run scripts/size_terminal_options.py"
    )


# ------------------------------------------------------------ the maths
@pytest.mark.parametrize("ret", [0.05, 0.0888, 0.1142, 0.16])
def test_two_stage_runs_from_capital_to_gordon(ret):
    c, r, g = 4000.0, 0.0888, 0.025
    assert two_stage(c, ret, r, g, 0) == c
    assert two_stage(c, ret, r, g, 10_000) == pytest.approx(
        c * perpetual_multiple(ret, r, g), rel=1e-9)


def test_two_stage_equals_capital_plus_pv_of_economic_profit():
    """The identity the paper leads with: TV = C + PV of N years of C_t x (R - r)."""
    c, ret, r, g, n = 4000.0, 0.1142, 0.0888, 0.025, 10
    pv_ep = sum(c * (1 + g) ** (t - 1) * (ret - r) / (1 + r) ** t for t in range(1, n + 1))
    assert two_stage(c, ret, r, g, n) == pytest.approx(c + pv_ep, rel=1e-12)


def test_return_equal_to_cost_of_capital_makes_the_moat_irrelevant():
    c, r, g = 4000.0, 0.0888, 0.025
    for n in (0, 5, 50):
        assert two_stage(c, r, r, g, n) == pytest.approx(c, rel=1e-12)


def test_the_return_lever_moves_value_the_way_a_user_expects():
    """D-64: hold capital, flex earnings. More return, more value, at any moat length."""
    c, r, g, n = 4000.0, 0.0888, 0.025, 10
    values = [two_stage(c, ret, r, g, n) for ret in (0.10, 0.12, 0.14, 0.16)]
    assert values == sorted(values)


def test_the_other_lever_convention_runs_backwards(by_key):
    """Paper section 6. Holding earnings and solving for capital makes a higher return
    LOWER the value. DNL Muddle Through, a ten-year moat beyond the forecast, 16%.

    Re-pinned 2 Oct 2026 (D-71): the explicit period is a fixed ten years, so
    "ten years from the valuation date" would now be a zero-length moat (TV =
    capital, nothing to compare). The test keeps its shape by sizing the paper's
    ten-year moat BEYOND the forecast instead; the direction is what it asserts.
    Earlier pins: 4379 / 3473 at a 6-year horizon with n = 4."""
    v = by_key[("dnl", "muddle_through")]
    e1 = v.capital * v.earned_return
    n = 10
    measured = two_stage(v.capital, v.earned_return, v.cost_of_capital, v.terminal_growth, n)
    backwards = two_stage(e1 / 0.16, 0.16, v.cost_of_capital, v.terminal_growth, n)
    assert measured == pytest.approx(5698, abs=1)
    assert backwards == pytest.approx(5359, abs=1)
    assert backwards < measured


@pytest.mark.parametrize("ret", [0.05, 0.1142])
@pytest.mark.parametrize("n", [1, 5, 10, 20, 40])
def test_implied_moat_inverts_the_two_stage_form(ret, n):
    c, r, g = 4000.0, 0.0888, 0.025
    m = implied_moat(two_stage(c, ret, r, g, n), c, ret, r, g)
    assert m.status == "finite"
    assert m.extension_years == pytest.approx(n, rel=1e-9)


def test_implied_perpetual_return_is_the_cost_of_capital_at_convergence():
    assert implied_perpetual_return(4000.0, 4000.0, 0.0888, 0.025) == pytest.approx(0.0888)


def test_engine_current_reproduces_every_engine_value_per_share(rows):
    """The per-share translation swaps the TV and nothing else."""
    # DNL re-pinned 25 Sep 2026 for D-35/D-36 (1.9895 -> 1.8461). Re-pinned again
    # the same day for the D-49 terminal-capex roll-forward fix (1.8734 -> 1.8461):
    # that roll-forward was still compounding revenue at a flat re-derived rate
    # instead of D-36's actual per-year fade path, which had been overstating the
    # earned return the component terminal capitalises.
    # DNL re-pinned 2 Oct 2026 for D-71 (1.8461 -> 1.9422): fixed ten-year
    # horizon, excess-return convergence headline.
    pinned = {("dnl", "muddle_through"): 1.9422, ("wbc", "muddle_through"): 30.0304,
              ("csl", "muddle_through"): 195.7835}
    for key, vps in pinned.items():
        v = next(x for x in rows if (x.company_id, x.scenario_id) == key)
        assert _basis(v, "engine_current").value_per_share == pytest.approx(vps, abs=1e-4)


# ------------------------------------------------------------ findings
def test_the_current_terminal_carries_the_moat_the_five_forces_work_chose(by_key):
    """Finding 1, resolved by D-71 (2 Oct 2026).

    Until D-71 this test recorded that DNL's component-built Gordon terminal
    IMPLIED a moat nobody had chosen -- 58 to 64 years on the three above-WACC
    scenarios. The headline terminal is now excess-return convergence over the
    declared decay horizon, so inverting the headline gives back exactly the
    moat the five-forces work declared: 12.5 years, the 10-15 band's midpoint.
    The finding is kept as its own resolution. WBC's declared terminal ROEs
    still imply 17 to 37 years and are untouched by D-71 (no decay horizon has
    been declared for the bank; see tests/dcf/test_terminal_form.py)."""
    for s in ("muddle_through", "ai_productivity_lag", "orderly_convergence"):
        m = _basis(by_key[("dnl", s)], "engine_current").implied_moat
        assert m.status == "finite", (s, m)
        assert m.extension_years == pytest.approx(12.5, abs=1e-6), (s, m)
    for s in ("muddle_through", "ai_productivity_lag", "orderly_convergence",
              "fragmentation", "disorderly_climate_crystallisation"):
        m = _basis(by_key[("wbc", s)], "engine_current").implied_moat
        assert m.status == "finite" and 15 < 5 + m.extension_years < 42, (s, m)


def test_wbc_stagflation_recovery_shows_up_on_the_new_axis(by_key):
    """Finding 2. M14, restated: the terminal sits on the far side of book equity from
    where the earned return points, i.e. it assumes a recovery the forecast does not show."""
    v = by_key[("wbc", "stagflation_persists")]
    assert v.earned_return < v.cost_of_capital
    assert _basis(v, "engine_current").implied_moat.status == "other_side"


def test_simple_tv_inherits_whatever_the_final_year_happens_to_be(by_key):
    """Finding 3. Where the forecast ends mid-glide, capitalising the final year's cash
    flow is a large call on one year. DNL Disorderly Climate: about 55% of the engine TV
    (was under half pre-D-35/D-36; the longer horizon and the fade both narrow the gap,
    but simple TV still meaningfully understates the component-built terminal)."""
    v = by_key[("dnl", "disorderly_climate_crystallisation")]
    assert _basis(v, "simple").terminal_value < 0.6 * _basis(v, "engine_current").terminal_value


def test_simple_tv_is_a_claim_about_returns_on_new_capital(by_key):
    """Finding 4. On DNL Muddle Through, simple TV implies a return on new capital
    above what the business earns on its existing capital -- a disclosure, not a veto."""
    v = by_key[("dnl", "muddle_through")]
    b = _basis(v, "simple")
    assert b.implied_return_on_new_capital > v.earned_return + 0.02


def test_moat_length_matters_less_than_whether_it_ends(by_key):
    """Finding 5. DNL Muddle Through: moving the moat from 5 to 15 years is worth less
    than moving it from 15 years to forever. Finite-or-indefinite is the big call."""
    v = by_key[("dnl", "muddle_through")]
    tv = {n: _basis(v, f"two_stage_plus_{n}").terminal_value for n in EXTENSION_GRID}
    perpetual = _basis(v, "two_stage_perpetual").terminal_value
    assert tv[10] - tv[0] < perpetual - tv[10]
    assert tv[0] == pytest.approx(v.capital)


def test_exit_multiples_assert_returns_far_above_what_is_earned(by_key):
    """Finding 6. Eight times forward EBITDA on DNL Muddle Through needs a perpetual
    return on all capital about four points above the earned return."""
    v = by_key[("dnl", "muddle_through")]
    b = _basis(v, "exit_8x_ebitda")
    assert b.implied_moat.status == "perpetual_or_more"
    assert b.implied_perpetual_return > v.earned_return + 0.03


def test_the_market_price_needs_a_return_the_forecast_does_not_show(by_key):
    """Finding 7. At the reference price, DNL's terminal must carry a perpetual return
    on all capital near 21 per cent against 12.7 earned -- or the forecast is light.
    (18.5 against 11.4 before D-71's ten-year horizon moved the capital base and
    the earned return; the gap to the market is the finding, and it widened.)"""
    v = by_key[("dnl", "muddle_through")]
    b = _basis(v, "market_implied")
    assert b.value_per_share == pytest.approx(3.61, abs=1e-9)
    assert 0.20 < b.implied_perpetual_return < 0.22


def test_csl_capital_base_is_built_and_on_the_axis(rows):
    """Build order item 2, 24 Sep 2026: CSL gained an invested-capital build.

    Superseded ``test_csl_cannot_be_placed_on_the_axis_until_its_capital_base_is_built``
    -- that test was asserted so the day this changed would be a conscious event, and
    this is that day. The FY25 opening stock (net PP&E 9,797 + intangibles ex-goodwill
    8,120, D-53) rolled forward through the explicit period via the segment engine's
    own capex/D&A/working-capital arrays (D-51: no separate reimplementation).
    """
    for v in (x for x in rows if x.company_id == "csl"):
        assert v.capital is not None
        assert 20_000 < v.capital < 26_000, (
            "CSL's rolled-forward capital should sit near the FY25 opening stock "
            "(~17.9bn) plus five years of net reinvestment, not a different order "
            "of magnitude")
        assert v.earned_return is not None
        # CSL earns well above its cost of equity on the corrected capital base --
        # a capital-light franchise, not the D-53 defect (61-73% return on NEW
        # capital, which this does not measure or repeat).
        assert v.earned_return > v.cost_of_capital
        assert any(b.name.startswith("two_stage") for b in v.bases)
