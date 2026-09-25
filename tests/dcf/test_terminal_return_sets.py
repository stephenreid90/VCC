"""The terminal-return set is regenerable, and its headline findings are pinned.

D-42 (PROPOSED) and M14. The committed set in
``design/methodology/terminal_return_sets.yaml`` is the published table; this test
is the ``asserted_by`` half of the standing-rule-4 contract — regenerate from the
production engines and the committed figures must come back.

The three findings pinned below are the reason the diagnostic was worth building,
and each is pinned loosely enough to survive a data refresh but tightly enough to
fail if the underlying assumption changes.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from size_terminal_returns import as_set, collect  # noqa: E402

SET_PATH = ROOT / "design" / "methodology" / "terminal_return_sets.yaml"


@pytest.fixture(scope="module")
def rows():
    return collect()


@pytest.fixture(scope="module")
def committed():
    return yaml.safe_load(SET_PATH.read_text(encoding="utf-8"))


def test_the_committed_set_regenerates(rows, committed):
    """Standing rule 4: the published table comes back from the engines."""
    assert as_set(rows) == committed, (
        "design/methodology/terminal_return_sets.yaml is stale — "
        "run scripts/size_terminal_returns.py"
    )


def test_every_valuation_is_covered(rows):
    scenarios = sorted(p.stem for p in (ROOT / "data" / "scenarios").glob("*.yaml"))
    assert len(rows) == 3 * len(scenarios)
    assert {r.company_id for r in rows} == {"dnl", "wbc", "csl"}


# ------------------------------------------------------- finding 1: CSL / D-53
def test_csl_terminal_asserts_an_implausible_return_on_new_capital(rows):
    """D-53, quantified. This is the number that ruling was missing.

    CSL declares ``terminal_capex_pct_revenue`` equal to ``da_pct_revenue``, so net
    capex in the terminal is exactly zero and the only reinvestment left is
    working capital at g x intensity. A perpetuity that grows while reinvesting
    about four per cent of its earnings is asserting a return on new capital in
    the high sixties, against a discount rate under nine per cent. That is not a
    moat, it is the arithmetic of ``capex_rule: equals_da`` — which is precisely
    what D-49 retired as a house rule and D-53 ruled must apply to CSL as well.

    Pinned as a band rather than a point: the finding is the order of magnitude,
    and implementing D-53 should drop it into the range DNL now occupies.
    """
    csl = [r for r in rows if r.company_id == "csl"]
    assert len(csl) == 6

    for r in csl:
        assert r.reinvestment_rate < 0.06, (r.scenario_id, r.reinvestment_rate)
        assert 0.55 < r.return_on_new_capital < 0.80, (r.scenario_id, r.return_on_new_capital)
        assert r.excess_over_cost_of_capital > 0.45, r.scenario_id
        assert any("exceeds" in w for w in r.warnings)


# ------------------------------------------------------- finding 2: WBC / M14
def test_wbc_stagflation_terminal_roe_is_a_recovery_assumption(rows):
    """M14. The one scenario where the declared rate sits above what is earned.

    On five of six the declared terminal ROE is conservative against the ROE the
    final explicit year earns. Stagflation is the exception and it is a large one,
    on the scenario whose terminal is the biggest share of value in the project.
    """
    wbc = {r.scenario_id: r for r in rows if r.company_id == "wbc"}
    stag = wbc["stagflation_persists"]

    assert stag.step_from_earned == pytest.approx(0.0401, abs=0.002)
    assert stag.earned_final_explicit == pytest.approx(0.0499, abs=0.002)
    assert any("recovery assumption" in w for w in stag.warnings)

    # Every other scenario is conservative or flat, which is what makes the
    # Stagflation case a finding rather than a systemic bias.
    for scenario, r in wbc.items():
        if scenario == "stagflation_persists":
            continue
        assert r.step_from_earned <= 0.01, (scenario, r.step_from_earned)
        assert not any("recovery assumption" in w for w in r.warnings), scenario


# ------------------------------------------------------- finding 3: DNL / D-42
def test_dnl_splits_on_the_cost_of_capital_which_is_what_d42_is_for(rows):
    """Three DNL scenarios assert an excess return and three do not.

    This is the diagnostic behaving as D-42 intends: the terminal return is not
    uniformly above or below the discount rate, so the warning discriminates
    rather than firing on everything. The three that exceed it are the ones that
    owe a §10.6-compliant defended exception.
    """
    dnl = {r.scenario_id: r for r in rows if r.company_id == "dnl"}
    above = {s for s, r in dnl.items() if r.excess_over_cost_of_capital > 0}
    below = set(dnl) - above

    assert above == {"muddle_through", "ai_productivity_lag", "orderly_convergence"}, above
    assert below == {"fragmentation", "disorderly_climate_crystallisation",
                     "stagflation_persists"}, below
    for s in above:
        assert any("D-42" in w for w in dnl[s].warnings)
    for s in below:
        assert not any("exceeds" in w for w in dnl[s].warnings), s


def test_the_two_readings_no_longer_disagree_about_fragmentation(rows):
    """Which reading governs is a substantive choice, not a rounding preference --
    and as of 25 Sep 2026 (D-35/D-36) the two readings have stopped disagreeing
    anywhere in DNL, Fragmentation included.

    Before the horizon extended and revenue growth started fading to g,
    Fragmentation sat BELOW its WACC on the return on new capital and ABOVE it
    on the whole capital base: under the weaker reading it owed no defended
    exception and under the better one it did. The longer horizon and the fade
    both smooth the gap between the two readings, and Fragmentation now sits
    (slightly) below WACC on BOTH. Documented rather than silently dropped,
    because a silent change of reading would silently change who owes a
    defence -- this asserts the new state explicitly so the next change to
    disagree is caught rather than assumed away.
    """
    frag = next(r for r in rows if r.company_id == "dnl"
                and r.scenario_id == "fragmentation")
    assert frag.excess_over_cost_of_capital < 0, frag.excess_over_cost_of_capital
    assert frag.excess_on_governing_return < 0, frag.excess_on_governing_return
    assert frag.governing_return == frag.return_on_whole_capital
    # No DNL scenario disagrees between the two readings any more (all six agree
    # in sign); revisit this test the day one does.
    dnl_rows = [r for r in rows if r.company_id == "dnl"]
    assert all(
        (r.excess_over_cost_of_capital > 0) == (r.excess_on_governing_return > 0)
        for r in dnl_rows
    ), [r.scenario_id for r in dnl_rows]


def test_the_declared_rate_does_not_reconcile_with_the_capital_build(rows):
    """The D-42 step 2 finding: D-45 and D-49 disagree, and by how much.

    Orderly Convergence is the only valuation in the project that declares a
    terminal return. The rate comes from its own declared movement — positive,
    small, which the project's translation table maps to +25bp on the
    convergence target — so it is the moat work's view rather than an invention.
    The capital build produces something far above it. Both cannot be right.
    """
    oc = next(r for r in rows if r.company_id == "dnl"
              and r.scenario_id == "orderly_convergence")
    assert oc.declared_return == pytest.approx(0.0913, abs=1e-6)
    # Re-pinned 25 Sep 2026 for D-35/D-36 (was 0.1246 / -0.0333): the longer
    # horizon and the growth fade both lower the return the capital build
    # produces, narrowing but not closing the gap against the declared rate.
    assert oc.return_on_whole_capital == pytest.approx(0.1193, abs=5e-4)
    assert oc.declared_versus_whole_capital == pytest.approx(-0.0280, abs=5e-4)
    assert any("declares a terminal return" in w for w in oc.warnings)


def test_only_dnl_reports_a_return_on_the_whole_capital_base(rows):
    """Because only DNL declares the capex rule that rolls a base forward.

    WBC has no invested-capital construction at all and CSL still runs
    capex = D&A (D-53, unimplemented), so neither can report the better reading.
    Asserted so that when CSL gains one, this test says so.
    """
    have = {r.company_id for r in rows if r.return_on_whole_capital is not None}
    assert have == {"dnl"}, have


def test_the_bank_reports_its_declared_rate_not_an_inverted_one(rows):
    """The bank terminal declares the return; the identity derives retention.

    Worth asserting because reporting an inverted return for the bank would be
    wrong in a way that looks right: the justified price-to-book form fixes ROE
    and solves for the payout, so inverting it would just return the input.
    """
    for r in (r for r in rows if r.company_id == "wbc"):
        assert r.construction == "bank_roe"
        assert r.reinvestment_rate == pytest.approx(
            r.terminal_growth / r.return_on_new_capital, rel=1e-9)
