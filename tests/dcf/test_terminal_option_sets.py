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
    LOWER the value: DNL Muddle Through, ten-year moat, 16% gives about 3,728."""
    v = by_key[("dnl", "muddle_through")]
    e1 = v.capital * v.earned_return
    n = 5  # ten years from valuation, five beyond the forecast
    measured = two_stage(v.capital, v.earned_return, v.cost_of_capital, v.terminal_growth, n)
    backwards = two_stage(e1 / 0.16, 0.16, v.cost_of_capital, v.terminal_growth, n)
    assert measured == pytest.approx(4467, abs=1)
    assert backwards == pytest.approx(3728, abs=1)
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
    pinned = {("dnl", "muddle_through"): 1.9895, ("wbc", "muddle_through"): 30.0304,
              ("csl", "muddle_through"): 195.7835}
    for key, vps in pinned.items():
        v = next(x for x in rows if (x.company_id, x.scenario_id) == key)
        assert _basis(v, "engine_current").value_per_share == pytest.approx(vps, abs=1e-4)


# ------------------------------------------------------------ findings
def test_the_current_terminal_already_assumes_a_moat_nobody_chose(by_key):
    """Finding 1. DNL's component-built terminal implies a moat of 66 to 72 years on its
    three above-WACC scenarios; WBC's declared terminal ROEs imply 22 to 42 years."""
    for s in ("muddle_through", "ai_productivity_lag", "orderly_convergence"):
        m = _basis(by_key[("dnl", s)], "engine_current").implied_moat
        assert m.status == "finite" and 60 < 5 + m.extension_years < 80, (s, m)
    for s in ("muddle_through", "ai_productivity_lag", "orderly_convergence",
              "fragmentation", "disorderly_climate_crystallisation"):
        m = _basis(by_key[("wbc", s)], "engine_current").implied_moat
        assert m.status == "finite" and 20 < 5 + m.extension_years < 45, (s, m)


def test_wbc_stagflation_recovery_shows_up_on_the_new_axis(by_key):
    """Finding 2. M14, restated: the terminal sits on the far side of book equity from
    where the earned return points, i.e. it assumes a recovery the forecast does not show."""
    v = by_key[("wbc", "stagflation_persists")]
    assert v.earned_return < v.cost_of_capital
    assert _basis(v, "engine_current").implied_moat.status == "other_side"


def test_simple_tv_inherits_whatever_the_final_year_happens_to_be(by_key):
    """Finding 3. Where the forecast ends mid-glide, capitalising the final year's cash
    flow is a large call on one year. DNL Disorderly Climate: under half the engine TV."""
    v = by_key[("dnl", "disorderly_climate_crystallisation")]
    assert _basis(v, "simple").terminal_value < 0.5 * _basis(v, "engine_current").terminal_value


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
    on all capital near 18.5 per cent against 11.4 earned -- or the forecast is light."""
    v = by_key[("dnl", "muddle_through")]
    b = _basis(v, "market_implied")
    assert b.value_per_share == pytest.approx(3.61, abs=1e-9)
    assert 0.17 < b.implied_perpetual_return < 0.20


def test_csl_cannot_be_placed_on_the_axis_until_its_capital_base_is_built(rows):
    """Asserted so that the day CSL gains an invested-capital build, this test says so."""
    for v in (x for x in rows if x.company_id == "csl"):
        assert v.capital is None
        assert not any(b.name.startswith("two_stage") for b in v.bases)
